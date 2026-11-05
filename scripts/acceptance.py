#!/usr/bin/env python3
"""Live acceptance runner for an isolated, empty Compose project.

Run after preflight/build. Existing events make oracle reconciliation fail rather
than being deleted. No prune, volume deletion, or hidden reset occurs here.
"""

import argparse
import base64
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
COMPOSE = ["docker", "compose", "--env-file", ".env", "--env-file", ".env.images"]


def run(arguments, *, expected=0, timeout=240):
    result = subprocess.run(COMPOSE + arguments, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    expected_codes = expected if isinstance(expected, tuple) else (expected,)
    if result.returncode not in expected_codes:
        raise RuntimeError(f"Compose command {arguments[0]} returned {result.returncode}, expected {expected}: {result.stderr[-500:]}")
    return result.stdout


def tools(*arguments, expected=0, env=()):
    command = ["run", "--rm", "-T", "--no-deps"]
    for value in env:
        command.extend(["-e", value])
    output = run(command + ["tools", *arguments], expected=expected)
    if expected:
        return {"expected_exit": expected}
    return json.loads(output.strip().splitlines()[-1])


def fixture(name, *, invalid=False, rejection=False):
    command = ["run", "--rm", "-T", "--no-deps", "--entrypoint", "python", "tools", "scripts/runtime_fixture.py", name]
    if invalid:
        command.append("--invalid")
    if rejection:
        command.append("--index-rejection")
    return json.loads(run(command).strip().splitlines()[-1])


def wait_for(function, *, seconds=120, description="condition"):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        try:
            result = function()
            if result:
                return result
        except (RuntimeError, ValueError, OSError) as exc:
            last = type(exc).__name__
        time.sleep(2)
    raise RuntimeError(f"{description} did not converge in {seconds}s; last error class={last}")


def reconciliation():
    output = run(["run", "--rm", "-T", "--no-deps", "tools", "verify", "--oracle", "/data/corpus/oracle.json", "--state", "/data/worker/quarantine.sqlite", "--output", "-"], expected=(0, 1))
    result = json.loads(output.strip().splitlines()[-1])
    (ARTIFACTS / "last-reconciliation.json").write_text(json.dumps(result, indent=2) + "\n")
    return result if result["passed"] else None


def configuration():
    return dict(line.split("=", 1) for line in (ROOT / ".env").read_text().splitlines() if line and not line.startswith("#") and "=" in line)


def http_json(service, path):
    settings = configuration()
    if service == "rabbitmq":
        port = os.environ.get("POC_RABBITMQ_MANAGEMENT_PORT", "15672")
        url = f"http://127.0.0.1:{port}" + path
        user, password = settings["RABBITMQ_DEFAULT_USER"], settings["RABBITMQ_DEFAULT_PASS"]
        context = None
    else:
        port = os.environ.get("POC_OPENSEARCH_PORT", "9200")
        url = f"https://127.0.0.1:{port}" + path
        user, password = "admin", settings["OPENSEARCH_INITIAL_ADMIN_PASSWORD"]
        context = ssl._create_unverified_context()  # This local test's demo certificate only.
    request = urllib.request.Request(url, headers={"Authorization": "Basic " + base64.b64encode((user + ":" + password).encode()).decode()})
    with urllib.request.urlopen(request, timeout=10, context=context) as response:
        return json.load(response)


def queue():
    return http_json("rabbitmq", "/api/queues/%2F/poc.events.v1")


def pending():
    result = queue()
    return result.get("messages_ready", 0) + result.get("messages_unacknowledged", 0)


def ready():
    result = http_json("opensearch", "/_cluster/health/poc-events-v1?wait_for_status=yellow&timeout=5s")
    return result.get("status") in ("green", "yellow") and not result.get("timed_out")


def fault_worker(point, *, expected=86, rejection_id=None):
    command = ["run", "--rm", "-T", "--no-deps"]
    if point:
        command.extend(["-e", "ALMA_POC_FAILPOINT=" + point])
    if rejection_id:
        command.extend(["-e", "ALMA_POC_REJECT_EVENT_ID=" + rejection_id])
    return run(command + ["worker", "worker", "--state", "/data/worker/quarantine.sqlite", "--once"], expected=expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outage-seconds", type=int, default=60)
    parser.add_argument("--drain-seconds", type=int, default=120)
    args = parser.parse_args()
    if not 1 <= args.outage_seconds <= 60 or not 1 <= args.drain_seconds <= 120:
        raise SystemExit("bounds may be reduced explicitly for a diagnostic run, never silently increased")
    ARTIFACTS.mkdir(exist_ok=True)
    report = {"started_at": datetime.now(timezone.utc).isoformat(), "passed": False, "backend": "RabbitMQ + OpenSearch", "cases": [], "accepted_target_profile": args.outage_seconds == 60 and args.drain_seconds == 120}
    producer = None
    run_id = uuid.uuid4().hex[:12]
    source_container = "alma-poc-source-" + run_id
    try:
        run(["up", "-d", "opensearch", "rabbitmq", "dashboards", "setup", "adapter", "worker"], timeout=360)
        wait_for(ready, seconds=300)
        if http_json("opensearch", "/poc-events-v1/_count")["count"] != 0:
            raise RuntimeError("acceptance needs an empty isolated Compose project; existing events were preserved")
        tools("generate", "--root", "/data/corpus", "--count", "1000")
        report["cases"].append({"case": "baseline", "result": wait_for(reconciliation)})
        for job in (f"acceptance-{run_id}-first", f"acceptance-{run_id}-second"):
            tools("adapter", "--root", "/data/corpus", "--state", "/data/adapter/checkpoints.sqlite", "--once", "--replay", job)
            wait_for(lambda: pending() == 0, description=f"{job}: RabbitMQ queue drain")
            result = wait_for(reconciliation, description=f"{job}: index and quarantine reconciliation")
            report["cases"].append({"case": job, "result": result})
        tools("adapter", "--root", "/data/corpus", "--state", "/data/adapter/checkpoints.sqlite", "--once", "--replay", "crash-confirm-" + run_id, expected=86, env=("ALMA_POC_FAILPOINT=adapter.after_confirm",))
        tools("adapter", "--root", "/data/corpus", "--state", "/data/adapter/checkpoints.sqlite", "--once", "--replay", "crash-confirm-" + run_id)
        wait_for(lambda: pending() == 0)
        report["cases"].append({"case": "adapter-confirm-crash", "exit": 86, "result": wait_for(reconciliation)})
        for point in ("worker.before_index", "worker.after_index", "worker.after_quarantine", "worker.lose_response"):
            run(["stop", "worker"])
            inserted = fixture(point, invalid=point == "worker.after_quarantine")
            wait_for(lambda: pending() > 0)
            fault_worker(point, expected=2 if point == "worker.lose_response" else 86)
            run(["start", "worker"])
            report["cases"].append({"case": point, "fixture": inserted, "result": wait_for(reconciliation)})
        run(["stop", "worker"])
        rejected = fixture("partial-index-rejection", rejection=True)
        accepted = fixture("valid-beside-rejection")
        wait_for(lambda: pending() >= 2)
        fault_worker(None, expected=0, rejection_id=rejected["event_id"])
        run(["start", "worker"])
        report["cases"].append({"case": "partial-index-rejection", "rejected": rejected, "accepted": accepted, "result": wait_for(reconciliation)})
        run(["stop", "worker"])
        inserted = fixture("broker-restart-pending")
        wait_for(lambda: pending() > 0)
        before = pending()
        run(["restart", "rabbitmq"])
        wait_for(lambda: pending() >= before)
        run(["start", "worker"])
        report["cases"].append({"case": "broker-restart-pending", "pending_before_restart": before, "fixture": inserted, "result": wait_for(reconciliation)})
        producer_command = COMPOSE + ["run", "--rm", "-T", "--no-deps", "--name", source_container, "tools", "stream", "--root", "/data/corpus", "--rate", "10", "--seconds", "120", "--oracle", "/data/corpus/oracle.json"]
        producer = subprocess.Popen(producer_command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        run(["stop", "opensearch"])
        stopped = time.monotonic()
        snapshots = []
        while time.monotonic() - stopped < args.outage_seconds:
            if not snapshots or time.monotonic() - snapshots[-1]["monotonic"] >= 10:
                snapshots.append({"monotonic": time.monotonic(), "pending": pending()})
            time.sleep(1)
        if not any(x["pending"] > 0 for x in snapshots):
            raise RuntimeError("no backlog was observed during the outage")
        run(["start", "opensearch"])
        wait_for(ready, seconds=300)
        restored = time.monotonic()
        stdout, stderr = producer.communicate(timeout=180)
        if producer.returncode:
            raise RuntimeError("continuous source did not complete: " + stderr[-300:])
        streamed = json.loads(stdout.strip().splitlines()[-1])
        remaining = args.drain_seconds - (time.monotonic() - restored)
        if remaining <= 0:
            raise RuntimeError("recovery deadline passed before source completion")
        final = wait_for(reconciliation, seconds=remaining)
        if pending() != 0:
            wait_for(lambda: pending() == 0, seconds=max(1, args.drain_seconds - (time.monotonic() - restored)))
        report["cases"].append({"case": "continuous-outage-recovery", "observed_unavailable_seconds": restored - stopped, "source": streamed, "backlog_samples": snapshots, "convergence_after_restoration_seconds": time.monotonic() - restored, "result": final})
        report["queries"] = tools("queries", "--output", "-")
        analysis = tools("analyze", "--oracle", "/data/corpus/oracle.json", "--output", "-")
        if not any(x["recurring"] for x in analysis["result"]["patterns"]["groups"]):
            raise RuntimeError("no recurring pattern found")
        (ARTIFACTS / "analysis.json").write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n")
        report["analysis_summary"] = {"events": analysis["result"]["event_count"], "groups": len(analysis["result"]["patterns"]["groups"])}
        subprocess.run([sys.executable, "scripts/check_budget.py"], cwd=ROOT, check=True, timeout=30)
        report["passed"] = True
    except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
    finally:
        if producer is not None and producer.poll() is None:
            try:
                subprocess.run(["docker", "stop", source_container], capture_output=True, timeout=30)
                producer.communicate(timeout=30)
            except (OSError, subprocess.SubprocessError):
                report["source_cleanup"] = "incomplete; inspect container " + source_container
        # Return a stopped search node to service after a failed outage test.
        try:
            run(["start", "opensearch", "rabbitmq", "worker"], timeout=30)
            logs = run(["logs", "--no-color", "--tail", "100"], timeout=30)
            for key, value in configuration().items():
                if ("PASS" in key or "PASSWORD" in key) and value:
                    logs = logs.replace(value, "[REDACTED]")
            (ARTIFACTS / "container-logs.txt").write_text(logs)
        except Exception:
            report["log_collection"] = "unavailable"
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        (ARTIFACTS / "acceptance.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"passed": report["passed"], "report": "artifacts/acceptance.json", "error": report.get("error")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

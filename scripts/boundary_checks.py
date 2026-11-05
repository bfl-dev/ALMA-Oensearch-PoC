#!/usr/bin/env python3
"""Run isolated M1 boundary checks and retain their reports and volumes."""

import json
import os
import platform
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_MEMORY = int(5.125 * 1024**3)


def run(command, *, env=None, timeout=60, check=True):
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                            text=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f"{command[0]} {command[1]} failed: {result.stderr[-500:]}")
    return result


def redact(text):
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                if "PASS" in key and value:
                    text = text.replace(value, "[REDACTED]")
    return text


def main():
    run_id = str(uuid.uuid4())
    project = "alma-boundary-" + run_id[:12]
    destination = ROOT / "artifacts/boundaries" / run_id
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination / "report.json"
    report = {"passed": False, "project": project, "run_id": run_id,
              "started_at": datetime.now(timezone.utc).isoformat(),
              "host": platform.platform(), "cases": {}}
    # Automatic loopback ports keep a retained demo's bindings out of the test.
    env = {**os.environ, "POC_OPENSEARCH_PORT": "0", "POC_RABBITMQ_PORT": "0",
           "POC_RABBITMQ_MANAGEMENT_PORT": "0"}
    compose = ["docker", "compose", "-f", str(ROOT / "compose.yaml"),
               "--env-file", str(ROOT / ".env"), "--env-file", str(ROOT / ".env.images"),
               "-p", project]
    started = False
    try:
        memory = dict(line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
        available = int(memory["MemAvailable"].strip().split()[0]) * 1024
        report.update(available_memory_bytes=available, required_memory_bytes=REQUIRED_MEMORY)
        if available < REQUIRED_MEMORY:
            raise RuntimeError("boundary stack requires 5.125 GiB available RAM; stop the current demo stack and retry")
        revision = run(["git", "rev-parse", "HEAD"]).stdout.strip()
        report.update(source_revision=revision,
                      checkout_dirty=bool(run(["git", "status", "--porcelain"]).stdout.strip()),
                      compose_version=run(["docker", "compose", "version"]).stdout.strip())
        image_keys = {"OPENSEARCH_IMAGE", "RABBITMQ_IMAGE", "PYTHON_IMAGE", "SOURCE_REVISION"}
        report["configured_images"] = {}
        for line in (ROOT / ".env.images").read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                if key in image_keys:
                    report["configured_images"][key] = value
        budget = run([sys.executable, "scripts/check_budget.py", "--output",
                      str(destination / "budget-before.json")])
        report["budget_before"] = json.loads(budget.stdout)
        started = True
        run(compose + ["up", "-d", "--wait", "--wait-timeout", "300", "--pull", "never",
                       "opensearch", "rabbitmq"], env=env, timeout=360)
        result = run(
            compose + ["run", "--rm", "-T", "--no-deps", "--pull", "never",
                       "--entrypoint", "python",
                       "-e", "BOUNDARY_RUN_ID=" + run_id,
                       "-e", "BOUNDARY_PROJECT=" + project,
                       "-e", "BOUNDARY_EXPECTED_REVISION=" + revision,
                       "tools", "scripts/boundary_fixture.py"],
            env=env, timeout=180, check=False)
        (destination / "fixture-stderr.txt").write_text(redact(result.stderr))
        if not result.stdout.strip():
            raise RuntimeError("boundary image produced no report; inspect fixture-stderr.txt and rebuild the image")
        fixture = json.loads(result.stdout.strip().splitlines()[-1])
        (destination / "fixture.json").write_text(json.dumps(fixture, indent=2) + "\n")
        report["fixture"] = fixture
        report["cases"] = fixture.get("cases", {})
        required_cases = {"identity_collision", "broker_capacity", "quarantine_capacity"}
        report["passed"] = (result.returncode == 0 and fixture.get("passed") is True
                            and set(report["cases"]) == required_cases
                            and all(case.get("passed") is True for case in report["cases"].values()))
        if not report["passed"]:
            report["error"] = fixture.get("error", "boundary fixture failed")
    except Exception as exc:
        report.update(error=redact(str(exc)), error_type=type(exc).__name__)
    finally:
        if started:
            try:
                logs = run(compose + ["logs", "--no-color", "--tail", "100"], env=env, timeout=30)
                (destination / "container-logs.txt").write_text(redact(logs.stdout))
            except Exception:
                report["log_collection"] = "unavailable"
            try:
                run(compose + ["down"], env=env, timeout=60)
                report["containers_stopped_volumes_retained"] = True
            except Exception as exc:
                report.update(passed=False, cleanup_error=redact(str(exc)))
            try:
                budget = run([sys.executable, "scripts/check_budget.py", "--output",
                              str(destination / "budget-after.json")])
                report["budget_after"] = json.loads(budget.stdout)
            except Exception as exc:
                report.update(passed=False, budget_error=redact(str(exc)))
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"passed": report["passed"], "report": str(report_path.relative_to(ROOT)),
                      "project": project, "error": report.get("error"),
                      "cleanup_error": report.get("cleanup_error"),
                      "budget_error": report.get("budget_error")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

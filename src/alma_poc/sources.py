"""Explicitly synthetic ONLINE/OFFLINE sources and an independent fixture oracle."""

import fcntl
import hashlib
import json
import random
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from .capture import Capture, atomic_json, read_records
from .errors import CapacityError, SystemFailure
from .model import utc_now, wire_json
from .scenarios import mixed_events

BASE_TIME = datetime(2026, 11, 3, tzinfo=timezone.utc)


def xml_record(message, *, timestamp, severity="Info", operation="op-17", request="req-17", stack="stack-17", component="mock.receiver"):
    # Escaping is deterministic and safely supports arbitrary XML message text.
    return (f'<{severity} TimeStamp={quoteattr(timestamp)} SourceObject={quoteattr(component)} Process="mock-acs" StackId={quoteattr(stack)}>'
            f'{escape(message)}<Data Name="OperationId">{escape(operation)}</Data><Data Name="RequestId">{escape(request)}</Data></{severity}>\n').encode()


def fixture(family, sequence, count):
    """Return independently described raw input and expected payload/disposition."""
    if sequence > count:
        raw = b'<Error TimeStamp="2026-11-03T00:00:00.000">unfinished\n' if family == "ONLINE" else b'{"timestamp":17,"severity":"ERROR","message":"missing component"}\n'
        return raw, {"disposition": "quarantined", "error_code": "E_XML_PARSE" if family == "ONLINE" else "E_PAYLOAD_PROFILE"}
    offset = sequence * 100
    operation, request, severity, message = f"sample-{sequence}", f"sample-request-{sequence}", "INFO", f"receiver sample {sequence}"
    if family == "ONLINE":
        scenarios = {
            1: (0, "op-17", "INFO", "action started"),
            2: (1000, "op-17", "ERROR", "receiver timeout after 10 ms — señal débil"),
            3: (1000, "op-17", "ERROR", "receiver timeout after 10 ms — señal débil"),
            4: (3000, "op-17", "NOTICE", "connection restored"),
            5: (500, "op-17", "INFO", "late diagnostic"),
            6: (1000, "op-18", "ERROR", "unrelated operation"),
        }
        if sequence in scenarios:
            offset, operation, severity, message = scenarios[sequence]
            request = "req-17" if operation == "op-17" else "req-18"
    else:
        if sequence == 1:
            offset, operation, request, message = -1000, "op-17", "req-17", "request accepted"
        elif sequence == 2:
            offset, operation, request, message = 4000, "op-17", "req-17", "request completed"
        elif sequence == 3:
            offset, operation, request, message = 1000, "op-18", "req-18", "unrelated request"
    stamp = (BASE_TIME + timedelta(milliseconds=offset)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    if family == "ONLINE":
        raw = xml_record(message, timestamp=stamp[:-1], severity=severity.title(), operation=operation, request=request, stack="stack-17" if operation == "op-17" else f"stack-{sequence}")
    else:
        raw = wire_json({"timestamp": stamp, "severity": severity, "component": "mock.api", "message": message, "operation_id": operation, "request_id": request, "data": []}) + b"\n"
    return raw, {"disposition": "indexed", "error_code": None, "event_time": stamp, "severity": severity, "component": "mock.receiver" if family == "ONLINE" else "mock.api", "message": message}


def generate_corpus(root, count=1000, invalid=1):
    if count < 6 or count > 10000 or invalid not in (0, 1):
        raise ValueError("use 6..10000 valid records per family and zero/one invalid fixture")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    oracle_path = root / "oracle.json"
    if oracle_path.exists():
        oracle = json.loads(oracle_path.read_text())
        if oracle["valid_per_family"] != count or oracle["invalid_per_family"] != invalid:
            raise SystemFailure("existing corpus settings differ; use a new directory")
    else:
        if any(root.iterdir()):
            raise SystemFailure("corpus directory is not empty and has no oracle")
        generations = {family: str(uuid.uuid4()) for family in ("ONLINE", "OFFLINE")}
        occurrences = []
        for family in ("ONLINE", "OFFLINE"):
            for sequence in range(1, count + invalid + 1):
                raw, expected = fixture(family, sequence, count)
                # Deliberately do not call the production event_id/normalizer.
                occurrences.append({"event_id": f"urn:alma-poc:event:v1:{generations[family]}:{sequence}", "family": family, "generation_id": generations[family], "sequence": sequence, "raw_sha256": hashlib.sha256(raw).hexdigest(), **expected})
        oracle = {"version": "1.0.0", "synthetic": True, "valid_per_family": count, "invalid_per_family": invalid, "generations": generations, "occurrences": occurrences, "seed_id": f"urn:alma-poc:event:v1:{generations['ONLINE']}:2", "negative_id": f"urn:alma-poc:event:v1:{generations['ONLINE']}:6"}
        atomic_json(oracle_path, oracle)
    expected_by_id = {x["event_id"]: x for x in oracle["occurrences"]}
    for family in ("ONLINE", "OFFLINE"):
        path = root / family.lower()
        if (path / "manifest.json").exists():
            for record in read_records(path):
                expected = expected_by_id.get(record.envelope["event_id"])
                if expected is None or record.envelope["raw"]["sha256"] != expected["raw_sha256"]:
                    raise SystemFailure("existing corpus differs from independent oracle")
            manifest = json.loads((path / "manifest.json").read_text())
            if manifest["sealed"]:
                if sum(1 for _ in read_records(path)) != count + invalid:
                    raise SystemFailure("sealed corpus is incomplete")
                continue
        with Capture(path, family, "mock-acs" if family == "ONLINE" else "mock-api", generation_id=oracle["generations"][family], budget_root=root) as capture:
            for sequence in range(capture.sequence + 1, count + invalid + 1):
                raw, _ = fixture(family, sequence, count)
                capture.append(raw)
            capture.seal()
    return {"oracle": str(oracle_path), "valid": count * 2, "quarantined_expected": invalid * 2, "seed_id": oracle["seed_id"]}


def stream(root, rate=10, seconds=120, family="both", oracle_path=None, *,
           scenario="normal", incident_rate=0.1, seed=None):
    if not 0 < rate <= 1000 or not 0 < seconds <= 3600 or not 1 <= int(rate * seconds) <= 20000:
        raise ValueError("rate/seconds exceed bounded source settings")
    if family not in ("ONLINE", "OFFLINE", "both") or scenario not in ("normal", "mixed"):
        raise ValueError("unsupported source family or scenario")
    if not 0 <= incident_rate <= 1 or seed is not None and type(seed) is not int:
        raise ValueError("incident rate must be 0..1 and seed must be an integer")
    if scenario == "mixed" and (family != "both" or rate < 0.1):
        raise ValueError("mixed scenarios require both families and at least 0.1 events/s")
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    families = ("ONLINE", "OFFLINE") if family == "both" else (family,)
    job = str(uuid.uuid4())
    generations = {f: str(uuid.uuid4()) for f in families}
    first_time = datetime.now(timezone.utc)
    events, incidents = [], []
    if scenario == "mixed":
        if seed is None:
            seed = random.SystemRandom().getrandbits(64)
        events, incidents = mixed_events(int(rate * seconds), job, random.Random(seed), incident_rate)
    plan, sequences = [], {f: 0 for f in families}
    for number in range(int(rate * seconds)):
        current = families[number % len(families)]
        stamp = (first_time + timedelta(seconds=number / rate)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        operation, request, message = f"live-{job}-{number}", f"request-{job}-{number}", f"live sample {number}"
        component = "mock.receiver" if current == "ONLINE" else "mock.api"
        severity, stack = "INFO", f"stack-{job}-{number}"
        if events:
            event = events[number]
            current, component, severity = event["family"], event["component"], event["severity"]
            operation, request, message = event["operation_id"], event["request_id"], event["message"]
            stack = event["stack_id"]
        sequences[current] += 1
        if current == "ONLINE":
            raw = xml_record(message, timestamp=stamp[:-1], severity=severity.title(),
                             operation=operation, request=request, stack=stack, component=component)
        else:
            raw = wire_json({"timestamp": stamp, "severity": severity, "component": component, "message": message, "operation_id": operation, "request_id": request})
        expected = {"event_id": f"urn:alma-poc:event:v1:{generations[current]}:{sequences[current]}", "family": current, "generation_id": generations[current], "sequence": sequences[current], "raw_sha256": hashlib.sha256(raw).hexdigest(), "disposition": "indexed", "error_code": None, "event_time": stamp, "severity": severity, "component": component, "message": message}
        plan.append((current, raw, expected))
    for incident in incidents:
        start = incident.pop("start_offset")
        incident["event_ids"] = [item[2]["event_id"] for item in plan[start:start + incident["event_count"]]]
        incident["seed_id"] = incident["event_ids"][1]
    metadata = {"job": job, "generations": generations, "requested_rate": rate,
                "requested_seconds": seconds, "intended_occurrences": len(plan),
                "clock": "synthetic scheduled UTC", "scenario": scenario,
                "incident_rate": incident_rate, "seed": seed, "incidents": incidents}
    if oracle_path:
        with (Path(oracle_path).parent / ".oracle.lock").open("a+b") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            oracle = json.loads(Path(oracle_path).read_text())
            oracle["occurrences"].extend(item[2] for item in plan)
            oracle.setdefault("streams", []).append(metadata)
            atomic_json(oracle_path, oracle)
    if scenario == "mixed":
        print(json.dumps({"phase": "stream_plan", "job": job, "synthetic": True,
                          "scenario": scenario, "seed": seed,
                          "requested_rate": rate, "requested_seconds": seconds,
                          "incidents": len(incidents), "incident_examples": incidents[:5]}), flush=True)
    captures = {}
    started = time.monotonic()
    try:
        for current in families:
            captures[current] = Capture(root / f"live-{job}-{current.lower()}", current, "mock-acs" if current == "ONLINE" else "mock-api", generation_id=generations[current], budget_root=root)
        for number, (current, raw, _) in enumerate(plan):
            remaining = started + number / rate - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            captures[current].append(raw)
        remaining = started + seconds - time.monotonic()
        if remaining > 0:
            time.sleep(remaining)
        for capture in captures.values():
            capture.seal()
    finally:
        for capture in captures.values():
            capture.close()
    return {"captured": len(plan), "job": job, "synthetic": True,
            "elapsed_seconds": time.monotonic() - started, "requested_rate": rate,
            "scenario": scenario, "seed": seed,
            "incidents": len(incidents), "incident_examples": incidents[:5]}


def serve_api(root, host="0.0.0.0", port=8080):
    root = Path(root)
    capture = Capture(root / "api-offline", "OFFLINE", "mock-api", budget_root=root)
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, payload):
            body = wire_json(payload)
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self.respond(200 if self.path == "/healthz" else 404, {"synthetic": True, "service": "offline-api"})

        def do_POST(self):
            if self.path != "/operations":
                return self.respond(404, {"error": "not found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 <= size <= 4096:
                    raise ValueError("request exceeds bound")
                value = json.loads(self.rfile.read(size) or b"{}")
                if not isinstance(value, dict) or value.keys() - {"operation_id", "request_id", "fail"}:
                    raise ValueError("invalid request fields")
                operation = value.get("operation_id", str(uuid.uuid4()))
                request = value.get("request_id", str(uuid.uuid4()))
                if any(not isinstance(x, str) or not 1 <= len(x) <= 128 for x in (operation, request)) or type(value.get("fail", False)) is not bool:
                    raise ValueError("invalid request values")
                raw = wire_json({"timestamp": utc_now(), "severity": "ERROR" if value.get("fail") else "INFO", "component": "mock.api", "message": "operation failed" if value.get("fail") else "operation accepted", "request_id": request, "operation_id": operation})
                with lock:
                    envelope = capture.append(raw)
                self.respond(500 if value.get("fail") else 202, {"event_id": envelope["event_id"], "operation_id": operation, "accepted_to_capture": True, "operation_failed": value.get("fail", False), "synthetic": True})
            except (ValueError, json.JSONDecodeError):
                self.respond(400, {"error": "invalid bounded JSON operation"})
            except CapacityError:
                self.respond(503, {"error": "capture capacity reached; operation not accepted"})

        def log_message(self, *_):
            pass  # No request bodies, credentials or ambient HTTP traffic in source logs.

    try:
        ThreadingHTTPServer((host, port), Handler).serve_forever()
    finally:
        capture.close()

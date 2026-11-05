"""Independent oracle reconciliation; correct totals alone cannot hide a loss."""

import base64
import hashlib
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path

from .capture import read_records
from .model import INDEX, utc_now


def reconcile(documents, oracle, quarantine, captures=None):
    expected = {x["event_id"]: x for x in oracle["occurrences"]}
    wanted = {key for key, value in expected.items() if value["disposition"] == "indexed"}
    bad = {key for key, value in expected.items() if value["disposition"] == "quarantined"}
    counts = Counter(x["event_id"] for x in documents)
    found = set(counts)
    entries = quarantine["entries"]
    qcounts = Counter(x["event_id"] for x in entries if x["materialization"] == INDEX)
    qfound = set(qcounts)
    wrong = []
    for document in documents:
        identifier = document["event_id"]
        if identifier not in wanted:
            continue
        record = expected[identifier]
        try:
            digest = hashlib.sha256(base64.b64decode(document["raw"]["data"], validate=True)).hexdigest()
            content_ok = all(document[field] == record[field] for field in ("severity", "component", "message"))
            content_ok = content_ok and document["raw"]["sha256"] == digest == record["raw_sha256"] and document["event_time"]["utc"] == record["event_time"]
            content_ok = content_ok and document["source"]["generation_id"] == record["generation_id"] and document["source"]["sequence"] == record["sequence"] and document["source"]["family"] == record["family"]
            if captures is not None:
                original = captures[identifier]
                content_ok = content_ok and document["raw"] == original["raw"] and document["source"] == original["source"] and document["ingested_at"] == original["captured_at"]
            if not content_ok:
                wrong.append(identifier)
        except (KeyError, ValueError, TypeError):
            wrong.append(identifier)
    wrong_quarantine = []
    for entry in entries:
        identifier = entry["event_id"]
        if identifier not in bad:
            continue
        envelope = entry["envelope"]
        try:
            digest = hashlib.sha256(base64.b64decode(envelope["raw"]["data"], validate=True)).hexdigest()
            if entry["code"] != expected[identifier]["error_code"] or digest != envelope["raw"]["sha256"] or digest != expected[identifier]["raw_sha256"] or captures is not None and envelope != captures[identifier]:
                wrong_quarantine.append(identifier)
        except (KeyError, ValueError, TypeError):
            wrong_quarantine.append(identifier)
    errors = {
        "missing_indexed": sorted(wanted - found), "extra_indexed": sorted(found - wanted),
        "duplicate_indexed": sorted(key for key, value in counts.items() if value != 1),
        "missing_quarantine": sorted(bad - qfound), "extra_quarantine": sorted(qfound - bad),
        "duplicate_quarantine": sorted(key for key, value in qcounts.items() if value != 1),
        "wrong_indexed_content": sorted(set(wrong)), "wrong_quarantine_content": sorted(set(wrong_quarantine)),
    }
    if captures is not None:
        errors["unproduced_expected"] = sorted(set(expected) - captures.keys())
        errors["missing_accepted_valid"] = sorted(wanted.intersection(captures) - found)
    return {"passed": not any(errors.values()), "materialization": INDEX, "expected_source_occurrences": len(expected), "indexed": len(documents), "quarantined": len(entries), "transport_diagnostics": len(quarantine["diagnostics"]), "indexed_by_family": dict(Counter(x["source"]["family"] for x in documents)), "errors": errors}


def verify_live(sink, oracle_path, state):
    oracle_path = Path(oracle_path)
    oracle = json.loads(oracle_path.read_text())
    captures = {}
    for manifest in oracle_path.parent.glob("*/manifest.json"):
        for record in read_records(manifest.parent):
            captures[record.envelope["event_id"]] = record.envelope
    documents = list(sink.scan())
    report = reconcile(documents, oracle, state.report(), captures)
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        import os
        revision = os.environ.get("SOURCE_REVISION", "unrecorded")
    report.update(generated_at=utc_now(), backend="OpenSearch", source_revision=revision, python=platform.python_version(), sqlite=state.report()["sqlite_version"])
    return report

#!/usr/bin/env python3
"""Acceptance-only fixture insertion; expected coordinates precede capture."""
import argparse
import hashlib
import json
import uuid
from pathlib import Path

from alma_poc.capture import Capture, atomic_json
from alma_poc.sources import fixture


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--invalid", action="store_true")
    parser.add_argument("--index-rejection", action="store_true")
    args = parser.parse_args()
    root = Path("/data/corpus")
    oracle_path = root / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    generation = str(uuid.uuid4())
    raw, expected = fixture("ONLINE", 1001 if args.invalid else 2, 1000)
    if args.index_rejection:
        expected = {**expected, "disposition": "quarantined", "error_code": "E_INDEX_DOCUMENT"}
    identifier = f"urn:alma-poc:event:v1:{generation}:1"
    oracle["occurrences"].append({"event_id": identifier, "family": "ONLINE", "generation_id": generation, "sequence": 1, "raw_sha256": hashlib.sha256(raw).hexdigest(), **expected})
    atomic_json(oracle_path, oracle)
    with Capture(root / ("fault-" + generation), "ONLINE", "mock-acs", generation_id=generation, budget_root=root) as capture:
        capture.append(raw)
        capture.seal()
    print(json.dumps({"name": args.name, "event_id": identifier, "disposition": expected["disposition"]}))


if __name__ == "__main__":
    main()

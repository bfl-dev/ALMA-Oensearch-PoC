#!/usr/bin/env python3
"""Check measured Docker growth without pruning anything."""
import json
from pathlib import Path

from preflight import ROOT, docker_bytes


def main():
    report = json.loads((ROOT / "artifacts/preflight.json").read_text())
    baseline = report["checks"]["baseline_docker_bytes"]
    growth = max(0, docker_bytes() - baseline)
    artifacts = sum(x.stat().st_size for directory in ("artifacts", ".cache") for x in (ROOT / directory).rglob("*") if x.is_file())
    passed = growth + artifacts + report["headroom_bytes"] <= report["project_budget_bytes"]
    output = {"passed": passed, "measured_global_docker_growth_bytes": growth, "artifact_bytes": artifacts, "reserve_bytes": report["headroom_bytes"], "budget_bytes": report["project_budget_bytes"], "limitation": "Rounded CLI accounting relative to a recorded baseline; avoid concurrent unrelated Docker changes. Not a per-project filesystem quota."}
    (ROOT / "artifacts/budget.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

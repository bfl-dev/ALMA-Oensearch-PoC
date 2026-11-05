# Implementation evidence and remaining gates

Date: 3 November 2026. Accepted design: `d5d82cf5b6490efbeebf691e8ec9630407c05e5f` in PR #2, merged as `6a7804cdbe12041f8f38770ed9247591664d68ea`. Owner explicitly authorized implementation. This is a reviewable implementation, not a completed runtime demo.

| Area | Delivered | Evidence boundary |
| --- | --- | --- |
| CT-01 | Mock XML, OFFLINE API/finite stream, durable capture/manifests/watermark, independent oracle | Core/subprocess tests; no ACS capture |
| CT-02 | Confirmed persistent mandatory publication, independent replay, FULL checkpoints, bounded durable queue | Harness/configuration; RabbitMQ runtime pending |
| CT-03 | Strict normalization/mapping, create/compare indexing, bounded retry, SQLite quarantine/manual ack | Core/client-boundary tests; OpenSearch runtime pending |
| CT-04 | Queries, saved dashboard/search, timeline, explainable correlation/templates | Analysis tests; live query/UI pending |
| IMP-01 | Compose, nonroot image, digest/hash/capacity preflight | Configuration validates; pull/build/footprint pending |
| VAL-01 | Independent reconciliation, subprocess faults, live acceptance controller | Memory-backed 2,000-event exercise; controller not run live |
| DOC-06 | Sourced migration risk matrix | Documentary; source inventory unknown |

## Actual local checks

Local result: **48 tests run, 47 passed, one explicit Draft-07 dependency skip** (`PYTHONPATH=src python3 -m unittest discover -s tests -q`). Compose configuration, Python compilation and whitespace checks passed.

Host Python is 3.14.9; target 3.12.16 needs CI/image validation. The unittest suite covers parser security/Unicode, identities, source corruption, fsync/crash recovery, checkpoints, partial bulk outcomes, quarantine, replay and analysis. The 2,000-valid-event exercise uses a memory sink/wire harness and reopens SQLite between passes. It is not a RabbitMQ/OpenSearch integration result. Full Draft-07 validation skips locally when `jsonschema` is unavailable; CI and the image include that pinned dependency.

Compose configuration validates with example env files. CLI generation produced 1,000 valid occurrences per family plus two expected-invalid occurrences in a temporary directory. Preflight stopped at Docker daemon permission denied. No package was installed, image pulled/built, service started, data migrated or full ACS runtime installed by this session.

Docker client: 29.9.2; Compose: 5.6.1. `vm.max_map_count`: 1,048,576. Initial available memory was approximately 5.3 GB, below the proposed 7.25 GiB ceiling sum: recheck after closing applications or on the main PC. Host free disk space does not override the 10 GB project allowance. No installed/peak stack size, ingestion rate, recovery latency or query performance is claimed.

## Remaining acceptance

Follow the [runbook](../running.md) in a Docker-capable terminal. Preserve immutable image references, full dependency lock, runtime versions and source revision. Verify actual queue/index settings, restart durability, both replays, crash/lost-response cases, exact dispositions, 60 s outage/120 s convergence, capacity/rejection/collision negatives, resource peaks, throughput/lag and query timings. Import/inspect Dashboards and capture incident evidence. Passing the current runner alone does not establish every acceptance criterion.

No vetted ACS corpus was available. Release-specific schema/IDL, byte/framing fidelity, clock evidence and real logging-client capture remain a separate main-PC experiment under CT-01. Migration is documentary and does not assume ALMA's source version.

M0 is accepted. M1 remains open pending evidence for CA-01 through CA-12. The 2 November target elapsed; no backdated delivery or replacement deadline is claimed.

## Dashboard repair — 4 November 2026 (America/Santiago)

The checks above describe the initial implementation session. During a later dashboard diagnosis, an existing local Compose stack was accessible through authorized Docker/localhost commands. OpenSearch Dashboards reported version `3.9.0` and green status. This observation does not establish full runtime acceptance or resource fit.

- The imported dashboard panels lacked `version`. Server logs recorded `migrations730` failing with `TypeError: Cannot read properties of null (reading 'version')`, although the import API had reported success. Executing the installed migration against in-memory copies reproduced the original warning; panels with `version: "3.9.0"` produced no migration warnings.
- Added the panel versions and a regression check for version format and saved-object references. Local unittest result: 49 tests run, 48 passed, one explicit dependency skip.
- The objects were present in the Global security tenant; an API request without an explicit tenant returned no dashboards. The importer now prints a tenant-qualified direct URL, and the runbook documents it.
- Exported the existing objects to ignored `artifacts/dashboards-before-panel-version-fix.ndjson`, then reimported all five objects successfully. Readback verified their references and corrected panel definitions. No source events, index documents, or volumes were changed by the repair.
- A read-only query within the saved dashboard time range returned exactly 2,000 events: 1,000 ONLINE and 1,000 OFFLINE. The histogram aggregation also counted 2,000. The diagnostic report is in ignored `artifacts/dashboard-repair.json`.
- Browser automation was unavailable. After reimport and opening the tenant-qualified direct URL, the owner explicitly confirmed: **"Se muestran los gráficos"**. This is owner-reported rendering evidence; no automated screenshot or complete UI acceptance is claimed.

The working tree is based on implementation revision `8858de996a492a70a4ba38906d725b056d15147f` plus this repair. Remaining CA-01 through CA-12 gates are unchanged.

## Owner-reported acceptance and live view

PR #11 merged as `c7b41d7`. The owner subsequently reported `passed: true`, `error: null` from the live acceptance runner and confirmed the dashboard/live view works. Reported budget accounting was 8,347,889,432 of 10,000,000,000 bytes including a 2 GB reserve. Full host reports and their revision/configuration have yet to be reviewed. Current M1 approval gates are tracked in the [acceptance checklist](m1-review.md).

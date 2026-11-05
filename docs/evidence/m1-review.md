# M1 acceptance review

PR #11 merged as `c7b41d7`. The owner approved the acceptance report with the message **"acceptance repport approved"** and confirmed the dashboard and live view work. **M1 is approved by the owner on 5 November 2026 (America/Santiago)** under the evidence and measurement waiver recorded below.

## Recorded results

The owner supplied `{"passed": true, "report": "artifacts/acceptance.json", "error": null}`. The same run reported 6,332,800,000 bytes of global Docker growth, 15,089,432 bytes of artifacts and a 2,000,000,000-byte reserve. Budget accounting was 8,347,889,432 of 10,000,000,000 bytes, leaving 1,652,110,568 bytes beyond the reserve. Accounting is relative to the preflight baseline and uses rounded Docker totals.

The acceptance report is approved by the owner. Keep its full host artifacts and source/configuration record with the M1 evidence. Core CI passed on PR #11 head `1788254`. The sources are the synthetic ONLINE mock and OFFLINE simulator.

## Accepted evidence and limitations

| Gate | Evidence to review | Current status |
| --- | --- | --- |
| CA-01 through CA-05 and CA-11 | Full `acceptance.json`, `last-reconciliation.json`, preflight and budget reports from the passing run, plus source revision/configuration. Check identities, dispositions, repeated XML, replay, faults, queue drain and the 60 s outage / 120 s recovery target. | Acceptance report approved by owner |
| CA-06 through CA-09 | Query results/timings and `analysis.json`. Inspect the known incident, late event, excluded nearby operation, rule/version/explanation, recurring group and singleton. | Accepted for M1 using owner-confirmed UI/live view and implemented/tested analysis; full host analysis/query artifacts were not independently inspected in this session |
| Collision and capacity boundaries | Live evidence that changed content under one ID pauses, and broker/quarantine capacity preserves accepted records. Use controlled small limits and an isolated environment. | Owner reported all three live checks passed on `67b69f4` |
| CA-12 reproduction and budget | Versions/digests/lock, host settings, reported storage budget, reproduction commands and stated measurement limits. | Storage budget passed; peak memory/storage, throughput and capture-to-search lag waived by owner for M1 |
| CA-10 and final review | Review the [migration report](../research/elasticsearch-migration.md), limitations and evidence above. Record the owner's explicit M1 acceptance against a revision. | Documentary report accepted with M1; exact operational migration route depends on a source inventory |

The mixed live generator supports incident investigation with shared synthetic identifiers, upstream failure, retries, downstream failure and recovery. It can supply additional CA-07/08 examples. The original fixture remains the late-arrival/negative-case reference. See [live commands](../running.md#live-log-generation).

The [validation matrix](../validation.md) and [requirements](../requirements.md) remain the acceptance baseline. The owner accepted M1 using these evidence levels and the explicit measurement waiver.

The [boundary runner](../running.md#live-boundary-checks) writes a separate report for identity collision, broker refusal at a small queue limit, and quarantine refusal/recovery at a small logical limit. It retains source, SQLite state and broker/index volumes for review.

## Owner decisions — 5 November 2026

The owner reported a passing boundary run on image revision `67b69f431a61c4b39c20d24fa0e61f54d706c9d5`. Its host report is `artifacts/boundaries/bbddbd25-078c-4e7a-84ad-28c4463e062b/report.json`; fixture, cleanup and budget errors were null. This covers the three controlled live collision/broker/quarantine cases. The preceding build budget reported 6,549,900,000 bytes of Docker growth, 18,508,809 bytes of artifacts and a 2 GB reserve, totaling 8,568,408,809 of 10,000,000,000 bytes.

The owner's instruction **"we will skip this tests"**, immediately following the explanation of peak memory/storage, ingestion throughput and capture-to-search lag, waives those four measurements as M1 approval gates. They were not measured in the evidence reviewed here. Keep them available for a later evaluation if needed. This amendment is an owner scope decision; the recorded correctness/recovery and budget results support the current release review.

## M1 approval — 5 November 2026

- Owner instruction: **"ok can we approve m1 so?"**, following approval of the acceptance report, the passing live boundary run, working UI/live view, waiver of the four performance/resource measurements, and explanation of the documentary migration report.
- Accepted baseline: PR #12 head `61892f24c7abdcba0c76de14e664b0653f0ca33b`, including the tested implementation `67b69f431a61c4b39c20d24fa0e61f54d706c9d5` and the measurement waiver. PR #11 is already merged as `c7b41d7`.
- Decision: accept the essential synthetic-source demo and its documentary migration assessment as M1. Close the implementation/validation/delivery tasks when PR #12 is merged.
- Evidence: owner-approved acceptance report, owner-reported passing boundary run, owner-confirmed dashboard/live view, and core CI. Full host analysis/query artifacts were not independently inspected in this session; acceptance records the evidence actually available.
- Waiver: peak memory, peak storage, indexed throughput and capture-to-search lag remain unmeasured and explicitly waived for M1. The existing storage-budget and correctness/recovery results remain recorded above.
- Scope boundary: real ACS capture/import and deployment-specific migration validation require later evidence under their existing admission/inventory gates. M2 work is separately scoped.

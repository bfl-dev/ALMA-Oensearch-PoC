# M1 acceptance review

PR #11 merged as `c7b41d7`. The owner reported a successful live acceptance run and confirmed the dashboard and live view work. M1 approval awaits review of the remaining evidence below.

## Recorded results

The owner supplied `{"passed": true, "report": "artifacts/acceptance.json", "error": null}`. The same run reported 6,332,800,000 bytes of global Docker growth, 15,089,432 bytes of artifacts and a 2,000,000,000-byte reserve. Budget accounting was 8,347,889,432 of 10,000,000,000 bytes, leaving 1,652,110,568 bytes beyond the reserve. Accounting is relative to the preflight baseline and uses rounded Docker totals.

The summary establishes a reported successful runner execution. Its full host report, source revision, timings and configuration still need review. Core CI passed on PR #11 head `1788254`. The sources are the synthetic ONLINE mock and OFFLINE simulator.

## Evidence needed for approval

| Gate | Evidence to review | Current status |
| --- | --- | --- |
| CA-01 through CA-05 and CA-11 | Full `acceptance.json`, `last-reconciliation.json`, preflight and budget reports from the passing run, plus source revision/configuration. Check identities, dispositions, repeated XML, replay, faults, queue drain and the 60 s outage / 120 s recovery target. | Runner pass reported; full artifacts pending review |
| CA-06 through CA-09 | Query results/timings and `analysis.json`. Inspect the known incident, late event, excluded nearby operation, rule/version/explanation, recurring group and singleton. | UI confirmed; analysis/query artifacts pending review |
| Collision and capacity boundaries | Live evidence that changed content under one ID pauses, and broker/quarantine capacity preserves accepted records. Use controlled small limits and an isolated environment. | Core tests exist; live boundary cases pending |
| CA-12 measurement and reproduction | Versions/digests/lock, host settings, peak memory/storage observations, throughput, capture-to-search lag over a stated interval, and reproduction commands. | Storage budget passed; peak and lag evaluation pending |
| CA-10 and final review | Review the [migration report](../research/elasticsearch-migration.md), limitations and evidence above. Record the owner's explicit M1 acceptance against a revision. | Report implemented; final review pending |

The mixed live generator supports incident investigation with shared synthetic identifiers, upstream failure, retries, downstream failure and recovery. It can supply additional CA-07/08 examples. The original fixture remains the late-arrival/negative-case reference. See [live commands](../running.md#live-log-generation).

The [validation matrix](../validation.md) and [requirements](../requirements.md) remain the acceptance baseline. M1 closes when evidence satisfies these gates and the owner accepts the result.

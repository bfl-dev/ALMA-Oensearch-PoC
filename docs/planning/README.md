# Delivery tracker

Accepted design: `d5d82cf` in PR #2, merged as `6a7804c`. The owner authorized implementation on 3 November 2026. PR #11 merged as `c7b41d7`. The live generator follow-up is on `feature/live-cascade-logging`.

| Milestone group | Status | Exit condition |
| --- | --- | --- |
| M0 — Technical definition | Accepted | Recorded owner acceptance of ADRs/contracts/parameters |
| M1 — Essential demo | Approved by owner on 5 November 2026 | Accepted essential scope and [recorded measurement waiver](../evidence/m1-review.md) |
| M2 — Extensions | Unscheduled | Separately reviewed scope after M1 |

M0/M1/M2 are planning identifiers; no GitHub milestone objects were created. The original 2 November target elapsed and no replacement deadline is promised.

| Task | GitHub issue | Current evidence |
| --- | --- | --- |
| IMP-01 environment/preflight | [#3](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/3) | Accepted; latest build budget 8.57/10 GB including reserve; peak measurements waived |
| IMP-02 sources/oracle | [#4](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/4) | Accepted synthetic corpus/oracle; real ACS follow-up separately scoped |
| IMP-03 publication/replay | [#5](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/5) | Accepted owner-approved live recovery/replay report |
| IMP-04 indexing/quarantine | [#6](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/6) | Accepted owner-reported live collision and capacity checks |
| VAL-01 acceptance/evaluation | [#7](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/7) | Accepted with [evidence and measurement waiver](../evidence/m1-review.md) |
| IMP-05/06 investigation/analysis | [#8](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/8) | Accepted for first-version scope; owner-confirmed UI and tested analysis; evidence limits recorded |
| DOC-06 migration research | [#9](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/9) | [Report](../research/elasticsearch-migration.md) accepted as documentary M1 scope |
| DEM-01 delivery/evidence | [#10](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/10) | [Runbook](../running.md)/[evidence index](../evidence/implementation.md); M1 accepted; evidence and limitations recorded |

M1 approval is recorded in the [acceptance record](../evidence/m1-review.md#m1-approval--5-november-2026). Close issues #3 through #10 with the merged M1 delivery. Future work is separately scoped. [Task specifications](implementation-tasks.md) retain scope, dependencies, traceability and acceptance requirements. DOC-01 through DOC-05 form the accepted documentary baseline; real ACS runtime evidence remains separate.

# Delivery tracker

Accepted design: `d5d82cf` in PR #2, merged as `6a7804c`. The owner authorized implementation on 3 November 2026. PR #11 merged as `c7b41d7`. The live generator follow-up is on `feature/live-cascade-logging`.

| Milestone group | Status | Exit condition |
| --- | --- | --- |
| M0 — Technical definition | Accepted | Recorded owner acceptance of ADRs/contracts/parameters |
| M1 — Essential demo | Implementation merged; live run/UI pass reported; evidence review pending | Evidence for CA-01 through CA-12 |
| M2 — Extensions | Unscheduled | Separately reviewed scope after M1 |

M0/M1/M2 are planning identifiers; no GitHub milestone objects were created. The original 2 November target elapsed and no replacement deadline is promised.

| Task | GitHub issue | Current evidence |
| --- | --- | --- |
| IMP-01 environment/preflight | [#3](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/3) | Owner-reported budget accounting 8.35/10 GB; peak measurements pending |
| IMP-02 sources/oracle | [#4](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/4) | Synthetic corpus/core tests; ACS integration pending |
| IMP-03 publication/replay | [#5](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/5) | Replay/fault runner pass reported; full host report pending review |
| IMP-04 indexing/quarantine | [#6](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/6) | Live runner pass reported; capacity/collision evidence pending |
| VAL-01 acceptance/evaluation | [#7](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/7) | Runner pass reported; [M1 review gates](../evidence/m1-review.md) remain open |
| IMP-05/06 investigation/analysis | [#8](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/8) | Dashboard/live view confirmed; analysis/query artifacts pending review |
| DOC-06 migration research | [#9](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/9) | [Report](../research/elasticsearch-migration.md) ready for review |
| DEM-01 delivery/evidence | [#10](https://github.com/bfl-dev/ALMA-Oensearch-PoC/issues/10) | [Runbook](../running.md)/[evidence index](../evidence/implementation.md); remaining M1 evidence review open |

All issues remain open for evidence review. Implementation tasks can share a PR; a task is not complete because code or a PR exists. [Task specifications](implementation-tasks.md) retain scope, dependencies, traceability and acceptance requirements. DOC-01 through DOC-05 form the accepted documentary baseline; real ACS runtime evidence remains separate.

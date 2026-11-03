# Delivery plan and task preparation

**Status as of 3 November 2026:** scope, conceptual C4, and Compose approved; DOC-03 documentary investigation complete. Detailed ADRs/contracts/acceptance settings proposed for review. Runtime implementation is unstarted; no issues/milestones or agents have been created/assigned by this design work.

## Milestones to create after design review

| Milestone | Outcome | Exit condition | Schedule |
| --- | --- | --- | --- |
| M0 — Reviewed technical definition | Scope, C4, sourced feasibility, ADRs, four contracts, and acceptance settings | Explicit acceptance of the technical-design revision; no implied approval of all proposals from merging a baseline PR | Current design gate; not complete |
| M1 — Essential demo | Two synthetic sources, recovery/replay, investigation, explainable analysis, evaluation and migration research | CA-01 through CA-12 executed with honest evidence and limitations | Original 2 November target elapsed; new date pending realistic planning |
| M2 — Extensions | Improvements prioritized from M1 evidence, including broader ACS integration if feasible | Separately reviewed scope | No committed date |

Scope approval completed DOC-01; supplied-reference review completed the initial DOC-02 stage. DOC-03 now has a [feasibility outcome](../research/acs-feasibility.md). DOC-04/05 are concrete proposals in this PR, not approved or implemented results. M1 requires accepted design/criteria and explicit runtime authorization. Do not backdate results or skip validation to meet the elapsed target.

## Backlog and dependencies

Use the [issue-ready task specifications](implementation-tasks.md) to create GitHub issues after design review. IDs below are local identifiers, not GitHub issue numbers.

| Task | Outcome | Dependency/status |
| --- | --- | --- |
| DOC-01 | Approved essential scope | Complete, owner decision |
| DOC-02 | Review supplied paper/internship references | Initial review complete; no current operational inventory established |
| DOC-03 | Real ACS feasibility/fallback report | Read-only research complete; recommendation in this PR |
| DOC-04 | Exact recovery/identity, tooling/version/topology proposal | ADR-0002/0003 proposed; review pending |
| DOC-05 | CT-01 through CT-04 and quantitative settings | Concrete contracts/examples proposed; review pending |
| IMP-01 | Reproducible Compose setup and capacity preflight | DOC-05 accepted + explicit runtime authorization |
| IMP-02 | Mock/simulator, durable capture, and independent corpus manifest | IMP-01 |
| IMP-03 | Identity/checkpoints, publication, and historical replay | IMP-02 |
| IMP-04 | Deterministic indexing, partial errors/retry, SQLite quarantine | IMP-03 |
| VAL-01 | Recovery/replay/repetition and OpenSearch evaluation evidence | IMP-04 |
| IMP-05 | Queries, Dashboards, and incident reconstruction | IMP-04 |
| IMP-06 | Explainable correlation and message patterns | IMP-05 |
| DOC-06 | Documentary migration matrix | DOC-02 + selected version scope; no runtime required |
| DEM-01 | Reproduction, evidence index, evaluation and honest delivery status | VAL-01, IMP-06, DOC-06 |

Tasks can share a PR when they remain reviewable. No service or agent is required per row.

## Issue and agent preparation

The [task template](../../.github/ISSUE_TEMPLATE/task.md) captures the approved revision, observable outcome, scope/exclusions, allowed components, dependencies, relevant requirements/contracts/ADRs, acceptance, and required evidence. An implementation task without a stable interface returns to design.

Before actual delegation, record the authorized task and approved commit, branch, file boundaries, and relevant tests. Planning documents are not instructions to launch agents. Mark only verified outcomes complete. Suggested labels remain small: documentation, design, implementation, validation, demo, extension, blocked.

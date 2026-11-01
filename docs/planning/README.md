# Delivery plan and task preparation

**Status:** documentation proposal. No implementation milestones/issues have been created and no agent execution has been assigned.

## Proposed milestones

| Milestone | Outcome | Exit condition | Target |
| --- | --- | --- | --- |
| M0 — Reviewed definition | Consistent scope, requirements, references, C4/ADRs, and minimum contracts | Explicit owner approval and a record of the authorized scope | Start on 1 November 2026 |
| M1 — Essential demo | Two sources, recovery/replay, explainable analysis, and evidence on GitHub | Essential criteria executed; pending items and limitations visible | Before 3 November: target 2 November, America/Santiago |
| M2 — Extensions | Improvements prioritized from M1 evidence | New scope approved | No committed date |

M1 depends on closing M0 and authorizing implementation. Do not invent a completion date or skip verification to meet the deadline. If M1 does not fit, renegotiate scope with the owner or honestly publish an interim result.

## Candidate backlog

Convert these rows into issues when the definition is finalized. IDs are local identifiers, not GitHub issue numbers.

| Task | Reviewable outcome | Dependencies | Type |
| --- | --- | --- | --- |
| DOC-01 | Review essential scope and complete the approval record | Documentation PR | Owner review |
| DOC-02 | Obtain `alma-internship.md` and cross-check the historical reference | None | Documentary research |
| DOC-03 | Evaluate real ACS and document feasibility/fallback | DOC-01 | Research; no development before authorization |
| DOC-04 | Finalize C4, ADR-0002, tooling, and topology | DOC-01, DOC-02, DOC-03 | Design |
| DOC-05 | Finalize contracts and acceptance parameters | DOC-04 | Design |
| IMP-01 | Reproducible local environment, versions, and persistence | DOC-05 + explicit authorization | Future implementation |
| IMP-02 | ONLINE/OFFLINE sources and corpus manifests | IMP-01 | Future implementation |
| IMP-03 | Adaptation, identity, checkpoints, and transport | IMP-02 | Future implementation |
| IMP-04 | Indexing, partial errors, retries, and quarantine | IMP-03 | Future implementation |
| VAL-01 | Evidence of recovery, replay, and repetition handling | IMP-04 | Future testing |
| IMP-05 | Queries, dashboard, and reproducible incident | IMP-04 | Future implementation |
| IMP-06 | Explainable correlation and basic patterns | IMP-05 | Future implementation |
| DOC-06 | Documentary migration report | DOC-02, versions from DOC-04 | Research |
| DEM-01 | Script, evidence, reproduction, and release status | VAL-01, IMP-06, DOC-06 | Future delivery |

This order does not require a service or PR per row. Keep tasks small and consolidate when it reduces coordination without sacrificing review.

## Agent issue structure

Use the [task template](../../.github/ISSUE_TEMPLATE/task.md). Include an observable objective, authorized scope, exclusions, applicable requirements/ADRs/contracts, dependencies, permitted files, acceptance criteria, and required evidence. A task without a stable contract returns to design; it must not invent the interface.

Before delegating, identify the approved revision, task/branch, boundaries, and relevant tests. Delivery must describe the outcome, evidence, risks, and pending work. Mark only verified work as complete. Backlog preparation does not authorize agent execution.

## Candidate labels

Keep the set small: `documentation`, `design`, `implementation`, `validation`, `demo`, `extension`, `blocked`. Dependencies and criteria must appear in issue bodies; a milestone groups outcomes but does not replace acceptance.

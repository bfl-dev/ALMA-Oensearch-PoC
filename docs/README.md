# Documentation index

Status as of 3 November 2026: **scope and conceptual C4 approved; technical-design proposals ready for review**. DOC-03 documentary research is complete. Contract/ADR proposals and quantitative acceptance remain pending approval; implementation has not started.

## Reading order

1. [Project definition](project-definition.md): purpose, owner decisions, approved essential scope, extensions, and the approval record.
2. [Requirements](requirements.md): expected behavior and proposed acceptance criteria.
3. [ACS feasibility](research/acs-feasibility.md), then [architecture](architecture/README.md): research outcome, approved logical layout, and proposed detailed answers.
4. [ADRs](adr/README.md): owner decisions and proposals with their consequences.
5. [Contracts](contracts/README.md): proposed CT-01 through CT-04, envelope schema, and synthetic valid/invalid examples.
6. [Validation](validation.md): scenarios, counting oracle, and demonstration evidence.
7. [Planning](planning/README.md) and [task specifications](planning/implementation-tasks.md): milestones, dependencies, and proposed issue-ready work.
8. [References](references/README.md): sources reviewed, evidence boundaries, and pending references.
9. [Development workflow](development-workflow.md): branch naming, PR titles, and review conventions.

## Conventions

English is the working language for documentation, diagrams, templates, issues, PR titles and descriptions, and commit messages. Existing identifiers are retained to preserve traceability across the language change.

| Status | Meaning |
| --- | --- |
| Owner decision | Explicit choice by the owner; does not imply implementation |
| Proposed | Recommendation awaiting review |
| Approved | Explicitly accepted by the owner, with date and scope recorded |
| Verified | Supported by a reviewed source or identified reproducible evidence |
| Pending | Not defined, obtained, or executed |

Identifiers: `D-xx` owner decisions, `RF-xx` functional requirements, `RC-xx` quality requirements, `CA-xx` acceptance scenarios, `CT-xx` contracts, and `ADR-xxxx` architecture decisions. A written criterion is not an executed test.

## Definition gate

The essential scope and guarantee boundaries are approved; see the [approval record](project-definition.md#approval-record). Before implementation, finalize the architectural decisions, minimum contracts, and detailed demo criteria. The [review record](project-definition.md#review-record) identifies remaining items. The [issue](../.github/ISSUE_TEMPLATE/task.md) and [PR](../.github/pull_request_template.md) templates support subsequent traceability.

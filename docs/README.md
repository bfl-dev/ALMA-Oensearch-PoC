# Documentation index

Status as of 5 November 2026: **M1 approved by the owner with recorded evidence levels and a measurement waiver**. See the [M1 approval](evidence/m1-review.md). Start with the [runbook](running.md) and [evidence record](evidence/implementation.md).

## Reading order

1. [Project definition](project-definition.md): purpose, owner decisions, approved essential scope, extensions, and the approval record.
2. [Requirements](requirements.md): expected behavior and accepted acceptance criteria.
3. [ACS feasibility](research/acs-feasibility.md), then [architecture](architecture/README.md): research outcome, approved logical layout, and proposed detailed answers.
4. [ADRs](adr/README.md): owner decisions and proposals with their consequences.
5. [Contracts](contracts/README.md): accepted CT-01 through CT-04, envelope schema, and synthetic valid/invalid examples.
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

M0 is accepted at revision `d5d82cf`; owner explicitly authorized implementation. See the [acceptance record](project-definition.md#technical-design-acceptance-and-implementation-authorization). M1 is accepted as recorded in the [approval and waiver](evidence/m1-review.md). [Planning](planning/README.md) links the implementation work; [migration research](research/elasticsearch-migration.md) is documentary only.

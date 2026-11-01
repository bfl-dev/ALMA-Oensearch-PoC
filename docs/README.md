# Documentation index

Status as of 1 November 2026: **draft for scope review**. Implementation is not authorized.

## Reading order

1. [Project definition](project-definition.md): purpose, owner decisions, essential demo, extensions, and pending review.
2. [Requirements](requirements.md): expected behavior and proposed acceptance criteria.
3. [Architecture](architecture/README.md): conceptual C4 views and questions requiring evaluation.
4. [ADRs](adr/README.md): owner decisions and proposals with their consequences.
5. [Contracts](contracts/README.md): boundaries, identity, errors, and guarantees to specify.
6. [Validation](validation.md): scenarios, counting oracle, and demonstration evidence.
7. [Planning](planning/README.md): milestones, dependencies, and issue/agent-task preparation.
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

Before implementation, agree on the essential scope, recovery guarantees, minimum contracts, and demo criteria. The [review record](project-definition.md#review-record) identifies pending items. The [issue](../.github/ISSUE_TEMPLATE/task.md) and [PR](../.github/pull_request_template.md) templates support subsequent traceability.

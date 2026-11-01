# Architecture Decision Records

An ADR records context, a choice, alternatives, consequences, and required validation. Writing a proposal does not make it approved.

| ADR | Topic | Status |
| --- | --- | --- |
| [0001](0001-project-constraints.md) | Owner technology constraints and boundaries | Owner decisions; not approval of the full scope |
| [0002](0002-recovery-and-event-identity.md) | Recovery and event identity | Proposed; requires review |

Use the [template](template.md) for new decisions. Avoid one ADR per minor detail. Before implementation, resolve at least recovery/identity guarantees, the processing tool, and the local topology; these may be grouped if the rationale is brief.

# Component contracts

**Status:** v1 contracts accepted at revision `d5d82cf` on 3 November 2026. Initial implementation is under review; runtime acceptance is separate.

| Contract | Boundary and content | Acceptance |
| --- | --- | --- |
| [CT-01](ct-01-source.md) | Durable capture/framing, XML/JSON profiles, exact envelope/identity, provenance, clock and limits | CA-01, CA-02, CA-05 |
| [CT-02](ct-02-transport.md) | Durable RabbitMQ publication, routing/confirms, checkpoints and backpressure | CA-03, CA-04 |
| [CT-03](ct-03-indexing.md) | Deterministic fields/mappings, ID/index, per-item results, retries, SQLite quarantine and retention | CA-01 through CA-05, CA-11 |
| [CT-04](ct-04-analysis.md) | Queries/timeline, small correlation rules, pattern groups and explainable outputs | CA-06 through CA-09 |

[Envelope JSON Schema](schemas/event-envelope-v1.schema.json) covers structure; [examples](examples/README.md) illustrate valid/invalid payloads and legitimate repeated occurrences. Cross-field identity, byte limits, digests, clock semantics, and runtime durability also require the normative prose. The schema does not replace those checks.

Read [ADR-0002](../adr/0002-recovery-and-event-identity.md) and [ADR-0003](../adr/0003-tools-and-local-deployment.md) with these contracts. One codebase can implement the logical boundaries; four contracts do not require four services.

## Invariants and evolution

- Same original occurrence, same ID across continuous ingestion, restart, and replay.
- Distinct occurrences remain distinct even if XML, message, and timestamp match.
- Content hashes verify bytes; paths, timestamps, delivery tags, or new per-attempt IDs cannot define occurrence equivalence.
- Preserve original raw input and clock/provenance; no invented source fields or causal claims.
- Keep parser version and concrete index stable for one materialization/replay window. Explicit corrections create a versioned materialization, preserving original identities/evidence.
- Reject unknown envelope properties/versions until a reviewed compatibility update. Keep supplied source formats separate from this project's capture framing.

## Review outcome

Owner accepted the design and authorized implementation. See the [acceptance record](../project-definition.md#technical-design-acceptance-and-implementation-authorization). Source admission and runtime acceptance remain separate evidence levels; see the [implementation evidence](../evidence/implementation.md).

# Component contracts

**Status:** proposed inventory, not an approved software contract. There are no schemas, APIs, or executable configuration at this stage.

## Boundaries to specify

| ID | Boundary | Minimum contract content | Acceptance |
| --- | --- | --- | --- |
| CT-01 | Source/file → adapter | XML/JSON format and framing, encoding, clock, provenance, stable occurrence identity, rotation, and replay | CA-01, CA-02, CA-05 |
| CT-02 | Adapter → RabbitMQ | Versioned envelope, routing, persistence, durable confirmation, checkpoint, backpressure, and unroutable messages | CA-03, CA-04 |
| CT-03 | RabbitMQ → processor → OpenSearch/quarantine | Validation, mappings, ID/index, partial bulk results, retries, acknowledgment, and durable disposition of permanent errors | CA-03, CA-04, CA-11 |
| CT-04 | Stored events → analysis/visualization | Time-based queries, original references, correlation explanations, and pattern output | CA-06 through CA-09 |

Contracts describe logical boundaries; they do not require four services.

## Candidate minimum model

| Concept | Semantics to agree on |
| --- | --- |
| `schema_version` | Envelope version; compatibility policy and rejection of unknown versions |
| `event_id` | Identity of an original occurrence, stable across redelivery/restart/replay |
| `source` | ONLINE/OFFLINE family, producer, environment, and durable source coordinates |
| `event_time` | Time declared by the source, format/time zone, and handling of missing or invalid values |
| `ingested_at` | Ingestion time, distinct from original time; not part of identity |
| `severity`, `component`, `message` | Normalized fields with provenance and preservation of unmapped values |
| `raw` or durable reference | Retrieval of the original record without reconstructing it from a template |
| `correlation_keys` | IDs observed at the source or explicitly inferred, with their provenance |
| Processing metadata | Parser version, replay/attempt, and diagnostics; separate from original identity |

Field names are candidates. Lengths, types, required/optional fields, invalid timestamps, multiline XML, characters, and size limits must be fixed using real examples or documented fixtures before implementation.

## Identity invariants

- Same source event, same identity, even if attempt count or ingestion mode changes.
- Distinct occurrences, distinct identities, even if every business field matches.
- Ingestion time, delivery tag, redelivery flag, or a per-attempt UUID do not determine source identity.
- A content hash may verify integrity but cannot distinguish identical occurrences.
- Replay preserves file/generation identity and position; it does not automatically infer that two equal files represent the same events.
- Identity is also preserved through quarantine and reprocessing. The target index and retention window are part of the idempotency contract.

## Minimum analysis output

A correlation must include event identifiers, rule and version, satisfied conditions, window, and explanation, stating whether the link is observed or inferred. A pattern must include its criterion/template, frequency, and original examples. Neither output changes or deletes source events.

## Next-stage deliverables

1. Approved field table, valid and invalid ONLINE/OFFLINE examples, and evolution policy.
2. Envelope schema and error/disposition catalog, after scope approval.
3. Exact identity/checkpoint, confirmation, and destination rules consistent with ADR-0002.
4. Verifiable correlation and pattern examples implementing CA-08/CA-09.

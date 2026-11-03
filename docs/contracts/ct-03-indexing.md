# CT-03 — Processing, indexing, and quarantine

**Status:** proposed for review. RF-04, RC-01 through RC-05; CA-01 through CA-05 and CA-11. Depends on CT-01/CT-02 and ADR-0002/0003.

## Deterministic normalized document

Each valid payload yields exactly one document in concrete index `poc-events-v1`, `_id=event_id`, parser version `1.0.0`. No attempt time, replay mode, mutable source path, or broker delivery tag enters the stored document. All fields below are mandatory; explicitly nullable fields use null. No extra top-level fields.

| Field | Type/meaning | Proposed OpenSearch mapping |
| --- | --- | --- |
| `document_version` | Literal `1.0.0` | keyword |
| `event_id` | CT-01 occurrence ID | keyword; also `_id` |
| `source` | Exact CT-01 source object | strict object; strings keyword, sequence long |
| `event_time.original` | Original timestamp string | keyword, nullable |
| `event_time.scale` | CT-01 scale | keyword |
| `event_time.utc` | UTC millisecond RFC 3339 projection or null | date, nullable |
| `event_time.status` | `normalized`, `invalid`, or `unsupported_scale` | keyword |
| `ingested_at` | Exact first capture time; not current processing time | date |
| `severity` | Uppercase XML root / validated OFFLINE severity | keyword |
| `component` | CT-01 selection rule; null if absent in XML | keyword, nullable |
| `message` | Text outside XML `Data` descendants / OFFLINE message | text, no keyword copy of the full message |
| `data` | Ordered string `{name,value}` pairs, preserving duplicates | object with indexing disabled; retained in `_source` |
| `correlation_keys` | Fixed nullable keys `request_id`, `operation_id`, `stack_id`, `context`, plus `provenance` | strict object, keyword values |
| `raw` | Exact CT-01 raw object, including base64/digest | strict object; data binary stored in `_source`, remaining fields keyword |
| `parser_version` | Literal `1.0.0` | keyword |

Create mappings explicitly with top-level and fixed-object `dynamic=strict`; do not dynamically turn arbitrary ACS `Data.Name` values into fields. Keep `_source` enabled. The full normalized document, including raw evidence, fits a proposed 256 KiB serialized limit. The binary field is not full-text indexed. Use one primary shard, zero replicas, and request-durable translog behavior; verify actual configuration during setup. This is no HA/storage-loss guarantee.

UTC-declared XML timestamps without a zone use the explicit source manifest declaration, never a guessed machine zone. Valid UTC values normalize to milliseconds and `Z`. Invalid XML dates preserve `original`, set `utc=null`, and mark `invalid`; a missing XML TimeStamp is a CT-01 payload violation. TAI/unknown records preserve original time with `utc=null` and `unsupported_scale`. Do not substitute ingestion time for event time. Initial synthetic incident records use declared UTC; current real ACS conversion is unverified.

Extract XML correlation keys only from unambiguous `Data` names `RequestId`/`OperationId`, attributes `StackId`/`Context`, or the matching OFFLINE keys. Conflicting repeated ID values or a promoted value longer than 128 characters yield a null key and a visible diagnostic; never choose or truncate one silently. Data entries remain intact. Provenance is `synthetic` for mock/simulator and `source` for verified real export. Unavailable keys are null, not fabricated.

## Bulk and errors

Use `create`, not auto-generated document IDs or unconditional replacement. Batch at most 20, flush within 250 ms, consume with prefetch 20 and explicit per-delivery acknowledgments. A successful response envelope does not mean every item succeeded; inspect individual statuses and associate each with its delivery.

| Outcome | Required action |
| --- | --- |
| Item `201` | Acknowledge its delivery after successful indexing response |
| Item `409` | Retrieve existing document; compare full deterministic JSON structure including raw/coordinates/parser version. Equal: acknowledge. Missing: retry. Different: pause as identity collision without overwrite/ack |
| Network/timeout, item `429`, transient `5xx` | Retry unresolved items with ADR-0002 waits; retain identity/destination |
| Broken XML/JSON, wrong profile type, unsupported XML child/root | Commit quarantine entry, then acknowledge |
| Verified document-specific mapping rejection | Commit quarantine with item response, then acknowledge; retain other batch results |
| HTTP `401`/`403`, missing index, bad shared mapping, unclassified failure | Pause visibly without acknowledgment; configuration/system error is not bad source data |
| HTTP `413` | Split batch; single document over agreed bound is quarantined with reason, while preserving raw input |
| Quarantine full/unavailable or failed commit | Pause, retain delivery; do not acknowledge/drop/requeue in a busy loop |

Retry delays: 1, 2, 4, 8, then at most 10 seconds, without a drop-on-exhaustion policy. Initially 10-second network timeout. Maintain broker heartbeats while waiting/processing; network work cannot block the AMQP loop indefinitely. Reestablish channels/consumers after connection loss. Already settled successes are not deliberately retried, but uncertain outcomes remain safe by ID/content checks.

## SQLite quarantine

Durable worker database, explicit transaction, `synchronous=FULL`, unique key `(event_id, materialization)` for a structurally valid envelope. Store original envelope/raw bytes, coordinates, raw hash, materialization `poc-events-v1`, parser version, error code/stage, and inspectable error details. Redelivery with the same key verifies matching source/raw and reuses one entry. A conflicting payload pauses as an identity collision. Commit precedes AMQP acknowledgment; restart after commit/before acknowledgment must remain idempotent.

Unusable wire envelopes may have no trustworthy event ID. Retain exact wire bytes in a separate diagnostic table under `wire:<sha256-of-wire-bytes>`, with delivery observations. This key groups corrupt transport evidence; it is not occurrence identity, and those diagnostics are excluded from valid-source identity counts. Do not replace a known source ID with a body hash. Unknown wire versions are diagnostic failures, not silently upgraded.

Provide a future inspection/export command and an explicit reprocessing/resolution procedure. Preserve original evidence; never automatically delete quarantine to meet a capacity or latency target. Nominal quarantine budget 64 MiB plus measured database overhead; pause before its full-disk failure boundary. Invalid records do not appear in valid-event OpenSearch counts.

## Retention and materialization

Keep source corpus, manifests, broker/state volumes, quarantine, and the concrete index from run start to explicit teardown. Nominal baseline window 24 hours; no scheduled deletion is implied. No rollover, arrival-time index routing, or destructive reset during retries/replay. Queries/counts select exactly `poc-events-v1`, not a wildcard over corrected materializations.

Parser changes/corrections preserve original occurrence identity but require an explicitly versioned result index and correction provenance. They are not silent rewrites or identity changes. The essential validation proves same-profile replay; a complete correction UI/workflow is outside this first implementation.

## Error codes and evidence

| Code | Meaning |
| --- | --- |
| `E_XML_PARSE` / `E_JSON_PARSE` | Invalid syntax/encoding or forbidden XML constructs |
| `E_PAYLOAD_PROFILE` | Valid syntax but wrong type/required field/root/child/profile |
| `E_ENVELOPE` | Invalid transport schema/version/identity/integrity; preserve diagnostic evidence |
| `E_INDEX_DOCUMENT` | Verified document-specific permanent indexing rejection |
| `E_OVERSIZE` | Agreed record/document bound exceeded; source evidence retained |
| `E_IDENTITY_COLLISION` | Same coordinates/ID with different source or deterministic document; pause |
| `E_SYSTEM` / `E_CAPACITY` | Infrastructure/configuration/capacity blocker; no silent disposal |

CA-03/CA-04/CA-11 must inject response loss, partial bulk results, quarantine-commit/ack crashes, capacity backpressure, and broker restart. Schema/example checks in this PR do not establish those runtime guarantees.

# ADR-0002 — Recovery through redelivery and stable occurrence identity

- Status: **proposed for technical-design review; not approved or runtime-verified**
- Updated: 3 November 2026
- Requirements: RF-03, RC-01 through RC-05
- Contracts: [CT-01](../contracts/ct-01-source.md), [CT-02](../contracts/ct-02-transport.md), [CT-03](../contracts/ct-03-indexing.md)

## Context and alternatives

A failure between a write and its confirmation creates an uncertain outcome. Reprocessing must converge while preserving distinct occurrences with identical bodies/timestamps. Reject body/timestamp hashes and per-attempt UUIDs as occurrence identities; avoid a distributed end-to-end transaction for this demo. Propose at-least-once delivery with idempotent storage effects. [S-03 and S-04](../references/README.md) cover the distinct confirmation/indexing boundaries.

## Capture and identity

Persist a lowercase UUID `generation_id` manifest before records. Allocate contiguous positive `sequence` values, including malformed payloads. Identity is literal ASCII `urn:alma-poc:event:v1:<generation_id>:<sequence>`, with canonical UUID and decimal sequence without leading zeroes. No hash, path, clock, ingestion mode, or attempt number enters it. Equal records at sequences 1 and 2 are separate events.

The capture file stores complete newline-terminated envelopes with base64 raw bytes. Sync the frame before accepting the event. Manifest creation uses an atomic write and file/parent-directory sync. Resume writers by scanning complete frames; an incomplete final append was not accepted and can be repaired before the next occurrence. Never reuse an accepted sequence.

The guarantee begins at durable project capture or confirmed broker acceptance, with storage retained. Upstream ACS loss, uncaptured events, corrupt/deleted sources, destroyed volumes, disk failure, and unbounded production are outside it. Real ACS needs a separately verified upstream export contract.

## Checkpoints and replay

One live publisher per generation initially. After routable persistent publication is confirmed, commit the highest contiguous confirmed sequence in SQLite using explicit transactions and `synchronous=FULL`. Never advance on send, timeout, returned/negatively confirmed publish, or failed checkpoint commit.

A crash after confirm but before checkpoint may republish the same record. Retain records and manifests throughout the supported replay window. Replay has a separate durable job/cursor and never rewinds the live checkpoint; its envelope, identity, raw bytes, provenance, and first capture time are unchanged.

Moves/copies preserve manifests. New independent occurrences require new generations even if files match. File hashes verify integrity, not occurrence equivalence. Accepted source generations cannot be truncated or edited in place.

## Durable processing disposition

1. Manual consumer acknowledgments, maximum 20 in-flight records. Validate envelope structure/integrity before payload parsing.
2. Normalize deterministically with parser profile `1.0.0`. The stable document's `ingested_at` is original `captured_at`; per-attempt timings are runtime metrics.
3. Bulk `create` into concrete `poc-events-v1`, `_id=event_id`. Inspect each item; HTTP success alone is insufficient.
4. Successful create permits acknowledgment. On `409`, retrieve and compare the complete deterministic document. Equal content is a successful retry; mismatch pauses as an identity/parser collision without overwriting/acknowledging it.
5. Permanent data failure permits acknowledgment only after an idempotent SQLite quarantine transaction commits. Retain envelope, raw evidence, coordinates, stage, and reason. Storage failure/full capacity leaves the delivery unacknowledged and pauses work.
6. Retry connection errors, `429`, and transient server failures with waits 1, 2, 4, 8, then at most 10 seconds. No fixed retry limit discards accepted records. Auth errors, absent index, invalid shared mapping, and unknown systemic errors pause visibly instead of quarantining the backlog.
7. Bulk batches at most 20 items, partial flush within 250 ms, network timeout initially 10 seconds. Maintain AMQP heartbeats during requests/waits. Retry only unresolved items; acknowledge successes individually.

Parameters are proposed test settings. Busy requeue loops, treating all `400` responses as data errors, or treating all conflicts as success violate this contract. CT-03 specifies the error catalog and SQLite quarantine. Broker, state, and OpenSearch volumes survive container/process restart; no replication is claimed.

## Destination, retention, and correction

One concrete index supports a bounded run: no arrival-date routing, rollover, TTL, index recreation, or retention deletion during failure/replay tests. The guarantee lasts from recorded run start until explicit teardown while retained source/destination exist; nominal validation window is 24 hours, not a deletion timer.

Changing parser/input is an explicit new materialization with provenance. Preserve occurrence IDs and original raw evidence; do not edit an accepted generation, overwrite a conflicting v1 document, or mix parser versions in `poc-events-v1`. Use a separate versioned result index and query/count one materialization at a time. Correction workflow is a documented boundary, not an implemented essential-demo capability.

## Failure matrix

| Failure point | Expected recovery |
| --- | --- |
| Before complete capture is synced | Not accepted; repair unfinished append before next acceptance |
| After capture, before confirmed publication | Republish retained source |
| After confirm, before checkpoint commit | Possible redelivery under the same ID |
| Before indexing or during outage | Retain delivery/backlog and bounded retries |
| After indexing, before response/acknowledgment | Retry create and verify matching existing document |
| After quarantine commit, before acknowledgment | Same event resolves to the same quarantine entry |
| Broker restart with pending accepted messages | Retained queue recovers; connections reestablished |
| State/quarantine cannot commit | Pause without acknowledgment or progress advancement |

CA-02 through CA-05 and CA-11 require independent identity/content reconciliation and injected fault evidence. None has executed. See [ADR-0003](0003-tools-and-local-deployment.md) for tooling rationale.

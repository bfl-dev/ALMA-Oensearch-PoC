# ADR-0002 — Recovery through redelivery and stable occurrence identity

- Status: **proposed; not approved**
- Date: 1 November 2026
- Requirements: RF-03, RC-01 through RC-05
- Contracts: CT-01, CT-02, and CT-03

## Context

A process can fail between a write and its confirmation. Processing an event again must not duplicate it. At the same time, ACS may produce different occurrences with identical bodies and timestamps. Content-based identity conflates these cases.

RabbitMQ documents publisher confirms and consumer acknowledgments as distinct mechanisms [S-03]. OpenSearch documents independent results for each bulk operation [S-04]. These facts require evaluating every boundary; they do not establish an end-to-end guarantee by themselves.

## Alternatives

| Option | Proposed evaluation |
| --- | --- |
| Identity from a body/timestamp hash | Reject: collapses legitimate repetition |
| New UUID for each attempt or replay | Reject: turns retries into new events |
| Persistent occurrence identity established before publication | Candidate: preserve across continuous reads, retries, and replay |
| End-to-end distributed transaction | Do not prioritize for the demo because of complexity; exactly-once is not promised |

## Candidate design

1. Establish durable source coordinates before publishing the event. For files, evaluate immutable file/generation identity and stable record position. A mutable path name is insufficient.
2. Derive or retain an `event_id` from those coordinates. Two equal records at different positions retain different IDs. For mocks, persist execution identity and generation sequence before delivery.
3. Advance the checkpoint only after confirmation of durable acceptance at that stage's destination. Queue, message, storage, and publisher-confirm configuration must be specified together; the persistence flag alone does not establish the guarantee.
4. Consume with explicit acknowledgment after each event is successfully indexed, or after durable transfer to quarantine when permanently invalid. Also evaluate failures when publishing to quarantine.
5. Keep both the ID and indexing destination stable throughout the supported window. Sending the same identity to another index may create another copy: agree on index/retention and replay policy before implementation.
6. Inspect each bulk item result. Separate successes, permanent rejections, and transient failures; an uncertain outcome requires an idempotent retry. Do not treat every conflict as success without checking its semantics.
7. Define retries with waiting, in-flight message limits, and backpressure. Do not delete backlog to meet a latency target.

## Consequences and open questions

The aim is at-least-once processing with an idempotent effect at the supported destination. Identity is not semantic deduplication of logs. The source contract and retention are part of the guarantee, not secondary details.

Pending: exact coordinate definition, file rotation/truncation, preservation of file identity when copying, checkpoint and quarantine technology, indexes, error policy, and versions. A parser change must not silently change occurrence identity; reprocessing requires a result-version policy.

## Validation for acceptance or rejection

CA-02 through CA-05 and CA-11. Include failures before/after confirmations, response loss, partial bulk success, and two events with equal content. Compare identity sets and content with an independent source manifest.

Sources: [S-03 and S-04](../references/README.md). These were reviewed to inform the evaluation; compatibility must be checked for the versions selected later.

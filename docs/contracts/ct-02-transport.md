# CT-02 — Adapter to RabbitMQ

**Status:** accepted by owner on 3 November 2026; runtime evidence tracked separately. RF-03, RC-01/RC-02, CA-03/CA-04; depends on CT-01 and ADR-0002.

## Broker contract

| Setting | Proposed v1 value |
| --- | --- |
| Protocol | AMQP 0-9-1, private Compose network |
| Queue | `poc.events.v1`, explicitly classic, durable, nonexclusive, not auto-delete |
| Exchange/routing | Default exchange `""`, routing key exactly `poc.events.v1`, one target |
| Message | CT-01 UTF-8 JSON, content type `application/json`, persistent delivery mode 2, message ID equal to event ID |
| Publication | Publisher confirms; `mandatory=true`; handle returns, negative confirms, timeouts, disconnects |
| Capacity | 64 MiB ready-body cap, overflow `reject-publish`; no TTL, expiration, or drop-head |
| Persistence | Broker volume retained across restart; verify declarations for selected RabbitMQ version |

Durable queue, persistent messages, and confirmations work together. A confirm alone does not prove routing: inspect returned/unroutable outcomes. One default-exchange route avoids ambiguous multi-queue partial acceptance. The cap excludes broker overhead/properties/unacknowledged deliveries; combine with at most 20 in-flight deliveries, bounded envelopes, broker alarms, and total disk accounting.

When a publish is rejected, retain the source record and do not advance progress. See official [confirms](https://www.rabbitmq.com/docs/confirms), [queue durability](https://www.rabbitmq.com/docs/queues), and [overflow](https://www.rabbitmq.com/docs/maxlength) guidance.

## Publisher progress and backpressure

One live publisher per generation. SQLite checkpoint key is `(generation_id, destination_materialization)` plus highest contiguous confirmed sequence. Live/replay cursors are separate; interrupted replay persists its job/cursor independently. Both publish original envelopes. Parsing XML/JSON belongs to the worker; malformed payload inside a valid envelope can be published.

After a routable confirmed acceptance, commit progress in an explicit SQLite transaction with `synchronous=FULL`. On send alone, return, negative confirm, timeout, or disconnect, keep the checkpoint unchanged. Uncertain outcomes may cause duplicate publication under the same ID. Retry with waits capped at 10 seconds while servicing heartbeats; never allocate a new identity or busy-loop.

Blocked broker or exhausted storage pauses capture/production before accepting new data. Existing source files remain authoritative. Visible status distinguishes source backlog, broker ready/unacknowledged deliveries, and blocked/error state. Source records are not deleted after successful publication.

Before implementation completion, verify actual declaration properties, route/return handling, disk alarms, SQLite commits, uncertain-confirm recovery, and live/replay separation. A persistence flag or orderly shutdown alone cannot prove CA-03/CA-04. No runtime broker configuration is introduced here.

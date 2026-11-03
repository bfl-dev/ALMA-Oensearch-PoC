# ADR-0003 — Python processing and a bounded Compose deployment

- Status: **proposed for technical-design review**
- Date: 3 November 2026
- Traceability: RF-01 through RF-08; RC-01 through RC-06; CT-01 through CT-04
- Already accepted by owner: OpenSearch, RabbitMQ, Compose, temporary host, two-hour ACS research ceiling

## Context and alternatives

The PoC needs explicit occurrence identity, durable progress, per-item indexing decisions, and quarantine. It must fit the temporary 16 GB RAM / 10 GB project-storage host and later move to the main PC.

| Approach | Strength | Cost |
| --- | --- | --- |
| Small Python adapter/worker | Explicit persistence, acknowledgment, collision checks, and fault injection | We own and must verify reconnect/error handling |
| Logstash with RabbitMQ input and OpenSearch output | Established ecosystem; relevant historical comparison | Evaluate PQ/ack/output-error boundaries against our contracts; additional JVM/configuration |
| Both | Can divide responsibilities | Adds another recovery boundary without a demonstrated need |

[RabbitMQ input](https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-rabbitmq) and [Logstash PQ](https://www.elastic.co/docs/reference/logstash/persistent-queues) documentation describe configurable durability, not proof of this full contract. The Python recommendation is about bounded scope and inspectability, not a claim that Logstash cannot be reliable.

## Proposed decision

Use one Python codebase with capture/adapter, worker, and on-demand analysis entry points. These roles are not separate microservice projects. Start with the documented mock, per [DOC-03](../research/acs-feasibility.md), preserving a file-export boundary for future real ACS.

Use separate SQLite databases for adapter checkpoints and worker quarantine on local persistent volumes, explicit transactions, `synchronous=FULL`, and one writer per role. Record effective settings and actual SQLite version. Retain source records independently. SQLite quarantine provides a uniqueness constraint and inspectable idempotent retention without another RabbitMQ publish/confirm boundary. A broker quarantine is an alternative, not a required service.

## Proposed version baseline

| Component | Version | Documentary evidence |
| --- | --- | --- |
| OpenSearch | `3.9.0` | [Release](https://github.com/opensearch-project/OpenSearch/releases/tag/3.9.0), 29 September 2026 |
| Dashboards | `3.9.0` | [Release](https://github.com/opensearch-project/OpenSearch-Dashboards/releases/tag/3.9.0), matching server |
| RabbitMQ | `4.4.0` | [Release](https://github.com/rabbitmq/rabbitmq-server/releases/tag/v4.4.0), 19 October 2026 |
| CPython | `3.12.16` | [Security release](https://www.python.org/downloads/release/python-31216/), 25 October 2026 |
| Pika | `1.4.4` | [Stable release](https://github.com/pika/pika/releases/tag/1.4.4); avoid inspected 1.5 release candidates |
| opensearch-py | `3.2.0` | [Release](https://github.com/opensearch-project/opensearch-py/releases/tag/v3.2.0); [matrix](https://github.com/opensearch-project/opensearch-py/blob/v3.2.0/COMPATIBILITY.md) covers OpenSearch 3.x |
| SQLite | Bundled with Python image | Record actual version/durability settings during setup |
| Docker Engine / Compose | Compatible host versions | Record exact versions and storage location during IMP-01 |

These are candidate pins, not installed/integration-tested dependencies. Before setup resolve available Linux/amd64 image tags, immutable digests, transitive locks, full footprint, and compatibility smoke checks. Do not use floating `latest` or silently substitute versions. Registry image availability/digests were not verified here.

## Proposed deployment and budget

One OpenSearch node, one Dashboards instance, one RabbitMQ, and adapter/worker roles; analysis reuses the project image on demand. One concrete events index, one primary shard, zero replicas. One durable classic queue. Neither storage choice demonstrates replication/high availability.

| Role | Initial memory ceiling proposal |
| --- | --- |
| OpenSearch | 4 GiB total, with 1 GiB fixed heap inside that total |
| Dashboards | 1.5 GiB |
| RabbitMQ | 0.75 GiB; check broker memory/disk alarms against host/container |
| Project processes combined | 1 GiB; analysis can run separately from peak ingestion |

Total proposed ceilings: 7.25 GiB. These are starting limits to measure, not observed consumption. Treat 10 GB as the entire incremental disk budget: downloaded/unpacked images, cache, ACS dependencies if any, source/state, broker, indexes, logs, and evidence. Plan at least 2 GB of growth/headroom inside that budget; measure actual filesystem headroom and engine disk thresholds before setup. If it cannot fit, report the blocker and move to the main PC or revise packaging; do not disable disk safety thresholds or delete unrelated host data.

Choose small ordinary corpus records so the complete acceptance dataset stays within 100 MiB; the maximum record-size case is a separate boundary test. Initially bound datasets to 100 MiB, ready queue bodies to 64 MiB, and quarantine to 64 MiB, with rotated runtime logs. These caps exclude engine overhead and do not replace total measurement. Pause before accepting more data at capacity; preserve existing accepted records.

Bind UI/API ports to loopback and use a private Compose network. Keep test secrets out of tracked files. Use OpenSearch's local test security setup with an explicit password and document its self-signed certificate boundary; no corporate SSO is implied.

Inspect host memory/free space, `vm.max_map_count`, and runtime prerequisites using [official Docker guidance](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/). Record needed host changes; do not change machine settings during this documentation stage.

The main PC changes allocations and measurements, not identities/contracts. Preserve manifests/IDs and rerun resource preflight. Proposed source mode, processing, storage, pins, and allocations need review; accepted Compose/C4 decisions do not imply their approval. No runtime configuration is introduced.

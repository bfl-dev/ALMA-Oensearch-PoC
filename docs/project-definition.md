# Formal project definition

**Status:** proposed for review. **Approval owner:** project owner. **Implementation:** awaiting authorization.

## Purpose

Build a demonstrable personal project that strengthens an ALMA 2027 internship application through evidence of design, failure recovery, and log-based incident investigation. The first delivery must be understandable from GitHub and reproducible in a bounded local environment.

Observability is initially limited to logs and the operational state of the pipeline. A complete metrics and tracing platform is outside the proposed demo.

## Owner decisions

| ID | Owner decision |
| --- | --- |
| D-01 | OpenSearch will be the main engine; migration from Elasticsearch will be researched through documentation |
| D-02 | Draw inspiration from ALMA's published historical architecture without inferring its current infrastructure |
| D-03 | Two sources: real ACS ONLINE or an XML mock, and OFFLINE through a web/API application simulator |
| D-04 | RabbitMQ as the persistent messaging intermediary |
| D-05 | Continuous ingestion and historical reprocessing |
| D-06 | Recovery after abrupt failures and temporary OpenSearch outages |
| D-07 | Avoid pipeline-generated duplicates while preserving legitimately repeated ACS events |
| D-08 | Search, visualization, incident reconstruction, explainable automatic correlation, and pattern discovery |

The requested work order is: repository → scope/requirements → C4/ADRs → contracts → milestones/issues/tasks → authorized implementation and testing.

## Proposed essential demo

No D-08 capabilities are removed: their first versions are kept small.

| Area | Proposed first version | Expected evidence |
| --- | --- | --- |
| ONLINE | Evaluate a real ACS component first; fall back to a documented XML mock if dependencies block the demo | Producer provenance, version, and limitations; never claim real integration when using a mock |
| OFFLINE | Small application/API simulator with normal operation, failure, and recovery | Reproducible events with request/operation identifiers |
| Transport | One persistent local RabbitMQ instance and bounded consumers | Recovery of pending messages after restart |
| Indexing | OpenSearch with Dashboards for visualization; local topology to evaluate | Reproducible searches and visible ingestion status |
| Replay | Reread an immutable historical file, overlapping with continuous ingestion | Same set of identities after one or more rereads |
| Incidents | One known synthetic incident with preceding and subsequent context | Timeline, supporting events, and limits of the explanation |
| Correlation | One or two deterministic rules using identifiers and time windows | Rule/version, related events, and reason for the link |
| Patterns | Group normalized messages, report frequency, and provide inspectable examples | At least one recurring pattern and one message outside the group |
| Migration | Brief compatibility and risk report with sources | Distinction between documented facts, hypotheses, and future tests |

ONLINE/OFFLINE identify source families, not connected/disconnected modes. Do not invent a shared identifier between sources to make correlation appear real: any synthetic link must be declared as part of the scenario.

## Proposed extensions

- Distributed clusters, high availability, and node-loss testing.
- More formats, sources, and operational scenarios; broader ACS integration after an initial mock.
- Anomaly detection, embeddings, machine learning, and process mining.
- Custom UI, external alerts, advanced SSO/RBAC, distributed metrics/traces, and remote deployment.
- An executed Elasticsearch migration: outside the requested scope and requiring an explicit change.

These extensions are not prerequisites for completing the essential demo.

## Boundaries of the proposed guarantees

The goal is to recover events available in a persistent source or accepted by durable transport, within the agreed volume and outage window. The exact acceptance point and checkpoint advancement rule must be defined before implementation. End-to-end exactly-once delivery is not promised.

The demo must cover abrupt producer/adapter and consumer termination, broker restart with storage retained, and temporary OpenSearch unavailability. Volume destruction, physical disk loss, source deletion, and an unlimited backlog are outside the proposed guarantee and must be disclosed in the delivery.

## Delivery before 3 November

The target is interpreted as **2 November 2026, America/Santiago**. The deadline requires prioritization and measurement; it does not replace scope review or authorize implementation.

Proposal: document on 1 November, close decisions and contracts at the start of the next work session, and implement/demonstrate on 2 November only if authorized and supported by the environment. If evidence is missing, publish the actual status and remaining work; do not label the demo complete.

## Review record

| Open item | Proposal to review | Status |
| --- | --- | --- |
| Essential scope | First-version table above | Pending |
| Real ACS versus mock | Prioritize real ACS with bounded investigation; record the blocker before switching to a mock | Effort limit and XML source to define |
| Resources and topology | Simple local environment; define node count and resources using available hardware | Pending |
| Correlation and patterns | Explainable rules and grouping/frequencies, initially without ML | Pending |
| Guarantees | Process failures and restart with persisted data, excluding storage loss | Pending |
| Quantitative acceptance | Tentative parameters in the validation plan | Pending |
| Internship reference | Obtain and read `alma-internship.md` | Pending |
| Implementation authorization | Explicit owner instruction after scope review | Not granted |

Approval record: **none yet**. When granted, record the date, supporting message/PR, approved documentation revision, and outstanding changes.

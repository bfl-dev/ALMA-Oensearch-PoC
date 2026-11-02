# Formal project definition

**Status:** project definition approved on 1 November 2026 (America/Santiago). **Approval owner:** project owner. **Implementation:** not started; architecture, ADRs, contracts, and planning remain the next stages.

## Purpose

Build a demonstrable personal project that strengthens an ALMA 2027 internship application through evidence of design, failure recovery, and log-based incident investigation. The first delivery must be understandable from GitHub and reproducible in a bounded local environment.

Observability is initially limited to logs and the operational state of the pipeline. A complete metrics and tracing platform is outside the approved essential demo.

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

## Approved essential demo scope

No D-08 capabilities are removed: their first versions are kept small.

| Area | Approved first-version scope | Expected evidence |
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

Historical replay uses an available, controlled archive or retained dataset whose original occurrence identities can be preserved. It does not assume old logs remain on ACS machines or that ALMA currently retains raw XML archives. Replaying raw records, redelivering RabbitMQ backlog, and migrating existing Elasticsearch history are separate operations. Migration remains documentary research in this PoC.

## Extensions outside the approved essential scope

- Distributed clusters, high availability, and node-loss testing.
- More formats, sources, and operational scenarios; broader ACS integration after an initial mock.
- Anomaly detection, embeddings, machine learning, and process mining.
- Custom UI, external alerts, advanced SSO/RBAC, distributed metrics/traces, and remote deployment.
- An executed Elasticsearch migration: outside the requested scope and requiring an explicit change.

These extensions are not prerequisites for completing the essential demo.

## Approved guarantee boundaries

The goal is to recover events available in a persistent source or accepted by durable transport, within the agreed volume and outage window. The exact acceptance point and checkpoint advancement rule must be defined before implementation. End-to-end exactly-once delivery is not promised.

The demo must cover abrupt producer/adapter and consumer termination, broker restart with storage retained, and temporary OpenSearch unavailability. Volume destruction, physical disk loss, source deletion, and an unlimited backlog are outside the approved guarantee and must be disclosed in the delivery.

## Delivery before 3 November

The target is interpreted as **2 November 2026, America/Santiago**. The deadline requires prioritization and measurement; it does not replace scope review or authorize implementation.

Proposal: document on 1 November, close decisions and contracts at the start of the next work session, and implement/demonstrate on 2 November only if authorized and supported by the environment. If evidence is missing, publish the actual status and remaining work; do not label the demo complete.

## Review record

| Item | Scope or remaining decision | Status |
| --- | --- | --- |
| Essential scope | First-version table above | Approved |
| Real ACS versus mock | Prioritize real ACS with bounded investigation; record the blocker before switching to a mock | Approach approved; effort limit and XML source still to define |
| Resources and topology | Simple local environment; define node count and resources using available hardware | Local scope approved; topology and resources pending |
| Correlation and patterns | Explainable rules and grouping/frequencies, initially without ML | Initial scope approved |
| Guarantees | Process failures and restart with persisted data, excluding storage loss | Boundaries approved; exact acceptance/checkpoint contracts pending |
| Quantitative acceptance | Tentative parameters in the validation plan | Pending detailed agreement |
| Internship reference | Attached `alma-internship.md` is now available and has been read | Initial source review complete; detailed migration assessment pending |
| Next stage | Evaluate architecture/ADRs, define contracts, then organize implementation work | Design and planning next; no implementation started |

### Approval record

- Date: **1 November 2026, America/Santiago**.
- Evidence: the project owner's explicit message in this conversation: **"i approve the project definition"**.
- Approved baseline: `docs/project-definition.md` as presented from repository revision `ce8f9ac8a8cbf7e2d9913149a9c42b44b03ff70a` in [PR #1](https://github.com/bfl-dev/ALMA-Oensearch-PoC/pull/1), with the historical-replay source clarification discussed immediately before approval.
- Effect: the essential scope, extension boundaries, and guarantee boundaries are approved. Continue with the agreed design and planning sequence without reopening those scope choices.
- Still open: exact topology/resources, ACS investigation limit/source, detailed recovery and identity design in ADR-0002, component contracts, and tentative quantitative acceptance targets. Scope approval does not mark these technical details approved or complete.
- Execution status: this update records approval and source clarification only; it does not merge the PR, create runtime infrastructure, or execute implementation agents.

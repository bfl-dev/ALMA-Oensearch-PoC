# Formal project definition

**Status:** project definition approved on 1 November 2026 (America/Santiago). **Approval owner:** project owner. **Architecture:** conceptual C4 approved on 3 November 2026 (America/Santiago). **Technical design:** accepted at revision `d5d82cf`. **Implementation:** initial code under review; live acceptance pending. The dated approval entries below preserve the decision history.

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

## Original delivery target and current status

The original before-3-November target meant **2 November 2026, America/Santiago**. It has elapsed. The initial implementation is now under review; measured runtime acceptance evidence remains pending. No replacement completion date is invented; establish a realistic schedule from the reviewed design and resource preflight.

## Review record

This table preserves the pre-acceptance design review. The later technical-design acceptance entry supersedes its pending decisions. Current execution status is in the [implementation evidence](evidence/implementation.md).

| Item | Scope or remaining decision | Status |
| --- | --- | --- |
| Essential scope | First-version table above | Approved |
| Real ACS versus mock | Prioritize real ACS with bounded investigation; record the blocker before switching to a mock | Two-hour investigation ceiling approved on 3 November 2026; component/XML source still to establish |
| Resources and topology | Simple local environment; define node count and resources using available hardware | Temporary host confirmed on 3 November 2026: i5-11300H, 16 GB total RAM, 10 GB project storage. Docker Compose accepted; future main PC specifications and detailed deployment pending |
| Correlation and patterns | Explainable rules and grouping/frequencies, initially without ML | Initial scope approved |
| Guarantees | Process failures and restart with persisted data, excluding storage loss | Boundaries approved; exact acceptance/checkpoint contracts pending |
| Quantitative acceptance | Tentative parameters in the validation plan | Pending detailed agreement |
| Internship reference | Attached `alma-internship.md` is now available and has been read | Initial source review complete; detailed migration assessment pending |
| Architecture | Conceptual C4 context and logical containers | Approved on 3 November 2026; detailed choices remain open |
| Next stage | Resolve detailed architecture questions/ADRs, define contracts, then organize implementation work | Design and planning next; no implementation started |

### Approval record

- Date: **1 November 2026, America/Santiago**.
- Evidence: the project owner's explicit message in this conversation: **"i approve the project definition"**.
- Approved baseline: `docs/project-definition.md` as presented from repository revision `ce8f9ac8a8cbf7e2d9913149a9c42b44b03ff70a` in [PR #1](https://github.com/bfl-dev/ALMA-Oensearch-PoC/pull/1), with the historical-replay source clarification discussed immediately before approval.
- Effect: the essential scope, extension boundaries, and guarantee boundaries are approved. Continue with the agreed design and planning sequence without reopening those scope choices.
- Still open: exact topology/resources, ACS investigation limit/source, detailed recovery and identity design in ADR-0002, component contracts, and tentative quantitative acceptance targets. Scope approval does not mark these technical details approved or complete.
- Execution status: this update records approval and source clarification only; it does not merge the PR, create runtime infrastructure, or execute implementation agents.

### Architecture approval follow-up

- Date: **3 November 2026, America/Santiago**.
- Evidence: the owner's message: **"i approve the architecture, but need to explain me the questions to answer"**.
- Baseline: conceptual C4 context and logical-container views in `docs/architecture/README.md` at revision `5e28f390edba5881269471d1cfd2e1401e56f322`.
- Effect: approve the component responsibilities and logical connections. The remaining engineering questions are explained in the architecture document; their candidate answers are recommendations, not newly approved decisions.
- Still open: ACS integration/time budget, detailed identity and recovery rules in ADR-0002, processing/storage tools, index policy, deployment versions/resources, contracts, and quantitative validation targets. This approval does not authorize implementation or merge PR #1.

### Host and ACS investigation follow-up

- Date: **3 November 2026, America/Santiago**.
- Owner confirmed the current machine as the demo host: Intel Core i5-11300H, 16 GB total RAM, and 10 GB available project storage. Native execution or Docker on this machine is acceptable.
- The owner accepted the proposed **two-hour maximum ACS feasibility investigation**. It may conclude earlier; record the outcome and blocker before invoking the already approved mock fallback.
- These constraints supersede the previously open host and investigation-budget items. Exact versions, allocation, real ACS source, contracts, and validation targets remain open. See the [architecture execution constraints](architecture/README.md#execution-constraints-confirmed-on-3-november-2026).

### Temporary host and packaging clarification

- Date: **3 November 2026, America/Santiago**.
- The owner clarified that the current machine is temporary and a more powerful main PC will be used when available. Its specifications are pending; the current 16 GB RAM / 10 GB storage allowance is not a permanent project limit.
- The owner accepted **Docker Compose** as the deployment approach. Exact versions, resource allocations, and configuration remain engineering details.
- The documentation baseline may be merged with those details explicitly open. Merging this definition PR does not approve every candidate technical answer or authorize implementation; detailed decisions, contracts, planning, and implementation authorization follow in the agreed sequence.

### Technical-design preparation

- Date: **3 November 2026, America/Santiago**.
- Owner instruction: **"go ahead"**, following the proposed DOC-03 investigation and technical-design/contracts PR sequence.
- Effect: authorize research and a reviewable documentation proposal; no runtime implementation, ACS installation, container pulls, or agent execution inferred.
- Research outcome: [DOC-03](research/acs-feasibility.md) now includes a public-browser follow-up: Confluence and ACS registry metadata are verified; modern schema/runtime and installed footprint remain unverified. Prefer a vetted sanitized export when available; use the XML mock immediately while no corpus exists, with a future main-PC logging-client experiment. This is a technical proposal, not runtime authorization or evidence of ACS incompatibility.
- Proposed next baseline: ADR-0002/0003, CT-01 through CT-04, candidate versions/resources, and acceptance parameters. See the [review guide](review/technical-design.md) and [task specifications](planning/implementation-tasks.md).
- Status: research findings documented; technical decisions/contracts await review. Prior scope/C4/Compose approvals remain intact. Runtime acceptance is unexecuted.

### Technical-design acceptance and implementation authorization

- Date: **3 November 2026, America/Santiago**.
- Owner instruction: **"accepted, now proceed with the implementation"**.
- Accepted baseline: PR #2 head `d5d82cf5b6490efbeebf691e8ec9630407c05e5f`, merged as `6a7804cdbe12041f8f38770ed9247591664d68ea`.
- Scope: ADR-0002/0003, CT-01 through CT-04, source admission/fallback, version/resource candidates and acceptance parameters; implement the essential demo and tests.
- Runtime results remain evidence to obtain. Current execution cannot access the Docker daemon and shell network; neither restriction changes the accepted guarantees.

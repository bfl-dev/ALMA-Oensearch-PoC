# Architecture: approved conceptual C4 views and pending detailed design

**Status:** conceptual C4 architecture approved by the owner on 3 November 2026 (America/Santiago); detailed engineering choices remain open. This does not represent an implemented architecture or ALMA's current infrastructure. [ADR-0001](../adr/0001-project-constraints.md) records owner constraints; [ADR-0002](../adr/0002-recovery-and-event-identity.md) proposes how to evaluate them.

## C4 level 1 — System context

| Element | C4 type | Responsibility and boundary |
| --- | --- | --- |
| Reviewer/developer | Person | Search logs, investigate incidents, and inspect evidence |
| Observability PoC | System under design | Transport, process, store, and analyze logs |
| ACS ONLINE source | External system | Identified real component or mock producing XML |
| Simulated OFFLINE application/API | External system | Produce reproducible operational and failure events |
| Historical files | External input resource | Identified immutable corpus available for replay |

ALMA production systems and operations are not part of this execution context.

## C4 level 2 — Approved logical containers

C4 containers represent execution/data units. This diagram does not require a separate process for every function or impose a physical topology. Adapters and replay can share one tool.

```mermaid
flowchart TD
    online["External source: ACS ONLINE real component or XML mock"]
    offline["External source: OFFLINE web/API simulator"]
    history["External input: historical files"]
    reviewer["Person: reviewer or developer"]
    subgraph poc["System: observability PoC"]
        adapters["Source adapters and historical ingestion"]
        sourceState[("Persistent state: identity and checkpoints (SQLite proposed)")]
        broker[("RabbitMQ: persistent transport")]
        worker["Processor and indexer"]
        quarantine[("Durable quarantine: SQLite proposed")]
        search[("OpenSearch: events and results")]
        dashboard["OpenSearch Dashboards: search and visualization"]
        analysis["Analysis: incidents, correlation, and patterns"]
        adapters <-->|"Progress and identity"| sourceState
        adapters -->|"Events and publisher confirms"| broker
        broker <-->|"Delivery and processing acknowledgments"| worker
        worker -->|"Indexing and per-event result"| search
        worker -->|"Unprocessable inputs and reason"| quarantine
        dashboard -->|"Queries"| search
        analysis <-->|"Queries and source events"| search
    end
    online -->|"XML"| adapters
    offline -->|"Application logs"| adapters
    history -->|"Replay with original identity"| adapters
    reviewer -->|"Investigate"| dashboard
    reviewer -->|"Run analysis"| analysis
```

The detailed-design proposal places payload normalization in a Python worker, keeps captured raw records on a persistent source volume, uses SQLite for checkpoints/quarantine, and runs analysis on demand. See [ADR-0003](../adr/0003-tools-and-local-deployment.md) and [CT-01 through CT-04](../contracts/README.md). Those technology/configuration details remain proposed; the conceptual C4 responsibilities are approved. OFFLINE goes through RabbitMQ by this PoC's design decision, not as a claim about the historical system.

## Level 3 and deployment

Level 4 is not required. Add level 3 only if it clarifies adapter/indexer internal responsibilities. A later deployment view will fix nodes, volumes, ports, resources, versions, and local exposure. The proposed demo does not require Kubernetes or multiple hosts.

## Execution constraints confirmed on 3 November 2026

Owner-provided constraints, not independently measured hardware:

| Item | Confirmed constraint |
| --- | --- |
| Host | Temporary development/demo host: the owner's current machine. A more powerful main PC is planned; its specifications are not yet recorded |
| CPU | Intel Core i5-11300H |
| Memory | 16 GB total host RAM, shared with the operating system and other applications |
| Storage | Up to 10 GB available for this project on the temporary host |
| Packaging | Docker Compose accepted by the owner on 3 November 2026; use the same approach on the future main PC |
| ACS investigation | At most two hours to assess a minimal real ACS producer/capture path; finish earlier if feasibility or a blocker becomes clear |

The two-hour limit is an investigation ceiling, not a duration estimate or a guarantee of real integration. Record the ACS release, candidate source, dependencies, estimated footprint, and outcome. If blocked at the limit or clearly incompatible with the resource budget earlier, document the reason and use the already approved XML mock fallback. Selecting a mock does not establish real ACS integration.

### Accepted packaging and proposed local deployment budget

The owner accepted Docker Compose as the packaging approach on 3 November 2026. The proposed service split is separate containers for OpenSearch, Dashboards, RabbitMQ, and the small project processes as needed. These services share the host's CPU, RAM, and disk; a container does not supply additional capacity. Exact versions, resource allocations, and service configuration remain detailed design work. No runtime configuration is introduced by this document.

The current hardware budget is temporary, not the project's permanent capacity ceiling. Keep paths, volumes, and resource settings configurable for the future main PC. On that host, record its specifications and repeat resource/capacity measurements; do not assume larger topology or high availability merely because more hardware is available.

- Start with one OpenSearch node and one RabbitMQ instance, persistent project volumes, and small bounded datasets. This is a restart/recovery demo, not a high-availability deployment.
- Target an initial combined memory budget of approximately 6–8 GB for the PoC, leaving room for the host and other applications. This is an engineering estimate to validate, not measured usage or an approved performance target. Set OpenSearch heap separately from its total process/container memory.
- Treat 10 GB as the full incremental project storage budget: downloaded/unpacked images, build cache, any ACS checkout/dependencies, raw data, broker/quarantine storage, indexes, runtime logs, and evidence. Images and build artifacts may be the limiting factor.
- Before installation, estimate the selected versions' complete footprint and verify actual free space in the runtime and volume filesystems. Keep growth headroom within the project budget; if the footprint does not fit, revise packaging or defer the real ACS environment before downloading/building it. Do not delete unrelated host data or promise that the complete stack fits before measurement.
- Bound source generation, backlog, quarantine, and runtime log growth. When capacity is reached, stop/pause production or ingestion with a visible reason while retaining recoverable records; do not silently discard accepted events.
- Pin compatible OpenSearch/Dashboards and RabbitMQ versions after the footprint review. Record deployment checks and peak usage in the [validation plan](../validation.md).

Packaging guidance: [official OpenSearch Docker documentation](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/), reviewed on 3 November 2026. It documents single-node deployment, Compose, persistent volumes, and explicit resource configuration; it does not certify this project's proposed budget.

## Detailed-design answers proposed for review

The component layout is approved; these new technical answers are proposals, not implicit owner decisions. [DOC-03](../research/acs-feasibility.md) records the research evidence and limitations.

| Earlier question | Proposed answer | Authoritative detail |
| --- | --- | --- |
| Real ACS or mock? | Prefer reviewed sanitized export if available; mock immediately without a corpus; main-PC logging-client test after capacity preflight | DOC-03 and ADR-0003 |
| Occurrence identity? | Persisted generation UUID plus contiguous sequence, independent of body/time/path | CT-01 and ADR-0002 |
| Checkpoint/acknowledgment timing? | Routable durable broker confirm before source progress; indexed or committed quarantine disposition before consumer ack | CT-02/CT-03 |
| Processing tool? | One small Python codebase instead of adding Logstash for this demo | ADR-0003 |
| Raw/quarantine persistence? | Retained capture corpus and idempotent worker SQLite quarantine | CT-01/CT-03 |
| Destination index? | Concrete poc-events-v1 throughout the retained run; no rollover/deletion during replay | CT-03 |
| Nodes/versions/resources? | One OpenSearch, one RabbitMQ, matching Dashboards; candidate release pins and configurable bounds | ADR-0003; runtime footprint verification pending |
| Small analysis? | One synthetic incident, bounded identifier rules, and versioned message-template grouping; output JSON reports | CT-04 |

Remaining review items are explicit in the [technical-design review guide](../review/technical-design.md). No runnable infrastructure is included.

### How the supplied ACS investigation informs the next stage

See [S-05](../references/README.md#s-05--supplied-acs-documentation-investigation). The report is documentary research; its underlying links were not independently revalidated in this update.

- It identifies XML archives and `acsXmlFileStore` as possible integration boundaries, with AMQP/Kafka handlers to investigate. Their presence in documentation does not establish active production configuration.
- It warns that `LogId` describes a class/type of event rather than proving a globally unique occurrence ID. The independent identity contract remains necessary.
- It reports TAI timestamps in the manual. CT-01 must preserve the original timestamp and time scale and define validated conversion for time-based searches; do not silently assume UTC.
- Its broader migration/production questions are a research checklist, not additional prerequisites for this personal demo. Current ALMA versions, deployment, and retention remain unverified.

### Approval record

- Owner message: **"i approve the architecture, but need to explain me the questions to answer"**.
- Date: **3 November 2026, America/Santiago**.
- Approved baseline: this document's conceptual C4 views at revision `5e28f390edba5881269471d1cfd2e1401e56f322`.
- Detailed recommendations above, ADR-0002, contracts, deployment values, and quantitative targets remain open. Implementation has not started.

## Relationship to the historical reference

Inspiration is limited to source separation, centralization, and decoupling through messaging. The adaptation to OpenSearch, identity contracts, and this demo's guarantees are project-specific decisions. The documentary mapping is in [references](../references/README.md).

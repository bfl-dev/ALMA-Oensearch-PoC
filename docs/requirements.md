# Requirements and acceptance criteria

**Status:** detailed acceptance baseline proposed for technical-design review. Requirements derive from the approved scope/owner decisions; exact contracts and quantitative targets await review. No scenario is an executed result.

## Functional requirements

| ID | Requirement | Decision | Acceptance |
| --- | --- | --- | --- |
| RF-01 | Ingest XML from real ACS or a documented mock, preserving original content and provenance | D-03 | CA-01 |
| RF-02 | Ingest OFFLINE logs from a simulated application/API | D-03 | CA-01 |
| RF-03 | Support continuous ingestion and historical replay through persistent RabbitMQ messaging | D-04, D-05 | CA-02, CA-04 |
| RF-04 | Normalize events while preserving the distinction between event time and processing time | D-05, D-08 | CA-01, CA-07 |
| RF-05 | Search and visualize by time range, source, severity, component, and text | D-08 | CA-06 |
| RF-06 | Reconstruct an incident with context and references to original events | D-08 | CA-07 |
| RF-07 | Produce automatic correlations with a rule, version, evidence, and explanation | D-08 | CA-08 |
| RF-08 | Discover message patterns through grouping, frequencies, and examples | D-08 | CA-09 |
| RF-09 | Research Elasticsearch → OpenSearch migration through documentation without executing it | D-01 | CA-10 |

## Quality requirements

| ID | Requirement | Decision | Acceptance |
| --- | --- | --- | --- |
| RC-01 | Recover processing after abrupt failures within the agreed failure model | D-06 | CA-03, CA-04 |
| RC-02 | Preserve backlog during temporary OpenSearch unavailability and drain it after recovery | D-06 | CA-04 |
| RC-03 | Avoid duplicates caused by redelivery, retry, or replay of the same event | D-07 | CA-02, CA-03, CA-05 |
| RC-04 | Preserve two legitimate occurrences even when their XML, message, and timestamp match | D-07 | CA-05 |
| RC-05 | Isolate invalid inputs and permanent indexing errors without silent loss or indefinite blocking of valid events | D-06 | CA-11 |
| RC-06 | Make the demo reproducible and measurable in a documented local environment | Delivery goal | CA-12 |

## Proposed acceptance scenarios

### CA-01 — Two sources and normalization

Given a corpus with a manifest of expected ONLINE and OFFLINE identities, when it is processed, each valid event retains its source, identity, original time, ingestion time, severity, component, message, and reference to original content. Queries retrieve the expected identities from both sources. Missing optional fields are represented explicitly; ACS values are not invented.

### CA-02 — Replay with overlap

Given a file with stable identity participating in continuous ingestion, when it is reread twice including previously published records, the final event set and count match expectations. Changing the path of the same file while preserving its file identity does not create new occurrences. The retention/target-index policy must support this property throughout the supported window.

### CA-03 — Failures at confirmation boundaries

When an adapter is terminated abruptly before and after receiving broker confirmation, its checkpoint does not cause loss after restart. When the consumer fails before indexing, or after indexing but before acknowledging the message, restart converges to the same expected set. Include a lost indexing response to simulate an uncertain outcome. If the destination is acknowledged before the event is durably persisted, the scenario fails.

### CA-04 — Temporary OpenSearch outage and broker restart

During the agreed outage, backlog is preserved and processes follow a bounded waiting/retry policy. After OpenSearch is restored, every accepted valid event appears once and backlog drains within the agreed threshold. In a separate scenario, restarting RabbitMQ with pending messages and retained volumes produces the same result. Evidence identifies which events had been durably accepted.

### CA-05 — Legitimate repetition versus technical duplication

Given two distinct ACS occurrences with identical XML and timestamps, when each is delivered several times and the file is subsequently reprocessed, exactly two events remain. The same occurrence retains its identity across continuous execution, restart, and replay. The oracle uses source coordinates/a manifest, not a body hash as occurrence equivalence.

### CA-06 — Search and visualization

The reviewer runs documented queries by time, source, severity, component, and text, finds a known event, and observes at least one time-based visualization and one distribution by source/severity. Queries and exportable evidence are retained; a screenshot alone does not prove counts.

### CA-07 — Incident reconstruction

Given a synthetic incident with a known timeline and late events, the investigation retrieves its context, orders events by event time with a documented tie-breaker, and distinguishes observations from hypotheses. References allow inspection of original logs. Temporal proximity is not treated as proven causality.

### CA-08 — Explainable correlation

A versioned rule links the expected events and returns their identities, satisfied conditions, and a readable explanation. A negative case with nearby events from another operation is not linked. If ACS identifiers are missing, the output identifies the inference and its limits. The demonstration discloses any artificial relationship between sources.

### CA-09 — Pattern discovery

A corpus includes messages from the same family with variable parameters and another distinct message. Analysis returns groups, a template or grouping criterion, frequencies, and examples; it detects the recurring family without merging or deleting its events. Normalization and limitations are documented. Model training is not required.

### CA-10 — Migration research

A report identifies the versions considered, APIs/clients, mappings, queries, visualizations, security/plugins, data transfer, and relevant risks. Each conclusion distinguishes reviewed documentation, assumptions, and pending validation. It does not claim an executed migration or assume ALMA's current Elasticsearch version.

### CA-11 — Invalid records and partial failures

A batch mixes valid records, invalid XML, and a permanent indexing rejection. Valid events are eventually indexed; invalid inputs remain in inspectable quarantine storage with source, reason, and identity/reference for correction and replay. Acknowledgment allows removal of the original message only after a durable disposition. Evaluate results for each item, including a partially successful batch.

### CA-12 — Reproducible demo and honest evidence

A reviewer follows instructions from a clean environment with declared prerequisites and obtains the agreed results. The report records the commit, versions, hardware, configuration, corpus, counts, timings, and limitations. Any unexecuted criterion is marked pending; no high-availability or operational-scale claims are made without evidence.

Load, timing, and retention parameters are proposed in the [validation plan](validation.md); they must be approved and fixed before tests are executed. The detailed implementation boundaries are in [CT-01 through CT-04](contracts/README.md). In v1, time-based incident/correlation acceptance uses declared UTC synthetic records; TAI/unknown records retain original time with a null UTC projection and an explicit status, pending a verified real-source conversion policy.

# Implementation task specifications

**Status:** proposed, issue-ready task descriptions; no execution assigned. All runtime tasks remain blocked on technical-design/acceptance review and explicit implementation authorization. Branches follow the accepted type convention. Each task must cite the approved design commit before work starts.

## Dependency order

`IMP-01` precedes `IMP-02`, then `IMP-03`, then `IMP-04`. `VAL-01` and `IMP-05` follow `IMP-04`; `IMP-06` follows `IMP-05`. `DOC-06` can run after version selection without runtime infrastructure. `DEM-01` requires validation, analysis, and migration research. No task is complete merely because its PR exists.

## IMP-01 — Reproducible local environment and capacity preflight

- Branch: `build/local-compose-environment`; milestone: M1.
- Dependencies: accepted ADR-0003/contracts/validation targets and explicit runtime authorization.
- Scope: Compose packaging, selected versions/digests, local secret example, health checks, persistent project volumes, resource/log limits, setup/stop/reset instructions. Resolve exact Engine/Compose/SQLite versions and transitive dependency lock. Do not introduce application sources or full ACS installation.
- Traceability: RC-06, CA-12, ADR-0003, CT-02/CT-03.
- Acceptance: declare the actual host; verify image availability/complete footprint before installing; fit the 10 GB total budget with headroom or report a blocker; record peak resources and version/digest inventory; loopback exposure; health queries succeed; restart retains broker/state/index data; destructive reset is explicit and separate.
- Evidence: reviewed setup commands, actual memory/disk measurements, index/queue properties, and limits. Existing unrelated volumes/data must not be pruned to make the budget fit.

## IMP-02 — Synthetic sources, capture corpus, and independent oracle

- Branch: `feature/synthetic-log-sources`; milestone: M1; depends on IMP-01.
- Scope: XML mock, small OFFLINE API simulator, durable capture/manifests, deterministic 1,000-valid-occurrence corpus per family, separate invalid fixtures and incident/negative cases. Disclose synthetic source mode and any cross-source identifier link. No claim of real ACS integration.
- Traceability: RF-01/RF-02/RF-04, RC-04, CA-01/CA-05/CA-07, CT-01.
- Acceptance: valid/invalid XML and JSON, Unicode, CDATA, multiline/duplicate Data, valid UTC plus unsupported-time examples; equal XML/timestamps at different coordinates; durable identity allocation and partial-append recovery; bounded source output; independently authored expected coordinates/dispositions. Contract examples are a seed, not the complete 2,000-event corpus.
- Evidence: manifest and expected sets created before pipeline processing; source provenance and capture boundary documented.

## IMP-03 — Stable source identity, checkpoints, publication, and replay

- Branch: `feature/durable-ingestion-and-replay`; milestone: M1; depends on IMP-02.
- Scope: envelope/schema validation (including Draft-07 meta-validation and positive/negative envelopes), byte/digest/coordinate checks, SQLite progress, mandatory persistent publication with confirms, independent replay cursor, capacity/backpressure status. Do not implement indexing in this task.
- Traceability: RF-03, RC-01/RC-03, CA-02/CA-03/CA-04, CT-01/CT-02, ADR-0002.
- Acceptance: preserve identity across rename/copy with manifests and replay; different generation for independent identical input; never advance on unroutable/rejected/uncertain publish; crash around checkpoint/confirm remains recoverable; unknown version/digest mismatch fails closed; source remains retained; queue limits reject new publication without evicting older accepted events.
- Evidence: checkpoint/confirm fault cases and source/broker reconciliation. Maintain broker heartbeats during backoff.

## IMP-04 — Normalization, per-item indexing, retries, and SQLite quarantine

- Branch: `feature/idempotent-indexing`; milestone: M1; depends on IMP-03.
- Scope: CT-03 deterministic projection, strict index mappings, manual acknowledgments, bounded bulk/retry, idempotent SQLite quarantine and inspection/export. Do not add dashboards or ML.
- Traceability: RF-04, RC-01 through RC-05, CA-01 through CA-05/CA-11, CT-03, ADR-0002.
- Acceptance: handle partial success/lost responses; create with stable ID/index; compare actual stored content on conflict; mismatch pauses without overwrite; data errors commit quarantine before ack; system/auth errors do not quarantine every record; repeated invalid occurrence yields one quarantine entry; capacity/storage failure leaves delivery recoverable; raw input and time-scale status retained.
- Evidence: mixed-batch expected sets, per-item results, collision negative case, and commit-before-ack fault evidence. Tests must exercise behavior rather than merely compare helper output with itself.

## VAL-01 — Failure/replay verification and OpenSearch evaluation

- Branch: `test/pipeline-recovery-evidence`; milestone: M1; depends on IMP-04.
- Scope: automate meaningful acceptance scenarios and retain a concise run report. Test both adapter/consumer abrupt termination, response loss, broker restart, outage, replay/repetition, quarantine restart, and capacity pressure. No feature expansion.
- Traceability: RC-01 through RC-06, CA-01 through CA-05/CA-11/CA-12; [validation matrix](../validation.md).
- Acceptance: exact identity/multiplicity/content/disposition matches the independent oracle; zero missing accepted valid events and zero extra copies; outage 60 s and drain within proposed 120 s after restoration once targets approved; records peak footprint, ingestion throughput/lag, query timings, configuration problems and limits. Failing targets stay failed; do not silently lower load/criteria.
- Evidence: machine/commit/configuration/corpus, fault points, raw counts/identity exports, timings and artifacts. Repeat baseline measurements on the main PC as a separate environment.

## IMP-05 and IMP-06 — Investigation views and explainable analysis

- Branches: `feature/log-investigation` then `feature/explainable-analysis`; milestone: M1.
- Dependencies: IMP-05 on IMP-04; IMP-06 on IMP-05. Can share a PR if review remains manageable.
- Scope: known-event/time/source/severity/text queries; two small Dashboards views; incident timeline including a late arrival; one or two deterministic CT-04 rules and message-template grouping. No custom UI or learned model.
- Traceability: RF-05 through RF-08, CA-06 through CA-09, CT-04.
- Acceptance: explicit one-materialization query scope, deterministic time/ID order, unsupported-time records visible separately, synthetic relationships disclosed, nearby unrelated operation excluded, rule versions/conditions/explanations retained, repeated family plus singleton group, contract token rules verified with examples, source events unchanged.
- Evidence: exportable queries/results/saved objects and analysis report, supporting original IDs, negative cases, and stated causal/grouping limitations.

## DOC-06 — Documentary migration assessment

- Branch: `docs/elasticsearch-migration-assessment`; milestone: M1; depends on candidate versions from ADR-0003.
- Scope: sourced matrix for versions/distributions, client/API compatibility, mappings, queries, saved objects, security/plugins, raw replay versus indexed-history transfer, rollback questions, and future laboratory tests. Do not execute a migration or invent ALMA's source version.
- Traceability: RF-09, CA-10, S-01/S-02/S-05.
- Acceptance: each conclusion separates primary-source facts, assumptions and unverified items; no blanket snapshot/client/dashboard compatibility claims; explicitly states what cannot be assessed without the source inventory.
- Evidence: precise sources and dates, comparison scope, and remaining experiments.

## DEM-01 — Reviewable delivery

- Branch: `docs/demo-evidence`; milestone: M1; depends on VAL-01, IMP-06, DOC-06.
- Scope: short README walkthrough, reproducible evidence index, optional short video, measured OpenSearch evaluation, and honest capability/limitation table.
- Traceability: CA-01 through CA-12.
- Acceptance: a reviewer can reproduce the agreed demo; reported results link to their commit/configuration/evidence; missing results stay pending. Original before-3-November target is recorded as elapsed, not met. A new completion date requires a new agreed schedule rather than backdating work.

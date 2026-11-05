# DOC-06 — Documentary Elasticsearch → OpenSearch assessment

**Reviewed:** 3 November 2026. **Scope:** preparation for a possible migration, not an executed migration or certification of ALMA's environment. PoC destination candidate: OpenSearch/Dashboards 3.9.0. ALMA's current source Elasticsearch distribution/version, creation versions of its indexes, plugins, deployment, retention and saved-object inventory are unknown.

The 2018 paper is historical context. Newer ACS documentation describes source/export behavior, not a current inventory of the search cluster. A raw XML import demonstrates source handling; it does not migrate existing indexed history, security state or dashboards.

## Compatibility and evidence matrix

| Area | Documented fact or evaluation boundary | Assessment / future test |
| --- | --- | --- |
| Engine/index versions | Snapshot, cluster and index-creation compatibility are separate. Elastic requires compatible versions even within Elasticsearch; OpenSearch documents different upgrade/migration routes [R1, R2] | Unknown source versions prevent selecting a direct restore route to 3.9.0. Obtain exact inventories before proposing hops or a tool version |
| Transfer choices | OpenSearch lists snapshot/restore, remote reindex and migration tooling; applicability is version-specific [R1] | Compare a bounded representative transfer with ID/content reconciliation. Do not claim that any Elasticsearch snapshot restores directly to OpenSearch 3.x |
| Migration Assistant | The current compatibility/feature tables must be consulted for the exact source/target. Automatic migration has limits, including saved objects and auto-generated ID replay behavior [R3] | Treat it as a research candidate, not an extra Kubernetes/AWS dependency for this local PoC. Record the tool release and supported route before a lab experiment |
| APIs and clients | opensearch-py 3.x documents OpenSearch 3.x compatibility [R4]; this is not compatibility of arbitrary Elasticsearch clients or extensions | Inventory actual clients, typed endpoints, authentication, Bulk/error semantics and queries. Run representative client calls against a disposable target |
| Mappings/settings | Source analyzers, types, dynamic templates, ingest transforms, routing, aliases and lifecycle policies are not supplied | Export sanitized metadata. Compare supported fields/analyzers and explicit defaults. The PoC's strict v1 mapping is a new model, not a migrated mapping |
| Queries/results | Supported syntax alone does not establish equivalent analyzer behavior, time conversion, aggregations or relevance | Preserve known query inputs and expected results; compare counts, IDs, time windows, aggregations and latency on the same bounded dataset |
| Saved objects | Dashboards supports saved-object import/export and reference resolution; successful import still needs correct index patterns and supported visualization types [R5] | Inventory Kibana version/features and export a representative set. Treat Lens/Canvas/plugin-specific objects and security tenants separately; the new PoC dashboard proves no migration compatibility |
| Security/plugins | No actual ALMA IdP, roles, plugin versions, licenses or secrets were accessed | Compare documented target capabilities with an approved requirement inventory. Local demo TLS/password settings are not corporate SSO or authorization validation |
| Retention/cutover | Current data volumes, source retention, restore tests and rollback requirements are unknown | Define preservation, backfill/live overlap, reconciliation and rollback before cutover. RabbitMQ redelivery, raw replay and indexed-history migration are different operations |

## What this implementation can evidence

The PoC can exercise OpenSearch ingestion/indexing/querying, explicit IDs, outage recovery, source preservation, and inspection/analysis of a synthetic corpus. Its current runtime verification status is in the implementation evidence report. Those outcomes are relevant engineering preparation, but do not establish migration feasibility for an unseen source deployment.

The smallest useful future migration experiment would record a specific source engine/index-creation version and target version, transfer a sanitized representative dataset through one documented supported route, preserve IDs and original content, compare expected queries/aggregations, assess client/saved-object differences, and document rollback boundaries. No source cluster or such experiment was created for this report.

## Primary references

- R1: [OpenSearch upgrade/migration guidance](https://docs.opensearch.org/latest/upgrade-or-migrate/).
- R2: [Elastic snapshot compatibility](https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore). Its Elasticsearch rules are not cross-product compatibility certification.
- R3: [Migration Assistant applicability and compatibility](https://docs.opensearch.org/latest/migration-assistant/is-migration-assistant-right-for-you/). Latest guidance is dated evidence, not a frozen tool release.
- R4: [opensearch-py 3.2.0 compatibility matrix](https://github.com/opensearch-project/opensearch-py/blob/v3.2.0/COMPATIBILITY.md).
- R5: [Dashboards saved objects](https://docs.opensearch.org/latest/dashboards/management/saved-objects/) and [Saved Objects APIs](https://docs.opensearch.org/latest/dashboards/management/saved-objects-api/).

No configuration, production data, credentials or unsupported compatibility claims are inferred from these references. This satisfies the documentary deliverable's initial scope; selecting and validating an ALMA migration route remains dependent on the missing inventory.

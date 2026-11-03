# References and evidence boundaries

Initial documentary review: 1 November 2026. Reference inventory updated: 3 November 2026. Distinguish owner instructions, reviewed sources, and pending documents.

## S-01 — Historical ALMA publication

Gil, J. P.; Miranda, N.; Garcés, M.; Avarias, J. **Current Status of Software Log Analysis at ALMA Observatory**. Software and Cyberinfrastructure for Astronomy V, 2018. DOI: [10.1117/12.2314247](https://doi.org/10.1117/12.2314247).

- Requested reference: `Current_Status_of_Software_Log_Analysis_at_ALMA_Observatory1.pdf`.
- Status: the exact requested PDF is now available as a project attachment. Its relevant logging, storage, and ingestion passages were read directly. The public publication text [uploaded by one of its authors](https://www.researchgate.net/publication/326236739_Current_status_of_software_log_analysis_at_ALMA_Observatory) was reviewed earlier; binary identity between the two copies was not checked.
- Scope: historical evidence from 2018; does not establish current infrastructure or procedures.

Brief mapping to the project:

| Section | Observation from the paper | Use in this PoC |
| --- | --- | --- |
| 2.1 and 3.2 | ACS/XML, the `alogging2mq` bridge, RabbitMQ, Logstash, and Elasticsearch/Kibana | Inspiration for decoupling ingestion and investigation; OpenSearch is the owner's choice |
| 2.3 and 3.3 | OFFLINE web/API sources and Filebeat for centralization | Motivates representing two families; both use RabbitMQ here by project decision |
| 4 and 5 | Exploration, process analysis, and analytical tools | Motivates incident investigation and explainable analysis; does not require reproducing their implementations |

The owner added [the paper PDF](Current_Status_of_Software_Log_Analysis_at_ALMA_Observatory1-1.pdf) to this branch. Its presence was checked on 3 November 2026; this update did not re-extract the PDF or compare binary copies. The project's MIT license does not extend to third-party publications.

## S-02 — Internship description

- Requested reference: `alma-internship.md`.
- Status: **available as a project attachment and read directly**. The attached text identifies the Software Team / Front Line Software Support Engineers (FLSSE) internship.
- The description covers analysis of existing Elasticsearch infrastructure, OpenSearch study and migration research, and a small OpenSearch cluster PoC evaluating deployment, ingestion, indexing, querying, monitoring, and integration. This supports the project's general direction; the owner-defined reliability and analysis requirements remain project choices.
- The attachment is a supplied copy of the posting, not access to ALMA's operational environment. Detailed source/version verification and the migration assessment remain pending. No inferred replacement file was created.

## S-03 — RabbitMQ confirmations

[Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms), official documentation, reviewed on 1 November 2026.

Publisher confirms and consumer acknowledgments cover different stages. Used to inform recovery questions in ADR-0002; not evidence of an implemented configuration. Check against the version selected later.

## S-04 — OpenSearch bulk indexing

[Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/), official documentation, reviewed on 1 November 2026.

Bulk operations are processed independently and results are reported per item. Used to require partial-error analysis. The `latest` link does not pin the project's version; that choice is pending.

## S-05 — Supplied ACS documentation investigation

- File: [documentation-investigation.md](documentation-investigation.md), added by the owner and read from repository revision `5e28f390edba5881269471d1cfd2e1401e56f322` on 3 November 2026.
- Report date: 30 October 2026. It describes a review of 34 public ICTACS pages, distinguishing documented statements, historical/proposed designs, inferences, and unverified information.
- Relevant leads: XML structure and time semantics; logging channels; `acsXmlFileStore` and optional AMQP/Kafka handlers; identity limitations; and open migration questions.
- Evidence boundary: this is a supplied research report, not a schema, a runtime integration test, or proof of ALMA's current production architecture. Its underlying source links were not independently revalidated in this update. Confirm the target ACS release, schema/IDL, samples, and delivery semantics before finalizing CT-01.
- The source report is retained in its original Spanish as supplied evidence. Project-authored decisions and summaries remain in English.

## Pending migration research

The next stage will produce a brief matrix covering versions, APIs/clients, mappings, queries, dashboards, security/plugins, and data transfer, with official sources. No current ALMA versions have been verified and no migration results exist in this repository.

## S-06 — ACS source review for DOC-03

Reviewed on 3 November 2026: public [ACS community checkout](https://github.com/ACS-Community/ACS/tree/e7fd9ce9ac6502dfdf840e920150585867504362), pinned to the historical ACS-OCT2017 revision. Formatter, parser tests, loggingMI.xsd, XmlFileStoreLoggerImpl, and QueueFileHandler were read directly; exact links and findings are in [DOC-03](../research/acs-feasibility.md).

This source proves historical code/schema availability, not today's ALMA release or an executed integration. Current GitLab/Confluence access was unsuccessful here. Historical namespace differences are documented rather than silently reconciled.

## S-07 — Community container candidates

Reviewed the [ACS Docker recipe](https://github.com/ACS-Community/ACS-Docker-Image/blob/9df3cbd1901147bfc929e2cf2d996060dc392e81/Dockerfile) at pinned revision 9df3cbd1901147bfc929e2cf2d996060dc392e81, its README, and the publisher's [acs](https://hub.docker.com/r/acscommunity/acs) / [acsdev](https://hub.docker.com/r/acscommunity/acsdev) pages. The recipe targets CentOS 7 / ACS 2020AUG; acsdev advertises stream9.2025apr.

Displayed image sizes are unverified publisher-page metadata. No full image, build dependency set, digest, unpacked footprint, startup path, or known-message export was verified. No image was downloaded. See DOC-03 for the resulting mock-first recommendation and conditions to reopen real ACS.

## S-08 — Tooling and persistence guidance

Primary documentation reviewed on 3 November 2026:

- RabbitMQ [queues](https://www.rabbitmq.com/docs/queues), [confirms](https://www.rabbitmq.com/docs/confirms), [overflow](https://www.rabbitmq.com/docs/maxlength), and [dead lettering](https://www.rabbitmq.com/docs/dlx): distinct persistence/confirmation stages, bounded queue behavior, and why a default overflow/DLX configuration is not the proposed no-silent-loss policy.
- Elastic [RabbitMQ input](https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-rabbitmq) and [persistent queues](https://www.elastic.co/docs/reference/logstash/persistent-queues): configuration and recovery boundaries for the tooling comparison. No performance comparison was run.
- Python [sqlite3](https://docs.python.org/3.12/library/sqlite3.html) and SQLite [synchronous pragma](https://www.sqlite.org/pragma.html#pragma_synchronous): local transaction/durability mechanisms; not a claim that our future configuration has been tested.
- OpenSearch [Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/), [index settings](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/index-settings/), and [Docker deployment](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/): indexing, local deployment, and resource prerequisites. Latest documentation is dated reference evidence, not a version pin or footprint certification.

## S-09 — Candidate releases and clients

The primary release metadata linked in [ADR-0003](../adr/0003-tools-and-local-deployment.md) was reviewed on 3 November 2026 for OpenSearch/Dashboards 3.9.0, RabbitMQ 4.4.0, CPython 3.12.16, Pika 1.4.4, and opensearch-py 3.2.0. The [client matrix](https://github.com/opensearch-project/opensearch-py/blob/v3.2.0/COMPATIBILITY.md) supports the 3.x client/server pairing at a documented compatibility level.

Release existence and the matrix do not establish image digest/availability, transitive dependency resolution, local installation, complete footprint, or integration behavior. Those are IMP-01 checks before the runtime baseline can be called reproducible.

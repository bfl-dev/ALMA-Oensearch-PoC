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

The owner added [the paper PDF](Current_Status_of_Software_Log_Analysis_at_ALMA_Observatory1-1.pdf) to this branch. Its presence was checked on 3 November 2026; the browser follow-up re-read its logging/export sections by text extraction; binary copies were not compared. The project's MIT license does not extend to third-party publications.

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
- Evidence boundary: this is a supplied research report, not a schema, a runtime integration test, or proof of ALMA's current production architecture. Selected underlying links were independently reopened in the browser follow-up below (S-10); the original 34-page survey was not repeated. Confirm target release, schema/IDL, samples, and delivery semantics before real import.
- The source report is retained in its original Spanish as supplied evidence. Project-authored decisions and summaries remain in English.

## Pending migration research

The next stage will produce a brief matrix covering versions, APIs/clients, mappings, queries, dashboards, security/plugins, and data transfer, with official sources. No current ALMA versions have been verified and no migration results exist in this repository.

## S-06 — ACS source review for DOC-03

Reviewed on 3 November 2026: public [ACS community source](https://github.com/ACS-Community/ACS/tree/e7fd9ce9ac6502dfdf840e920150585867504362), pinned to the historical ACS-OCT2017 revision. Formatter, parser tests, loggingMI.xsd, XmlFileStoreLoggerImpl, and QueueFileHandler were read directly; exact links and findings are in [DOC-03](../research/acs-feasibility.md).

This source proves historical code/schema availability, not today's ALMA release or an executed integration. The initial pass could not access GitLab/Confluence; S-10 supersedes that access assessment. The follow-up also inspected the pinned loggingClient.cpp, file-store test CDB/prologue, TimestampedStringQueue, QueueFile, and IsoDateFormat. Historical namespace, encoding, clock and LogId differences are documented rather than silently reconciled; no current-release schema was obtained.

## S-07 — Community container candidates

Reviewed the [ACS Docker recipe](https://github.com/ACS-Community/ACS-Docker-Image/blob/9df3cbd1901147bfc929e2cf2d996060dc392e81/Dockerfile) at pinned revision 9df3cbd1901147bfc929e2cf2d996060dc392e81, its README, and the publisher's [acs](https://hub.docker.com/r/acscommunity/acs) / [acsdev](https://hub.docker.com/r/acscommunity/acsdev) pages. The recipe targets CentOS 7 / ACS 2020AUG; acsdev advertises stream9.2025apr.

The browser follow-up verified tag/platform/index and manifest digest metadata and explicitly compressed sizes; see S-10 and DOC-03. Actual unpacked/peak storage, startup behavior and known-message export remain unexecuted. No image was downloaded. The legacy recipe is not evidence that the advertised 2025APR image was built from that revision.

## S-08 — Tooling and persistence guidance

Primary documentation reviewed on 3 November 2026:

- RabbitMQ [queues](https://www.rabbitmq.com/docs/queues), [confirms](https://www.rabbitmq.com/docs/confirms), [overflow](https://www.rabbitmq.com/docs/maxlength), and [dead lettering](https://www.rabbitmq.com/docs/dlx): distinct persistence/confirmation stages, bounded queue behavior, and why a default overflow/DLX configuration is not the proposed no-silent-loss policy.
- Elastic [RabbitMQ input](https://www.elastic.co/docs/reference/logstash/plugins/plugins-inputs-rabbitmq) and [persistent queues](https://www.elastic.co/docs/reference/logstash/persistent-queues): configuration and recovery boundaries for the tooling comparison. No performance comparison was run.
- Python [sqlite3](https://docs.python.org/3.12/library/sqlite3.html) and SQLite [synchronous pragma](https://www.sqlite.org/pragma.html#pragma_synchronous): local transaction/durability mechanisms; not a claim that our future configuration has been tested.
- OpenSearch [Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/), [index settings](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/index-settings/), and [Docker deployment](https://docs.opensearch.org/latest/install-and-configure/install-opensearch/docker/): indexing, local deployment, and resource prerequisites. Latest documentation is dated reference evidence, not a version pin or footprint certification.

## S-09 — Candidate releases and clients

The primary release metadata linked in [ADR-0003](../adr/0003-tools-and-local-deployment.md) was reviewed on 3 November 2026 for OpenSearch/Dashboards 3.9.0, RabbitMQ 4.4.0, CPython 3.12.16, Pika 1.4.4, and opensearch-py 3.2.0. The [client matrix](https://github.com/opensearch-project/opensearch-py/blob/v3.2.0/COMPATIBILITY.md) supports the 3.x client/server pairing at a documented compatibility level.

Release existence and the matrix do not establish image digest/availability, transitive dependency resolution, local installation, complete footprint, or integration behavior. Those are IMP-01 checks before the runtime baseline can be called reproducible.

## S-10 — Public browser follow-up for ACS feasibility

Access date: **2026-11-03**, America/Santiago. Browser used without login; the owner chose public sources only. [DOC-03](../research/acs-feasibility.md) contains the source inventory B01–B12 with page revisions/edit dates, exact image digests, historical source permalinks, findings, inferences and unexecuted checks.

| Primary reference | Revision/release and finding |
| --- | --- |
| [Logging manual](https://confluence.alma.cl/pages/viewpage.action?pageId=25790043) / [acsExtras](https://confluence.alma.cl/pages/viewpage.action?pageId=61367992) | v95 (2025-05-15) / v2 (2026-03-13): XML/API and managed XML-store purpose; not verified runtime configuration |
| [Notification Channel](https://confluence.alma.cl/pages/viewpage.action?pageId=50562416) / [ACE implementation](https://confluence.alma.cl/spaces/ICTACS/pages/118345196/ACS+Technical+Documents+-+Logging+System+-+C+ACE+Logger+Implementation) | v10 (2025-04-25) / v29 (2024-04-03): service roles, configuration and upstream reliability boundaries |
| [Retrieving ACS](https://confluence.alma.cl/spaces/ICTACS/pages/54004860/Retrieving+ACS) / [build guide](https://confluence.alma.cl/spaces/ICTACS/pages/54004895/Step-by-step+Compilation+and+Installation) | v5 (2021-09-27) / v10 (2025-04-24): source/release branch and ExtProd/build instructions; mixed-age examples |
| [RHEL9 installation](https://confluence.alma.cl/spaces/ICTACS/pages/240564943/ACS+Installation+-+RHEL9) / [requirements](https://confluence.alma.cl/spaces/ICTACS/pages/54005149/System+Requirements) | v4 (2025-09-09), last tested COMMON-2025OCT / v15 (2025-04-24): binaries gated; general 10 GB and 4 GB RAM guidance, not measured container footprint |
| [Cheat sheet](https://confluence.alma.cl/spaces/ICTACS/pages/98413896/ACS+Cheat+Sheet) / [2026OCT notes](https://confluence.alma.cl/spaces/ICTACS/pages/304317478/COMMON-2026OCT) | v21 (2026-06-16) / v6 (2026-09-29): headless startup lead and recent maintenance evidence |
| [Offline XML FAQ](https://confluence.alma.cl/pages/viewpage.action?pageId=54003112) | 2020 page with 2004 answer: logging-client export lead; historical, not an executed recipe |
| [acsdev tags](https://hub.docker.com/r/acscommunity/acsdev/tags) / [acs tags](https://hub.docker.com/r/acscommunity/acs/tags) | `stream9.2025apr`: 5.48 GB compressed, linux/amd64; legacy `2020.08.0-centos7`: 1.29 GB; `2020.08.0`/`latest`: 1.72 GB. Exact platform/index digests in DOC-03; no installed-size measurement. |

The supplied [GitLab group](https://asw.alma.cl/groups/ASW) failed with a browser HTTP/2 protocol error. The documented [Bitbucket source URL](https://bitbucket.alma.cl/scm/asw/acs.git) reached a login page; no authentication attempted. The [manual-linked ESO schema index](https://www.eso.org/projects/alma/develop/acs/OnlineDocs/ACS_docs/schemas/index.html) returned 404. Restricted release archives were only identified in the installation guide. These outcomes are access observations, not claims that ALMA sources or current schemas do not exist.

Reassessed recommendation: a sanitized, release-identified real export is preferable when obtainable; the immediate temporary-host source remains a documented mock because no corpus is available and total storage fit is unproven. A future authorized main-PC test should try the Python logger plus logging client before LogsXmlStore. No verified current deployment, installation, integration or runtime resource result is claimed.

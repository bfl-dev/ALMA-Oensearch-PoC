# References and evidence boundaries

Documentary review: 1 November 2026. Distinguish owner instructions, reviewed sources, and pending documents.

## S-01 — Historical ALMA publication

Gil, J. P.; Miranda, N.; Garcés, M.; Avarias, J. **Current Status of Software Log Analysis at ALMA Observatory**. Software and Cyberinfrastructure for Astronomy V, 2018. DOI: [10.1117/12.2314247](https://doi.org/10.1117/12.2314247).

- Requested reference: `Current_Status_of_Software_Log_Analysis_at_ALMA_Observatory1.pdf`.
- Status: the exact file was not found in the available resources. The public publication text [uploaded by one of its authors](https://www.researchgate.net/publication/326236739_Current_status_of_software_log_analysis_at_ALMA_Observatory) was reviewed. Binary identity with the requested PDF was not checked.
- Scope: historical evidence from 2018; does not establish current infrastructure or procedures.

Brief mapping to the project:

| Section | Observation from the paper | Use in this PoC |
| --- | --- | --- |
| 2.1 and 3.2 | ACS/XML, the `alogging2mq` bridge, RabbitMQ, Logstash, and Elasticsearch/Kibana | Inspiration for decoupling ingestion and investigation; OpenSearch is the owner's choice |
| 2.3 and 3.3 | OFFLINE web/API sources and Filebeat for centralization | Motivates representing two families; both use RabbitMQ here by project decision |
| 4 and 5 | Exploration, process analysis, and analytical tools | Motivates incident investigation and explainable analysis; does not require reproducing their implementations |

The paper was not copied into the repository. The project's MIT license does not extend to these publications.

## S-02 — Internship description

- Requested reference: `alma-internship.md`.
- Status: **pending retrieval and review**. It is not in the initial repository and was not found under that name among the available files.
- No file of the same name was created with inferred content. Statements from earlier conversations do not replace the original document.
- Pending: posting source and date, role/team, exact content, and verifiable relationship to scope. Until then, no official ALMA requirements are attributed to this reference.

## S-03 — RabbitMQ confirmations

[Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms), official documentation, reviewed on 1 November 2026.

Publisher confirms and consumer acknowledgments cover different stages. Used to inform recovery questions in ADR-0002; not evidence of an implemented configuration. Check against the version selected later.

## S-04 — OpenSearch bulk indexing

[Bulk API](https://docs.opensearch.org/latest/api-reference/document-apis/bulk/), official documentation, reviewed on 1 November 2026.

Bulk operations are processed independently and results are reported per item. Used to require partial-error analysis. The `latest` link does not pin the project's version; that choice is pending.

## Pending migration research

The next stage will produce a brief matrix covering versions, APIs/clients, mappings, queries, dashboards, security/plugins, and data transfer, with official sources. No current ALMA versions have been verified and no migration results exist in this repository.

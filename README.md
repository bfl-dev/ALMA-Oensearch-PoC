# ALMA OpenSearch Observability PoC

Personal project to demonstrate reliable log ingestion and incident investigation with OpenSearch, in preparation for an ALMA 2027 internship application.

**Status: M1 approved by the owner on 5 November 2026. Live acceptance and boundary runs passed on the owner's PC; dashboard/live view confirmed. Peak-resource, throughput and capture-to-search lag measurements were waived.**

This is an independent learning project. Its architectural inspiration is a historical ALMA publication; it does not describe or claim access to ALMA's current infrastructure.

## M1 demonstration

- Ingest ACS ONLINE XML logs and simulated OFFLINE web/API logs through persistent RabbitMQ messaging.
- Combine continuous ingestion and historical replay while preserving event identity.
- Recover from abrupt process failures and temporary OpenSearch outages without pipeline-generated duplicates or loss of legitimate repeated events.
- Search and visualize logs, reconstruct an incident, explain automatic correlations, and discover recurring message patterns.
- Document Elasticsearch-to-OpenSearch migration considerations without performing a migration.

The Python implementation includes synthetic sources, durable capture, confirmed publication, replay, deterministic indexing/quarantine, queries, saved dashboard objects and analysis. The owner approved the live acceptance report and reported passing collision/capacity checks. Sources are synthetic; real ACS follow-up is separately scoped. See the [runbook](docs/running.md) and [evidence record](docs/evidence/implementation.md).

## Documentation

Start at the [documentation index](docs/README.md), then review the [project scope](docs/project-definition.md) and [requirements](docs/requirements.md).

| Topic | Document |
| --- | --- |
| Purpose, boundaries, essential demo and extensions | [Project definition](docs/project-definition.md) |
| Requirements and acceptance scenarios | [Requirements](docs/requirements.md) |
| C4 views and architecture questions | [Architecture](docs/architecture/README.md) |
| Architecture decision records | [ADR index](docs/adr/README.md) |
| Component boundaries and event identity | [Contracts](docs/contracts/README.md) |
| Failure tests and demo evidence | [Validation plan](docs/validation.md) |
| Milestones, dependencies and agent tasks | [Delivery plan](docs/planning/README.md) |
| Historical paper and internship reference | [References](docs/references/README.md) |
| Real ACS feasibility and initial source recommendation | [DOC-03](docs/research/acs-feasibility.md) |

English is the working language for documentation, diagrams, templates, issues, pull requests, and commit messages. The repository URL retains its original spelling, `ALMA-Oensearch-PoC`.

## Run and validate

Use a local Linux/amd64 Docker Engine with Compose, Python 3, uv and network access. Preflight enforces the temporary host's 10 GB project disk allowance and 7.25 GiB available-memory requirement. It stops if fit cannot be established.

```sh
make test
make config
make preflight
make build
python3 scripts/acceptance.py
```

The acceptance runner needs an empty isolated Compose project. Read the [runbook](docs/running.md) first. Preflight generates private credentials, digest references and a hashed dependency lock; no package/image substitution occurs. The live runs were performed on the owner's PC.

For interactive use after setup: `make up`, `make corpus`, `make verify`, `make queries`, `make analyze`, then `python3 scripts/import_dashboards.py`. Dashboards binds to <http://127.0.0.1:5601>. `make down` retains volumes. Do not publish the generated `.env`.

The original 2 November 2026 target elapsed. M1 was accepted on 5 November with the [recorded evidence and measurement waiver](docs/evidence/m1-review.md). The i5-11300H/16 GB host is temporary; a future main PC requires new preflight measurements. See the [documentary migration assessment](docs/research/elasticsearch-migration.md).

## License

[MIT](LICENSE). Referenced third-party publications retain their own rights.

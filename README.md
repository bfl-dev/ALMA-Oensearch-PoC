# ALMA OpenSearch Observability PoC

Personal project to demonstrate reliable log ingestion and incident investigation with OpenSearch, in preparation for an ALMA 2027 internship application.

**Status: project definition approved; architecture and contracts are next. No application code or runnable demo exists yet.**

This is an independent learning project. Its architectural inspiration is a historical ALMA publication; it does not describe or claim access to ALMA's current infrastructure.

## Intended demonstration

- Ingest ACS ONLINE XML logs and simulated OFFLINE web/API logs through persistent RabbitMQ messaging.
- Combine continuous ingestion and historical replay while preserving event identity.
- Recover from abrupt process failures and temporary OpenSearch outages without pipeline-generated duplicates or loss of legitimate repeated events.
- Search and visualize logs, reconstruct an incident, explain automatic correlations, and discover recurring message patterns.
- Document Elasticsearch-to-OpenSearch migration considerations without performing a migration.

These are project goals, **not implemented capabilities**. The essential demo scope is approved; detailed architecture, contracts, and quantitative acceptance targets remain to be finalized.

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

English is the working language for documentation, diagrams, templates, issues, pull requests, and commit messages. The repository URL retains its original spelling, `ALMA-Oensearch-PoC`.

## Target and next gate

Target: a presentable GitHub demonstration **before 3 November 2026**, interpreted as completion by 2 November in `America/Santiago`. This is a planning target, not a delivery guarantee.

The owner approved the project definition on 1 November 2026 (America/Santiago). Next: evaluate the C4 views and ADRs, finalize component contracts and acceptance parameters, and organize implementation work. See the [approval record](docs/project-definition.md#approval-record) and [agent guidance](AGENTS.md).

## License

[MIT](LICENSE). Referenced third-party publications retain their own rights.

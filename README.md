# ALMA OpenSearch Observability PoC

Personal project to demonstrate reliable log ingestion and incident investigation with OpenSearch, in preparation for an ALMA 2027 internship application.

**Status: scope and conceptual C4 approved; technical design and contracts proposed for review. No application code or runnable demo exists yet.**

This is an independent learning project. Its architectural inspiration is a historical ALMA publication; it does not describe or claim access to ALMA's current infrastructure.

## Intended demonstration

- Ingest ACS ONLINE XML logs and simulated OFFLINE web/API logs through persistent RabbitMQ messaging.
- Combine continuous ingestion and historical replay while preserving event identity.
- Recover from abrupt process failures and temporary OpenSearch outages without pipeline-generated duplicates or loss of legitimate repeated events.
- Search and visualize logs, reconstruct an incident, explain automatic correlations, and discover recurring message patterns.
- Document Elasticsearch-to-OpenSearch migration considerations without performing a migration.

These are project goals, **not implemented capabilities**. Scope, conceptual C4, and Docker Compose are approved. [ACS feasibility](docs/research/acs-feasibility.md), [detailed decisions](docs/adr/README.md), and [contracts](docs/contracts/README.md) now provide concrete proposals for review.

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

## Target and next gate

The original target was a presentable demo before 3 November 2026 (completion by 2 November, America/Santiago). That target has elapsed; no runnable demo has been delivered and no replacement date is promised here.

The next gate is review of the proposed tooling/source fallback, recovery/identity rules, CT-01 through CT-04, and measurable acceptance parameters. [Issue-ready tasks](docs/planning/implementation-tasks.md) prepare implementation after that review and explicit runtime authorization.

The temporary host has an i5-11300H, 16 GB total RAM, and a 10 GB project storage allowance. Docker Compose is accepted; a more powerful main PC is planned. Resource limits are configurable proposals, not permanent project ceilings or measured performance. See [architecture](docs/architecture/README.md).

## License

[MIT](LICENSE). Referenced third-party publications retain their own rights.

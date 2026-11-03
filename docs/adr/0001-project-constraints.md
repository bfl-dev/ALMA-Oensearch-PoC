# ADR-0001 — Owner constraints and decisions

- Status: owner decisions received on 1 November 2026
- Origin: opening instructions for this work; D-01 through D-08 in the [project definition](../project-definition.md)
- Scope: records existing choices; does not approve the complete design or start implementation

## Context and decision

The project seeks presentable evidence of observability for a personal application. OpenSearch is the primary destination and RabbitMQ the persistent intermediary. It includes ONLINE ACS/XML and simulated OFFLINE sources, continuous and historical ingestion, failure recovery, preservation of legitimate repetition, and explainable analysis.

Elasticsearch → OpenSearch migration will be researched through documentation. ALMA's published historical architecture is an inspiration, without assuming it remains current. Scope must be reviewed with the owner before implementation.

## Options and boundaries

Engine and broker choices are not reopened in this ADR: the owner has resolved them. Versions, topology, processing tools, and contracts remain open. There is no evidence that this design replicates ALMA's current infrastructure.

## Consequences and validation

The demo must show both reliable event handling and its usefulness for incident investigation. The deadline requires a small first version of each capability and clearly separated extensions. Acceptance will be established by reviewing [requirements](../requirements.md) and [validation](../validation.md).

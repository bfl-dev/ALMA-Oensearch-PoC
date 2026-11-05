# Repository working instructions

## Status and authorization

The owner explicitly accepted the technical design at revision `d5d82cf5b6490efbeebf691e8ec9630407c05e5f` and authorized implementation on 3 November 2026 (America/Santiago): "accepted, now proceed with the implementation". PR #2 is merged. ADR-0002/0003, CT-01 through CT-04, and their acceptance parameters form the accepted implementation baseline.

- Implement the essential demo and meaningful tests; record actual evidence and remaining runtime blockers.
- Preserve the real-export admission gate and use synthetic sources until a vetted corpus is available.
- The host is temporary: 16 GB total RAM, 10 GB project storage allowance; Docker Compose is accepted. Do not delete unrelated data or disable disk safety thresholds to meet this budget.
- Do not delegate to agents without explicit authorization. Current authorization is for implementation, not agent delegation.
- The authorization supersedes earlier documentation-only restrictions. Merging implementation PRs still requires review; do not claim runtime acceptance from unit tests or configuration validation.

## M1 acceptance

The owner accepted M1 on 5 November 2026 against PR #12 head `61892f2`, following the approved main acceptance report and owner-reported passing boundary/UI checks. See `docs/evidence/m1-review.md`. Peak memory/storage, throughput and capture-to-search lag measurements were explicitly waived for M1. Preserve these evidence limits in future reports. M2 work requires separately agreed scope.

## Documentation and delivery

- Use English for repository documentation, diagrams, templates, issues, PR titles and descriptions, and commit messages. Preserve proper names, source filenames, and established identifiers.
- Name branches `<type>/<kebab-case-description>` according to the change: `feature/`, `docs/`, `fix/`, `refactor/`, `test/`, `chore/`, `ci/`, or `build/`. See `docs/development-workflow.md` for the corresponding PR title types.
- The M1 delivery uses PR #11 and PR #12 (`feature/live-cascade-logging`). Future branches and PR titles follow their actual change type.
- Distinguish owner decisions, proposals, and verified evidence.
- Keep contract changes traceable; do not silently weaken accepted failure or identity guarantees.
- Read CT-01 through CT-04 and ADR-0002/0003 before implementation; do not invent an interface or assume documentary pins were integration-tested.
- Link requirements, ADRs, contracts, and evidence through their identifiers.
- Do not describe goals or pending tests as achieved results.
- Do not present the 2018 paper as evidence of ALMA's current infrastructure.
- Do not use a message hash, timestamp, or redelivery flag as the sole identity of an event.
- Do not publish ALMA operational data, credentials, or content from unverified references.
- Preserve `LICENSE` and content outside the change.

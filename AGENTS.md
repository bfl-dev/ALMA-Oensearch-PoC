# Repository working instructions

## Status and authorization

The project is in the definition phase. The owner requested a scope review before implementation. Only documentation, research, and planning are currently authorized.

- Do not create application code, simulators, runnable infrastructure, containers, dependencies, CI, or software tests until the owner authorizes implementation of the reviewed scope.
- Do not delegate execution to agents without the owner's authorization. Task documents are preparation, not execution instructions.
- Record scope approval in `docs/project-definition.md` when an explicit instruction is given. The existence or merge of a documentation PR is not sufficient to infer approval.
- If a later instruction from the owner authorizes work, that instruction takes precedence; update the documentation status accordingly.

## Documentation and delivery

- Use English for repository documentation, diagrams, templates, issues, PR titles and descriptions, and commit messages. Preserve proper names, source filenames, and established identifiers.
- Name branches `<type>/<kebab-case-description>` according to the change: `feature/`, `docs/`, `fix/`, `refactor/`, `test/`, `chore/`, `ci/`, or `build/`. See `docs/development-workflow.md` for the corresponding PR title types.
- For this change, use `docs/project-definition` and a PR title of `docs: <outcome>`.
- Distinguish owner decisions, proposals, and verified evidence.
- Link requirements, ADRs, contracts, and evidence through their identifiers.
- Do not describe goals or pending tests as achieved results.
- Do not present the 2018 paper as evidence of ALMA's current infrastructure.
- Do not use a message hash, timestamp, or redelivery flag as the sole identity of an event.
- Do not publish ALMA operational data, credentials, or content from unverified references.
- Preserve `LICENSE` and content outside the change.

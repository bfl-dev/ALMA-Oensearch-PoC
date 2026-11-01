# Branch and pull request conventions

## Working language

The owner has chosen English for repository work. Write documentation, diagram labels, templates, issues, PR titles and descriptions, and commit messages in English. Preserve proper names, original source filenames, and established traceability identifiers.

## Branches

Owner decision: the prefix reflects the type of change. Format: `<type>/<kebab-case-description>`, lowercase, with a brief and specific description. Use English descriptions for consistency with the repository's working language.

| Prefix | Purpose | Example | PR title type |
| --- | --- | --- | --- |
| `feature/` | New capability | `feature/historical-replay` | `feat:` |
| `docs/` | Documentation and definition | `docs/project-definition` | `docs:` |
| `fix/` | Behavior correction | `fix/replay-event-identity` | `fix:` |
| `refactor/` | Reorganization without behavior changes | `refactor/event-normalization` | `refactor:` |
| `test/` | Tests and fixtures | `test/consumer-recovery` | `test:` |
| `chore/` | Maintenance and supporting tools | `chore/update-tooling` | `chore:` |
| `ci/` | Integration/delivery automation | `ci/documentation-checks` | `ci:` |
| `build/` | Build system, packaging, or dependencies | `build/pin-runtime-dependencies` | `build:` |

The PR title mapping is a proposed convention accompanying the branch standard; the owner explicitly requested type-based branch prefixes. For related changes of several types, choose the PR's main purpose. Separate unrelated changes. Do not create validators or CI to enforce this convention during the definition phase.

## Pull requests

Branch from `main` using the appropriate type, open a PR describing the outcome and validation, and link requirements/ADRs/contracts where applicable. The [template](../.github/pull_request_template.md) captures this information.

This documentation PR uses `docs/project-definition`. Documentation review does not authorize implementation: scope approval and authorization must be recorded explicitly as described in [AGENTS.md](../AGENTS.md).

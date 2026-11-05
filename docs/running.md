# Run the essential demo

The implementation follows accepted ADR-0002/0003 and CT-01 through CT-04. The [evidence record](evidence/implementation.md) distinguishes completed checks from pending live acceptance.

## Setup

Run from the repository root on Linux/amd64 with a local Docker Engine, Compose, Python 3, uv (`0.9.5` in CI), and registry/package network access. This implementation session cannot access the Docker socket. Remote daemons and Docker Desktop storage accounting are unverified.

```sh
make test
make config
python3 scripts/preflight.py --offline
make preflight
make build
```

Preflight requires 7.25 GiB available memory and `vm.max_map_count >= 262144`. It does not change host settings/permissions. It enforces the owner's 10 GB incremental project allowance with 2 GB reserve. Images, build cache, source, state, indexes, logs and reports count toward it. Compressed-size estimates are not installed sizes; growth is measured after each pull/build. Shared Docker storage/global changes limit attribution, so avoid concurrent builds. No prune occurs. If fit fails, preserve data and use the main PC or review allocations. A future host can explicitly change `--budget-gb`, `--headroom-gb` and `--min-memory-gib`; record allocations and measurements together.

Online preflight writes ignored `.env` (random credentials, mode 0600), `.env.images` (platform digests/source revision), `requirements.lock` (complete dependencies/hashes), and `artifacts/preflight.json`. Preserve the lock and digests with run evidence; do not publish credentials. Example env files validate syntax only. The image requires the resolved lock; no floating `latest` fallback is supplied.

`make test` uses host Python/stdlib. One Draft-07 test skips when `jsonschema` is absent; CI installs the pinned dependency. After build, `make schema` runs full schema/meta-schema and fixture validation.

OpenSearch uses its local test security configuration and self-signed certificate; local clients disable verification. Ports bind to loopback and the private Compose network. These settings are unsuitable for remote exposure. Do not share `.env` or expanded Docker configuration containing passwords.

## Live acceptance

```sh
python3 scripts/acceptance.py
```

Use an empty isolated project. Existing indexed events cause failure instead of deletion. A fresh shell `COMPOSE_PROJECT_NAME` selects separate volumes; use free loopback ports if another stack is running. Keep that environment for all commands and measure storage before retaining multiple stacks. Do not delete data to obtain a passing test.

The runner generates 1,000 valid occurrences per family plus invalid fixtures against an independent oracle. It exercises two replays, adapter-confirm/worker crash windows, lost bulk response, partial mapper rejection, broker restart with pending messages, and a 10 events/s source across a 60 s OpenSearch outage with 120 s convergence after restoration. Diagnostic reductions are explicitly marked as a different target profile. Passing the implemented runner does not by itself establish every CA-01 through CA-12 assertion.

Reports include `artifacts/acceptance.json`, `last-reconciliation.json`, `analysis.json`, redacted container logs and preflight/budget results. Check exact identity/multiplicity/raw content/disposition, not equal totals alone. Record runtime versions, immutable images, dependency lock hash and source revision. Actual peak sampling, full throughput/lag evaluation, live capacity/collision negative tests, and UI evidence remain required. The optional manual GitHub `live` workflow runs in a separate hosted environment; it cannot establish laptop resource fit.

## Live boundary checks

The owner has approved the main acceptance report. Run the remaining collision and capacity cases from the updated PR #12 branch after rebuilding the image:

```sh
git switch feature/live-cascade-logging
git pull --ff-only origin feature/live-cascade-logging
export SOURCE_REVISION="$(git rev-parse HEAD)"
make build
make boundary-checks
```

The boundary stack requires 5.125 GiB available memory. If the current demo consumes that headroom, stop its Compose project first with `make down` using its actual `COMPOSE_PROJECT_NAME`. Named volumes are retained. The runner selects its own fresh `alma-boundary-…` project and automatic loopback ports, starts OpenSearch/RabbitMQ only, and checks the existing project storage budget before and after the run.

| Case | Expected proof |
| --- | --- |
| Identity collision | A valid envelope with changed raw content under an existing ID raises `E_IDENTITY_COLLISION`, leaves the original indexed document intact, and retains the unacknowledged delivery in RabbitMQ. |
| Broker capacity | A test queue fits one envelope. Publishing the second is negatively confirmed, the checkpoint stays at sequence 1, and both source records remain. After consuming the accepted message, retry confirms the original second event and advances to sequence 2. |
| Quarantine capacity | A test-local SQLite logical budget fits one invalid event. A second raises `E_CAPACITY` and stays unacknowledged. Reopen the same database with more capacity, retry, and verify both raw envelopes are retained before the queue drains. |

The small test limits exercise the production declaration, publication, checkpoint and settlement code paths. Standard runtime limits remain 64 MiB. These controlled logical-capacity tests do not simulate a physical disk failure. The injected errors are expected assertions inside a passing test.

The final JSON prints `passed`, `project` and the unique `artifacts/boundaries/<run-id>/report.json` path. Inspect its three `cases` results and retained budget/version/configuration evidence. Each run has a new report directory, preserving the approved `acceptance.json` and budget report. The runner stops its own containers at the end and retains their volumes, including on failure. No UI stack is started. The new runner still needs a live host result before the M1 boundary gate can close.

## Interactive demo

```sh
make up
make corpus
make verify
make queries
make analyze
python3 scripts/import_dashboards.py
```

Ingestion is asynchronous; verify after the queue drains. Verification exits 1 for mismatches and exports `artifacts/reconciliation.json`; queries/analysis also export JSON. The importer writes to the **Global** security tenant and prints a direct `dashboard_url`. Open <http://127.0.0.1:5601/app/dashboards?security_tenant=global#/view/poc-overview> after signing in. A different tenant has a separate saved-object collection and may show no dashboard. The saved fixture window covers 3 November 2026; change the time picker for live traffic. The dashboard includes a time histogram and source/severity distribution; the saved search is imported as a separate object.

If the header loads but the dashboard area is blank, use the direct URL above and check the browser console. The panel definitions include a `version` for OpenSearch Dashboards 3.9.0: omitting it causes `migrations730` to log `Cannot read properties of null (reading 'version')`, even when the import API reports success. After updating the saved objects, rerun `python3 scripts/import_dashboards.py` and reload the direct URL. Successful import and query responses alone do not establish browser rendering; record UI evidence separately.

`make replay` creates an independent cursor over retained identities. A changed-content collision pauses instead of overwriting. Enable the optional API with:

```sh
docker compose --env-file .env --env-file .env.images --profile live up -d api
curl -X POST http://127.0.0.1:8080/operations -H 'Content-Type: application/json' -d '{"operation_id":"manual-17","request_id":"request-1","fail":false}'
```

The synthetic request log is captured before response. Normal requests return 202; `fail:true` simulates HTTP 500 while retaining the event. Capacity rejection returns 503. Manual events are absent from the fixed acceptance oracle: use a separate project for exploration. CLI help also documents finite `stream` generation with explicit `--oracle` extension.

Inspect quarantine:

```sh
docker compose --env-file .env --env-file .env.images run --rm tools quarantine --state /data/worker/quarantine.sqlite --output -
```

## Live log generation

After building the updated application image, run:

```sh
make live
make live RATE=10 DURATION=300 INCIDENT_RATE=0.2 SEED=17
make live SCENARIO=normal
```

Run one command at a time. The default is 10 events/s for 120 seconds, mixed scenarios, and a 10% probability of a cascade per operation when enough positions remain. The commands start the stack, create/reuse the fixed corpus and extend its independent oracle before live capture. Existing generation identities remain stable. A different `COMPOSE_PROJECT_NAME` selects a different project; preserve the same setting for all related commands and keep only one stack bound to the chosen ports.

Mixed mode randomly chooses receiver timeout, device unavailable or connection reset. Each complete seven-event cascade includes request acceptance, upstream error, processor retry/exhaustion, downstream operation failure, receiver reconnection and successful recovery. Events share an operation/request ID across ONLINE and OFFLINE and span `mock.api`, `mock.receiver`, `mock.processor` and `mock.pipeline`. Normal operations and final background events fill the rest of the exact requested event count. A cascade starts only when all seven slots fit. These are simulated dependencies defined by the scenario.

The generator prints its seed and up to five incident examples before capturing. Copy an operation ID into a Dashboards filter such as `correlation_keys.operation_id: "live-..."`, or use an example's `seed_id` with `analyze --seed`. Set the time range to Last 15 minutes and enable refresh. `SEED` repeats the scenario choices; each invocation gets new occurrence IDs and current scheduled UTC timestamps. The rate applies to total events across both families. Mixed mode requires both families and at least 0.1 events/s to fit a cascade inside the 60 s correlation window. Existing `stream` calls retain normal-mode defaults, including the acceptance runner.

Generation stops at `DURATION` or the 20,000-event / one-hour bounds. Press Ctrl+C to interrupt the foreground command. From a second terminal, stop its named source container with:

```sh
make live-stop
make verify
```

Use the same `COMPOSE_PROJECT_NAME` for stopping and verification. Accepted captures remain available to the adapter/worker. An interrupted or capacity-blocked plan retains the oracle's intended events, so verification reports `unproduced_expected` for events never captured. Review that separately from `missing_accepted_valid`. Completed streams should reconcile after the queue drains. The source budget remains 100 MiB and analysis remains bounded to 20,000 total indexed events across retained runs.

Update/rebuild example for a new checkout revision:

```sh
export SOURCE_REVISION="$(git rev-parse HEAD)"
make build
make live
```

For current M1 status and the evidence still needed, see the [acceptance checklist](evidence/m1-review.md).

## Persistence and limitations

`make down` stops containers and retains named volumes. Source, checkpoints, quarantine, broker and index survive restart. No reset/prune command is supplied. Volume deletion is a separate destructive action outside recovery guarantees. No automatic rollover/deletion occurs during the retained run.

Publication checkpoints advance after routable confirms. Consumer acknowledgments follow successful create/identical conflict or committed quarantine. Capacity, authentication, mapping drift and collisions pause without discarding accepted events. Inspect Compose status/logs; stop intake under storage pressure. Do not truncate capture, delete manifests, clear state or remove indexed documents during replay validation.

Capture readers expose only the synced commit watermark. Recovery can adopt complete pending frames and truncates incomplete tails before identity reuse. Real ACS export admission still requires release/framing/encoding/clock evidence. No authentic import or TAI conversion is implemented; TAI/unknown time retains its original value with null UTC and appears separately in analysis.

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

## Persistence and limitations

`make down` stops containers and retains named volumes. Source, checkpoints, quarantine, broker and index survive restart. No reset/prune command is supplied. Volume deletion is a separate destructive action outside recovery guarantees. No automatic rollover/deletion occurs during the retained run.

Publication checkpoints advance after routable confirms. Consumer acknowledgments follow successful create/identical conflict or committed quarantine. Capacity, authentication, mapping drift and collisions pause without discarding accepted events. Inspect Compose status/logs; stop intake under storage pressure. Do not truncate capture, delete manifests, clear state or remove indexed documents during replay validation.

Capture readers expose only the synced commit watermark. Recovery can adopt complete pending frames and truncates incomplete tails before identity reuse. Real ACS export admission still requires release/framing/encoding/clock evidence. No authentic import or TAI conversion is implemented; TAI/unknown time retains its original value with null UTC and appears separately in analysis.

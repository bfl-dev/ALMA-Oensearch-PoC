# Validation and demonstration

**Status:** proposed plan. No software tests have been executed and these capabilities have not been measured.

## Tentative parameters for review

The values below are proposed local acceptance targets, not observed performance or requirements attributed to ALMA. Adjust them once resources and versions are known, before execution.

| Parameter | Initial proposal |
| --- | --- |
| Deterministic corpus | 1,000 ONLINE and 1,000 OFFLINE occurrences, with an independent manifest |
| Legitimate repetition | Include at least one ACS pair with identical XML and timestamps but distinct coordinates |
| Historical data | Reprocess the corpus twice and include overlap with continuous reads |
| Continuous flow | 10 events/s in aggregate for 2 minutes, in a scenario separate from corpus counting |
| OpenSearch outage | 60 seconds during continuous execution |
| Recovery | Backlog drained within 120 seconds after restoration, with declared resources |
| Loss/duplication | Zero accepted valid events lost; zero additional copies per identity after convergence |
| Search | Correct reproducible queries; record timings without promising an SLO yet |
| Retention and replay | Explicitly define the supported window; do not test only against newly created indexes |

A failing scenario still fails even if the global total matches because losses and duplicates cancel each other out.

## Resource preflight and accounting

Confirmed host: i5-11300H, 16 GB total RAM, with a 10 GB project storage allowance; native or local Docker execution is acceptable. See the [execution constraints](architecture/README.md#execution-constraints-confirmed-on-3-november-2026) for the tentative deployment budget and two-hour ACS investigation ceiling.

Before future runtime setup, record available host memory, actual free space on the image/cache and volume filesystems, selected versions, image/dependency footprint estimates, and remaining growth headroom. The 10 GB allowance covers the entire project's incremental footprint, not just OpenSearch documents. Defer installation if it cannot fit.

During future runs, report total and peak memory/disk consumption, including images/build cache, source data, broker/quarantine state, indexes, and runtime logs. Verify bounded production/backpressure at capacity without deleting pending events. No capacity results exist yet.

## Oracle and evidence

The corpus manifest defines original occurrences and their coordinates before the pipeline. Compare identity sets, multiplicity, and content against that manifest; do not generate the oracle solely with the same identification function being validated.

Record separately: produced, available in persistent source storage, durably accepted by the broker, indexed, pending, quarantined, and retried. Dropped events cannot be hidden inside a processed counter.

Wait for the documented search-visibility condition and completion of retries before counting. An event recognized as already processed requires identity/content/destination validation according to the contract. Invalid inputs are counted in quarantine, not as valid indexed events.

## Minimum matrix

| Scenario | Criteria | Future evidence |
| --- | --- | --- |
| Two sources and controlled corpus | CA-01, CA-06 | Manifest, queries, and exported results |
| Replay and overlap | CA-02, CA-05 | Before/after sets, coordinates, and repetition cases |
| Adapter failure at confirmation boundary | CA-03 | Before/after checkpoints and identity reconciliation |
| Consumer failure and lost response | CA-03 | Failure point, redelivery, and final state |
| OpenSearch outage | CA-04 | Backlog/timing and reconciliation after recovery |
| RabbitMQ restart with pending messages | CA-04 | Durable state and post-restart results |
| Partially failed bulk and invalid record | CA-11 | Per-event results and recoverable quarantine |
| Incident with late events | CA-07, CA-08 | Timeline, explained rule, and negative case |
| Message patterns | CA-09 | Groups, frequencies, examples, and limits |
| Research and reproduction | CA-10, CA-12 | Report with sources and verified instructions |

Each run must identify the commit, versions, hardware, configuration and data, command/procedure used, expected/actual result, and evidence links. Scripts and tests will be written when implementation is authorized.

## Proposed presentation script

1. Explain the problem, historical inspiration, and independent project scope.
2. Show both sources, a known query, and visualizations.
3. Reconstruct the incident and justify the correlation using supporting events.
4. Show a recurring pattern with examples; distinguish analytical grouping from occurrence identity.
5. Interrupt OpenSearch, observe backlog, restore service, and verify recovery.
6. Reprocess historical data and show that legitimate repetition survives without technical duplicates.
7. Present abrupt-failure evidence, migration research, and pending limitations.

A video may summarize longer tests but must link reproducible evidence. A README listing goals is not an executed demo.

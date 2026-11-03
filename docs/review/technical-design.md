# Technical-design review guide

**Status:** concrete proposals ready for owner review; no runtime implementation authorized by this document. Branch: `docs/technical-design`. Baseline: merged definition at `fb5a4419317e9b60448b59f07b40061f7fe3cc0f`.

## What this PR adds

Read the [ACS feasibility report](../research/acs-feasibility.md), [ADR-0002](../adr/0002-recovery-and-event-identity.md), [ADR-0003](../adr/0003-tools-and-local-deployment.md), and [contract index](../contracts/README.md). The proposals turn approved component responsibilities into exact source/transport/indexing/analysis behavior, supported by a structural envelope schema and original synthetic examples.

| Decision to review | Proposed answer | Limitation/evidence |
| --- | --- | --- |
| Initial ONLINE source | Prefer vetted sanitized real export when available; mock immediately while no corpus exists; main-PC logging-client experiment later | Confluence, image digests/platforms/compressed sizes now verified; modern schema/runtime and total storage fit remain unverified |
| Processing and persistence | Python with SQLite checkpoint/quarantine stores | Clear boundaries, but reconnect/commit/ack behavior still needs tests; Logstash not claimed incapable |
| Occurrence/recovery model | Generation UUID + sequence; retained capture; confirmed publication; create/compare before consumer ack | At-least-once delivery with idempotent effects; no storage-loss or exactly-once claim |
| Destination and retention | Concrete poc-events-v1, one parser, retained run until explicit teardown | No rollover/deletion during replay; corrected materializations separately scoped |
| XML/time profile | Historical-format subset; declared UTC mock, TAI/unknown preserved with null UTC | Real-export gate covers byte/framing/encoding/clock evidence; no current ACS schema validation or TAI conversion |
| Versions and resources | OpenSearch/Dashboards 3.9.0, RabbitMQ 4.4.0, Python/client candidates and bounded Compose proposal | Release metadata reviewed; registry digests, full footprint and runtime compatibility checks pending setup |
| Acceptance | 2,000-valid-event corpus proposal, 60 s outage/120 s drain proposal plus concrete contract bounds and small analysis windows | No measurements or passing runtime scenarios yet |

## Readiness and follow-up

DOC-03 research is complete; DOC-04/05 remain proposed until this revision is explicitly accepted. [Task specifications](../planning/implementation-tasks.md) are prepared for future milestones/issues. No agent task has been assigned or executed.

After review, record any amendments and the accepted design commit, establish a realistic delivery schedule, and create the implementation milestones/issues. Runtime work then needs explicit owner authorization under [AGENTS.md](../../AGENTS.md). A PR merge alone does not assert that every proposal is approved or that setup/tests passed.

The current host is temporary. The main PC needs a recorded resource inventory and new preflight/measurement evidence, not a redesign of source identity. The original before-3-November goal has elapsed; this PR does not backdate or claim a demo delivery.

## Verification of this documentation

See [documentation checks](documentation-checks.md). Format/integrity checks support review of the proposal; they do not substitute for broker, SQLite, OpenSearch, parser, or recovery acceptance tests.

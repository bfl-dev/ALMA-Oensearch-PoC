# CT-04 — Investigation, explainable correlation, and patterns

**Status:** accepted by owner on 3 November 2026; runtime evidence tracked separately. RF-05 through RF-08; CA-06 through CA-09. Reads the CT-03 materialization without changing source events.

## Query boundary

Select exactly `poc-events-v1`. Use `event_time.utc` for time filters and a stable `(event_time.utc, event_id)` ascending timeline order. Unknown/invalid event-time records are explicitly listed separately with original time and reason; never silently substitute ingestion time. Tie-breaking by event ID is deterministic presentation order, not causal order. Use exact fields for source/severity/component and text search for message. Wait for documented search visibility before reconciliation.

Initial Dashboards evidence: one event-time histogram and one source/severity distribution, plus a known-event search. Preserve saved objects/query definitions and exportable results; screenshots supplement rather than replace exact counts. No custom UI is required.

## One synthetic incident and negative case

Propose a declared scenario: simulated API operation `op-17` triggers a synthetic ACS component action; request and ONLINE events explicitly carry that operation identifier. A timeout repeats twice, then recovery and API completion follow. Capture a late-arriving event whose original time belongs earlier in the timeline. A simultaneous unrelated operation `op-18` must not be linked. This cross-source relationship is artificial scenario design, not evidence about production ALMA identifiers.

The full deterministic corpus and expected identities will be created in IMP-02. The small [contract examples](examples/README.md) illustrate format/identity only; they are not the complete incident or 2,000-event acceptance corpus.

## Proposed rules

| Rule/version | Conditions | Interpretation |
| --- | --- | --- |
| `same-operation/1.0.0` | Non-null exact `operation_id`, same environment, valid UTC times within 60 seconds of the seed | Observed identifier match within a bounded window; not proof of causality |
| `same-stack/1.0.0` | ONLINE, same producer/environment, non-null exact `stack_id`, valid UTC times within 10 seconds of seed | Shared diagnostic stack context; no inferred cross-source relation |

Windows are inclusive absolute differences from an explicit seed event, not transitive chains that grow without bound. Rules do not match null IDs, merely similar text, or time proximity alone. Time-invalid records cannot receive time-window links. State synthetic provenance and missing identifiers. One rule suffices if the corpus does not support a meaningful stack case; the second must not be claimed without evidence.

Each correlation result contains `analysis_version`, rule ID/version, seed ID, sorted related IDs, materialization, window, matched values/conditions, classification (these initial rules use observed matches, with no inferred fallback), synthetic flag, and readable explanation/limitations. Empty/no-match output is valid evidence for the negative case. Repeated runs on the same materialization/settings return the same links.

## Pattern profile

Use `message-template/1.0.0`: collapse whitespace, replace UUID tokens with `<UUID>`, then standalone decimal integer tokens with `<N>`, in that order; do not remove arbitrary words or infer a model. Group by source family, component, severity, and resulting template. Use Python Unicode whitespace/word semantics: collapse whitespace with `\s+` and strip ends; UUID regex `(?i)(?<!\w)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?!\w)`; integer regex `(?<!\w)[0-9]+(?!\w)`. Replace each match with the literal marker, without any additional substitutions. Numeric substrings within word tokens remain unchanged. For `timeout after 10 ms` and `timeout after 20 ms`, expect template `timeout after <N> ms`; `connection restored` stays separate.

Return version, exact criterion/template, group key, count, time range if available, and up to five sorted example IDs with raw evidence references. A recurring group has count at least two; retain singleton groups. Source records are never merged/deleted. Explain that normalization can group semantically different messages and preserve inspectable examples. No ML, embeddings, anomaly model, or root-cause proof is claimed.

## Analysis output persistence

Initially write a versioned JSON report as a run artifact with source commit, materialization, rules, seed/window, query scope, and sorted results. This avoids creating another service or searchable result index. Record report-generation time separately from the deterministic result payload. Reports may be regenerated; they do not affect event identities/counts or index documents. File layout and reporting command are future implementation work.

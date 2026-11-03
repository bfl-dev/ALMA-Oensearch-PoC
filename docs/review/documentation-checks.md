# Documentation verification

Date: 3 November 2026. Scope: proposed technical-design documents and static synthetic examples, against merged baseline `fb5a4419317e9b60448b59f07b40061f7fe3cc0f`.

## Completed checks

- 97 relative Markdown links checked against the final/local plus baseline file inventory; no missing file targets.
- Five local heading-anchor links checked; no missing anchors. Markdown code fences are balanced.
- Six JSON files parsed: the envelope schema, valid/invalid OFFLINE payloads, envelope, normalized example, and occurrence oracle.
- Envelope raw bytes decode exactly to the XML sample; canonical base64, SHA-256, capture/record bounds, coordinate/ID relationship, and declared timestamp format were checked.
- The normalized example matches XML text, component, severity, Data order, original timestamp, stable ingestion timestamp, raw content, source coordinates, and operation identifier.
- Valid XML parses; intentionally incomplete XML fails parsing. Invalid OFFLINE JSON is syntactically valid and intentionally violates the payload profile.
- The five-occurrence oracle has five distinct IDs, three expected indexed records, and two expected quarantined records. Two legitimate ONLINE occurrences share identical raw bytes/hash but have different coordinates and IDs. These are example expectations, not observed pipeline results.
- The pinned historical loggingMI.xsd rejects the original unqualified XML example and accepts a namespace-qualified projection. This verifies a documented namespace distinction, not compatibility with today's ACS release.
- Change inventory is confined to documentation/instructions and static contract data. No application code, Compose configuration, dependency manifest, CI, or application tests are included. Supplied research report, PDF, and repository license are unchanged.

## Explicitly unexecuted checks

A full Draft-07 JSON Schema validator is unavailable in the local checking environment. JSON syntax and explicit sample/field invariants were checked; this is not a claim of complete schema-meta-validation or execution against a generic validator. IMP-03 must validate the schema and positive/negative envelopes with its selected validator.

Mermaid was not rendered; the existing C4 code fence and changed labels were inspected structurally. No runtime source/parser service, broker, SQLite checkpoint/quarantine, OpenSearch, image footprint, restart, or performance test was executed. Candidate software versions were researched, not installed.

The checking scripts and pinned reference-XSD bytes were temporary verification aids, not application deliverables or copied third-party repository content. Runtime acceptance remains tracked separately in the validation plan and issue-ready tasks.

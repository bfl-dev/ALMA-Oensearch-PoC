# CT-01 — Source capture and event envelope v1

**Status:** accepted by owner on 3 November 2026; runtime evidence tracked separately. RF-01 through RF-04, RC-03/RC-04, CA-01/CA-02/CA-05. A project profile, not an ACS standard or verified integration.

## Capture and identity

Input is an append-only UTF-8 NDJSON capture file: one complete [envelope](schemas/event-envelope-v1.schema.json) per physical line. XML can contain newlines/CDATA because raw bytes are base64-encoded inside the envelope. This framing is ours, not a claim about native ACS files.

A retained generation manifest fixes source family/producer/environment, provenance, raw format, clock, and a lowercase canonical UUID `generation_id` before writing. Persist it atomically and sync the parent directory. Sequence numbers are contiguous positive integers from 1, even for malformed payloads. Identity is exactly:

`urn:alma-poc:event:v1:<generation_id>:<sequence>`

Use a decimal sequence without leading zeroes. A frame is accepted only after newline/data sync. The implementation also atomically syncs a `committed.json` sequence/prefix watermark before exposing it to readers. Recovery can adopt complete pending frames after syncing them; incomplete tails remain unaccepted. `captured_at` is assigned once at first durable project capture and retained on retry/replay. Resume by scanning complete records; unfinished trailing appends were not accepted. Never reuse an accepted sequence.

At most 65,536 decoded raw bytes and 131,072 serialized UTF-8 envelope/frame bytes excluding the newline. Empty raw records are valid transport for invalid-payload fixtures. Strict canonical base64 and matching SHA-256 are required. Schema validation alone cannot enforce decoded size, digest, coordinate equality, or provenance.

At size/capacity limits stop/reject before accepting additional data. Never truncate accepted raw content. Incomplete final NDJSON is pending during live reads; broken sealed input, changed accepted coordinates, or digest mismatch fails closed as source corruption. Valid framing containing malformed XML is different: that occurrence can reach quarantine while later records proceed.

Moves/renames preserve generation identity and sequence. New project-capture generations created by rotation obtain new UUIDs; native ACS export renames do not create new identities. In-place truncation/rewrite of accepted data is unsupported and reported, not treated as a new file under old identity. Retain records/manifests throughout the supported replay window. Copying a corpus preserves its manifest; equal file content alone does not prove equal occurrences.

## Envelope fields

| Field | Required type/meaning |
| --- | --- |
| `schema_version` | Literal `1.0.0`; unknown versions rejected until supported |
| `event_id` | Canonical string above, checked against coordinates |
| `source.family` | `ONLINE` or `OFFLINE` |
| `source.producer`, `source.environment` | Nonempty strings, maximum 128 characters; environment initially `poc` |
| `source.generation_id` | Lowercase canonical UUID |
| `source.sequence` | Integer 1 through 9,007,199,254,740,991 |
| `source.provenance` | `synthetic` or `real-export`; real export requires retained release/export evidence |
| `source.time_scale` | `UTC`, `TAI`, or `unknown`, declared from evidence |
| `captured_at` | UTC RFC 3339, millisecond precision, literal `Z` |
| `raw.format` | `acs-xml` for ONLINE, `offline-json` for OFFLINE |
| `raw.encoding` | Literal `base64`; decoded profile bytes must be UTF-8 |
| `raw.data` | Canonical base64 of exact original bytes |
| `raw.sha256` | Lowercase 64-digit SHA-256, for integrity, never occurrence equivalence |

Reject unknown envelope properties in v1. Attempts, replay flags, mutable paths, and AMQP tags are runtime metadata, not source identity or stable payload. Future schema changes require a reviewed version policy.

## ONLINE XML profile

One complete element, unqualified or in namespace `urn:schemas-cosylab-com:logging:1.0`. Supported roots: `Trace`, `Debug`, `Info`, `Notice`, `Warning`, `Error`, `Critical`, `Alert`, `Emergency`. Other roots are unsupported and quarantined. Require nonempty `TimeStamp` of at most 128 characters; preserve the string even if date parsing fails.

Context can include `SourceObject`, `Host`, `Process`, `Thread`, `Context`, `LogId`, `StackId`, `StackLevel`, `File`, `Line`, `Routine`, `Priority`, `Audience`, `Array`, `Antenna`, and `Uri`. Component is `SourceObject`, else `Process`, else null. Severity is uppercase root name; do not infer numeric priority mappings. Missing optional fields remain null/empty. A promoted component longer than 128 characters is a profile error, not silently truncated.

Preserve mixed message text outside `Data` descendants in document order. Preserve `Data` as ordered `{name,value}` string pairs, including duplicate names and entries before/after message text. Require nonempty `Data.Name` and text/CDATA-only content. Unsupported child elements/conflicting namespaces are quarantined. Unknown attributes remain accessible in raw evidence. Prohibit DTDs, external entities/resource loading, and XInclude. Preserve exact raw whitespace independently of normalized text.

This subset is grounded in historical formatter/tests, not claimed as complete current ACS compatibility. `Delouse`, `Archive`, `Alarm`, document wrappers and other unsupported roots are outside v1; a profile rejection does not mean the source is invalid ACS. See [DOC-03](../research/acs-feasibility.md).

## Real XML export admission gate

Before importing `real-export`, retain an approved sanitized source artifact and an export manifest identifying release/commit or image digest, exporter/version/options, source encoding, framing/wrapper/namespace, clock evidence and sanitization method. Obtain and compare the actual release's schema/IDL and sample behavior, recording any schema/wire mismatch; an old XSD or a Docker Hub tag is insufficient. A real capture is not automatically compatible with this project profile.

Initially prefer sealed files. Determine complete XML element boundaries independently of physical lines: historical clients/stores differ in wrappers and may contain multiline CDATA. Keep the approved sanitized artifact intact and retain an ordered mapping from record byte ranges to project generation/sequence; resume/rename/reimport must reuse that mapping, including repeated equal records. Native filename, LogId and timestamp are not sufficient coordinates. Assign new generations only to independently captured/imported occurrences; retain the manifest for replay.

V1 still requires UTF-8 payload bytes. Verify actual bytes; a historical logging-client file mode declares ISO-8859-1 and an old Java store uses `writeBytes`. Incompatible encoding requires a reviewed conversion/profile policy with original artifact and conversion provenance retained, not silent transcoding or a false exact-byte claim. Sanitized exports are derivative evidence, not byte-identical operational originals; preserve ordering/multiplicity and describe changes before assigning the retained project capture.

Verify producer clock/timezone explicitly. The manual's TAI statement conflicts with historical Java local-time formatting; do not infer UTC or TAI from a zone-free string or host assumptions. In v1 unresolved time stays `unknown`, with null UTC projection. Framing, byte fidelity, closure/rotation and known-marker delivery remain runtime checks, not capabilities established by this contract.

## OFFLINE JSON profile

Each decoded record is one UTF-8 JSON object. Reject duplicate keys, NaN/Infinity, non-object roots, unknown fields, and missing/wrong-type mandatory fields. Require string `timestamp`, `severity`, `component`, `message`. Timestamp is UTC RFC 3339 with milliseconds and `Z`; severity is one of the nine uppercase ONLINE names; component is nonempty, at most 128 characters. Message may be empty.

Optional `request_id`/`operation_id`: nonempty strings, maximum 128 characters. Optional `data`: ordered string `{name,value}` pairs. Payload size bounds apply to all fields. Capture precedes broker publication. Application identifiers are not occurrence identity; identical API calls still produce different sequences. Declare any artificial cross-source identifiers in the scenario.

## Time and errors

CT-03 separates original time, declared scale, UTC projection, and status. Mock XML declares UTC in its manifest; only that explicit declaration permits interpreting a zone-free XML timestamp as UTC. JSON requires `Z`. TAI/unknown scales retain original strings with null UTC projection in v1. No TAI-to-UTC conversion is guessed: future real integration must validate a conversion policy before claiming time-based correlation for such records.

Malformed XML/JSON is a captured occurrence and is quarantined under its original ID. Corrupt envelopes/source artifacts fail the boundary without checkpoint advancement. See [examples](examples/README.md).

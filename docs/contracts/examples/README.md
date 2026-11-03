# Contract examples

**Status:** original synthetic examples for proposed CT-01/CT-03; not ALMA operational data, an ACS runtime test, or the full acceptance corpus.

| File | Expected result |
| --- | --- |
| [online-valid.xml](online-valid.xml) | Accepted XML profile, including CDATA, Unicode, and `Data` |
| [online-invalid.xml](online-invalid.xml) | Transportable raw bytes, then `E_XML_PARSE` quarantine |
| [offline-valid.json](offline-valid.json) | Accepted simulator profile |
| [offline-invalid.json](offline-invalid.json) | JSON syntax valid, `E_PAYLOAD_PROFILE` for numeric timestamp and missing component |
| [online-envelope.json](online-envelope.json) | CT-01 envelope for online-valid.xml |
| [online-normalized.json](online-normalized.json) | Deterministic CT-03 projection of that envelope |
| [occurrences.json](occurrences.json) | Independently declared source coordinates/expected dispositions; two ONLINE occurrences deliberately reference identical bytes |

The example generation IDs and source clocks are deliberately synthetic. A manifest entry fixes coordinates before processing. Sequences 1 and 2 in the ONLINE generation have identical payload hashes, different event IDs, and the same timestamp; replay preserves exactly two occurrences. The invalid record at sequence 3 is retained in quarantine. OFFLINE uses its own generation with one valid and one invalid occurrence.

Raw digests include each example file's final newline. Base64 decoding online-envelope.json must reproduce online-valid.xml byte for byte. Source `time_scale=UTC` explicitly describes the mock; it does not assert that a real ACS timestamp is UTC.

The historical XSD in DOC-03 was inspected, but these unqualified wire-style examples are not advertised as validated against the current ACS schema. Contract JSON syntax, byte integrity, expected payload shape, and identity relationships can be checked without installing/running the pipeline. Runtime fault tests remain pending.

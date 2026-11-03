# DOC-03 — ACS integration feasibility

**Date:** 3 November 2026, America/Santiago. **Result:** documentary investigation complete; no runtime integration test. **Recommendation:** use the approved XML mock fallback initially; revisit real ACS on the main PC. This is not evidence that ACS cannot run on the temporary machine.

## Question and stopping rule

Can a minimal real producer and XML capture path be verified within the two-hour investigation ceiling and the temporary host's 10 GB total project storage allowance? No checkout, image pull, installation, build, or producer execution was performed. The research concluded early after access and footprint-verification blockers became clear; it did not consume two hours simply to exhaust the allowance. Exact elapsed time was not instrumented.

## Evidence inspected

| Evidence | Verified observation | Limit |
| --- | --- | --- |
| Supplied [documentation investigation](../references/documentation-investigation.md) | Identifies XML files, logging channels, and `acsXmlFileStore` as integration candidates | Supplied report; current Confluence pages could not be reopened here |
| [Community ACS source](https://github.com/ACS-Community/ACS/tree/e7fd9ce9ac6502dfdf840e920150585867504362), pinned `e7fd9ce9ac6502dfdf840e920150585867504362` | Formatter, parser tests, XSD, and file-store code accessible | Identifies ACS-OCT2017; historical, not the current ALMA release |
| [Formatter](https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsjlog/src/alma/acs/logging/formatters/AcsXMLLogFormatter.java) and [parser tests](https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/jlogEngine/test/com/cosylab/logging/engine/ACS/ACSLogParserTest.java) | Severity elements, contextual attributes, CDATA, repeated `Data`, and multiline messages | Supports a documented synthetic profile, not universal compatibility |
| [loggingMI.xsd](https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/logging/ws/idl/loggingMI.xsd) | Historical namespace and required `TimeStamp` | Namespaced schema differs from unqualified formatter/parser examples; not a current-release wire specification |
| [File-store component](https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/src/alma/acs/xmlfilestore/logging/XmlFileStoreLoggerImpl.java) | Uses container services and connects `LCEngine` to the logging channel through `QueueFileHandler` | Requires an ACS environment; not a standalone generator |
| [File handler](https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/src/alma/acs/xmlfilestore/common/QueueFileHandler.java) | Closing a file can rename it | Supports keeping path out of event identity; not current retention evidence |
| [Community Dockerfile](https://github.com/ACS-Community/ACS-Docker-Image/blob/9df3cbd1901147bfc929e2cf2d996060dc392e81/Dockerfile), pinned `9df3cbd1901147bfc929e2cf2d996060dc392e81` | CentOS 7, ACS 2020AUG, dependency compilation and ACS build | Legacy recipe, not executed |
| [acs image page](https://hub.docker.com/r/acscommunity/acs) and [acsdev page](https://hub.docker.com/r/acscommunity/acsdev) | Advertise images; `acsdev` documents `stream9.2025apr` | Displayed sizes about 1.7 GB and 5.5 GB are unverified metadata, not measured unpacked footprint or verified immutable digests |

Direct access to current ALMA GitLab/Confluence and registry tag metadata failed here. Shell requests failed DNS resolution; the search service could not open the ALMA pages. This limits this investigation, not the owner's access or ALMA service availability.

## Options and recommendation

| Option | Assessment | Recommendation |
| --- | --- | --- |
| Build inspected ACS recipe | Legacy dependencies, unverified runtime and footprint, substantial work beyond XML capture | Do not start on the temporary host |
| Newer advertised community image | Plausible, but digest, complete footprint, and minimal logger/export procedure unverified | Revisit with main-PC resources or verified headroom |
| Export from an existing working ACS environment | Smallest real-integration route if available | No working environment/corpus established here |
| Documented XML mock | Reproducible faults/repetitions without ACS runtime dependencies | Recommended first source mode |

The same 10 GB must hold OpenSearch, Dashboards, RabbitMQ, cache, records, state, and evidence. Advertised image sizes do not establish that the full stack fits, or that real ACS is impossible to fit.

Use the [CT-01](../contracts/ct-01-source.md) synthetic XML profile, retaining exact bytes in a persistent corpus. A future verified XML export can use that boundary after its release, framing, encoding, clock, and provenance are documented. This demonstrates ACS-inspired handling, not running ACS or production integration. Source/XSD are linked, not copied or relicensed. The mock's UTC clock is a project choice.

## Reopening real integration

Record hardware/headroom; identify accessible ACS source/image and immutable identifiers; document the smallest headless producer/export procedure. After runtime work is authorized, capture a known message with startup/version evidence and validate release-specific XML/time/rotation/delivery boundaries. Keep upstream losses outside the capture guarantee.

DOC-03 research is complete. The mock/tooling recommendation remains proposed for technical-design review; no implemented capability is claimed.

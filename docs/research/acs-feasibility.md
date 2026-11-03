# DOC-03 — ACS integration feasibility

**Reviewed:** 3 November 2026, America/Santiago. **Result:** a real headless producer/XML export is documentarily practical, but has not been run or sized here. **Recommendation:** prefer a small sanitized export from an already working, identified ACS release when available; use the documented mock for the immediate temporary-host PoC because no such corpus exists yet and local ACS has no demonstrated storage margin. On the main PC, test the logging-client route before configuring `LogsXmlStore`.

This browser follow-up supersedes the earlier access-blocked assessment. Research is complete; runtime feasibility remains conditional. No ACS source checkout, image pull/build, installation, service startup, or pipeline implementation was performed. The investigation concluded within the two-hour ceiling once the evidence supported a decision. This is not implementation authorization or evidence of current ALMA deployment.

## Method and evidence boundaries

Read the supplied [investigation](../references/documentation-investigation.md), [reference index](../references/README.md), 2018 paper (especially sections 2.1 and 3.1–3.3), review guide, ADR-0002/0003, and CT-01. Followed relevant links using the browser and inspected selected historical files through the GitHub connector; did not repeat the 34-page survey.

The supplied `ALMA-Oensearch-PoC` directory was an older non-Git snapshot missing the technical-design additions. It was preserved unchanged. A sibling Git checkout, `ALMA-Oensearch-PoC-current`, was cloned on `docs/technical-design` at open PR #2 head `a3fc736070e1a793846e1086524578b3e092cd25`. Its `AGENTS.md` restricts this work to documentation/research.

- **D — Documented:** observed in a primary source; not proof of execution.
- **H — Historical:** release-pinned code, old advice, or historical deployment evidence.
- **I — Inference/proposal:** reasoned PoC choice requiring validation.
- **U — Unexecuted/unknown:** not established here.

All browser access below was on **2026-11-03**, without login. The owner chose public sources only after the documented repository reached sign-in. Revisions are those exposed by Confluence change links; an edit date does not establish design age or deployment date.

## Browser-verified primary sources

| ID | Source and observed revision | Findings and limits |
| --- | --- | --- |
| B01 | [ICTACS space](https://confluence.alma.cl/collector/pages.action?key=ICTACS), dynamic | D: public documentation and release navigation accessible. |
| B02 | [Logging and archiving Manual](https://confluence.alma.cl/pages/viewpage.action?pageId=25790043), v95, 2025-05-15 | D/H: Python API example, XML/time/identity semantics and schema location. Old references and damaged rendered examples limit reuse. |
| B03 | [acsExtras](https://confluence.alma.cl/pages/viewpage.action?pageId=61367992), v2, 2026-03-13 | D: `LogsXmlStore`, `AlarmsXmlStore`, `QueueFileHandler`, optional AMQP/Kafka handlers. Catalog, not release-specific setup instructions. |
| B04 | [Notification Channel](https://confluence.alma.cl/pages/viewpage.action?pageId=50562416), v10, 2025-04-25 | D/H: naming/notification services, CDB QoS, reconnection and discard/reliability limitations. |
| B05 | [Retrieving ACS](https://confluence.alma.cl/spaces/ICTACS/pages/54004860/Retrieving+ACS), v5, 2021-09-27 | H: Bitbucket read-only Git URL; `acs/YYYYMMM` release branches from 2020APR. Availability today requires separate verification. |
| B06 | [Installation index](https://confluence.alma.cl/spaces/ICTACS/pages/54004890/Installation+and+Configuration), v4; [build guide](https://confluence.alma.cl/spaces/ICTACS/pages/54004895/Step-by-step+Compilation+and+Installation), v10; both 2025-04-24 | D/H: build ExtProd, then ACS Kit/Tools/CommonSoftware; sample output uses 2020JUN. Full build is broader than producing one log. |
| B07 | [RHEL9 installation](https://confluence.alma.cl/spaces/ICTACS/pages/240564943/ACS+Installation+-+RHEL9), v4, 2025-09-09 | D: explicitly last tested for COMMON-2025OCT; Java 21, OS/development dependencies, ExtProd/ACS archives, environment profile and `acsStart`. Binary download requires a password. |
| B08 | [System Requirements](https://confluence.alma.cl/spaces/ICTACS/pages/54005149/System+Requirements), v15, 2025-04-24 | D/H: 10 GB storage, at least 4 GB RAM with intermittent behavior at that limit; repeats 4 GB for loggingService. CPU minimum unknown. Mixed-age OS/tool tables. |
| B09 | [ACS Cheat Sheet](https://confluence.alma.cl/spaces/ICTACS/pages/98413896/ACS+Cheat+Sheet), v21, 2026-06-16 | D: core startup and Java container commands; GUIs are separate. |
| B10 | [COMMON-2026OCT](https://confluence.alma.cl/spaces/ICTACS/pages/304317478/COMMON-2026OCT), v6, 2026-09-29 | D: fifth ACS release for Cycle 14; integration branch changes include dependencies, logging and NC fixes. Maintenance evidence, not an immutable downloadable release or production inventory. |
| B11 | [Offline log FAQ](https://confluence.alma.cl/pages/viewpage.action?pageId=54003112), created 2020-05-15; answer 2004-08-31 | H: command-line capture and later viewing in jlog. A simpler export lead than a managed component. |
| B12 | [ACE logger implementation](https://confluence.alma.cl/spaces/ICTACS/pages/118345196/ACS+Technical+Documents+-+Logging+System+-+C+ACE+Logger+Implementation), v29, 2024-04-03 | D: distinguishes central `loggingService`, Python intermediary `acsLogSvc`, and `loggingClient` file/stdout/syslog outputs. |

Access outcomes: [ASW GitLab](https://asw.alma.cl/groups/ASW) returned browser `ERR_HTTP2_PROTOCOL_ERROR`; the [documented Bitbucket URL](https://bitbucket.alma.cl/scm/asw/acs.git) redirected to login for `/projects/asw/repos/acs/browse`. The manual-linked [ESO schema index](https://www.eso.org/projects/alma/develop/acs/OnlineDocs/ACS_docs/schemas/index.html) returned 404. These do not establish service-wide unavailability or absence of internal/current schemas. No login, TLS bypass or ALMA-system changes were performed; B05's insecure global TLS workaround was not followed. B07's [restricted binary location](https://webdav.alma.cl/restricted/Releases/) was identified from the guide, not accessed or downloaded.

## Images, releases, and capacity

**D:** [acsdev overview](https://hub.docker.com/r/acscommunity/acsdev) attributes maintenance to ALMA's Common Infrastructure Team and documents the `acs` environment alias and `INTROOT`. That is publisher attribution; the latest visible push was April 2025, not evidence of a refreshed 2026 image. [acs overview](https://hub.docker.com/r/acscommunity/acs) retains an older community recipe. Neither was executed.

| Tag and browser detail link | Platform | Manifest digest | Compressed size |
| --- | --- | --- | --- |
| [acsdev:stream9.2025apr](https://hub.docker.com/layers/acscommunity/acsdev/stream9.2025apr/images/sha256-f13d118dd4e3b44f0ac3d9e83aa555ba8ae4fb83997efa77f708c01e731d1f50) | linux/amd64 | `sha256:f13d118dd4e3b44f0ac3d9e83aa555ba8ae4fb83997efa77f708c01e731d1f50` | 5.48 GB; tag UI displayed push 2025-04-26 |
| [acs:2020.08.0-centos7](https://hub.docker.com/layers/acscommunity/acs/2020.08.0-centos7/images/sha256-a34122a09c938e4212c0a14bd6b466108987877d95d394b0a0d6b2772b5b6c43) | linux/amd64 | `sha256:a34122a09c938e4212c0a14bd6b466108987877d95d394b0a0d6b2772b5b6c43` | 1.29 GB; UI says almost six years old |
| [acs:2020.08.0](https://hub.docker.com/layers/acscommunity/acs/2020.08.0/images/sha256-9a4e89360b4340be7f7b740c46d2b1a10422b87edfcd57ce5d55c983d98bc4e3), also listed as `latest` | linux/amd64 | `sha256:9a4e89360b4340be7f7b740c46d2b1a10422b87edfcd57ce5d55c983d98bc4e3` | 1.72 GB; UI says about six years old |

For acsdev, Hub separately labels index digest `sha256:0139e9e4b0f2a44a22f48591c0094e46c91f25e8e2acbb4108f2bc0832fb9a45`. Distinguish index from platform manifest. The [acsdev tags](https://hub.docker.com/r/acscommunity/acsdev/tags) and [acs tags](https://hub.docker.com/r/acscommunity/acs/tags) were read; no ARM entry was displayed for these candidates, not a registry-wide architecture audit.

The acsdev layers advertise `APP_BRANCH=integration/COMMON-2025APR`, Java 21, an ACS-2025APR archive copy and an installation layer. Its default command keeps the container alive; loading its environment is not service startup. The centos7 layer metadata identifies ACS-2020AUG. The previously reviewed [Dockerfile](https://github.com/ACS-Community/ACS-Docker-Image/blob/9df3cbd1901147bfc929e2cf2d996060dc392e81/Dockerfile), pinned `9df3cbd1901147bfc929e2cf2d996060dc392e81`, is historical 2020AUG evidence, not a mapping to the 2025 image.

Hub explicitly labels size as the sum of compressed layers. It excludes unpacked storage, peak extraction/build space, writable growth, cache and volumes. **U:** actual installed footprint/peak RAM. B08's 10 GB is general documented storage guidance without release-specific accounting, not a measured container footprint. The temporary i5-11300H/16 GB host has only 10 GB for the entire project, including OpenSearch/Dashboards/RabbitMQ, data/state/evidence and headroom. **I:** there is no evidenced fit for additional local ACS. Smaller historical tags establish neither fit nor compatibility; defer local ACS to a separately measured main-PC experiment.

## Smallest plausible headless producer/export

**D/H:** B02 provides `Acspy.Common.Log.getLogger` and `logInfo`; B12 describes the service path. B11 documents `acsStartLoggingClient > myLogFile.xml`. This supports a smaller candidate than creating a custom component plus Java file store:

1. Load one identified ACS release's environment. Record immutable image/source, `acsConfigReport`, OS/architecture, timezone and ACS instance. Use normal `acsStart` initially (B07/B09); naming/notification, central logging and Python intermediary must be available. Exact service pruning/minimum process count is **U**.
2. Attach the logging client first, then emit a known INFO marker through the Python ACS logger. Verify readiness, centralized filtering and buffered dispatch/flush. Console output alone does not prove channel receipt.
3. Capture XML and diagnostics separately; stop cleanly and retain original bytes plus startup/version evidence. Verify the installed wrapper's options before using its file mode.
4. Count marker occurrences; approve a small sanitized sealed corpus for import, retaining order, multiplicity and provenance. One captured marker does not prove loss-free delivery.

**I:** no GUI, telescope hardware, custom application component/container, OpenSearch or broker is needed for this capture experiment itself. ACS core still has substantial dependencies. Formatting XML without services would demonstrate serialization only. A future sequential capture experiment can avoid running ACS and the observability stack at their combined peak.

The historical [loggingClient.cpp][client] resolves naming/channel services. Stdout emits fragments plus newlines; `-f` adds an ISO-8859-1 declaration, `Log`/`Header` wrapper and closing `Log` on signal termination. Crash output may be incomplete. `ACS_LOG_BIN` changes channel/input handling, so XML output does not establish an XML-only upstream transport. **U:** behavior in the advertised 2025 image/current release, wrapper invocation, actual encoding and shutdown durability.

## LogsXmlStore configuration and file behavior

B03 establishes purpose and optional brokers, without defaults or guarantees. **H:** concrete details below are solely from ACS-OCT2017 revision `e7fd9ce9ac6502dfdf840e920150585867504362`, not verified for 2025APR/2026OCT.

The [implementation][store] requires Java container services, generated interfaces, `jlogEngine.LCEngine`, an ORB/logging channel, queue utilities and alarm-source API. It connects through QueueFileHandler, enables reconnection and closes the engine in cleanup. The [test CDB][components] registers `LOGS_XMLSTORE`, helper `alma.acs.xmlfilestore.logging.impl.LoggerHelper`, type `IDL:alma/xmlFileStore/LogsXmlStore:1.0`, in Java `frodoContainer`. The [test prologue][prologue] starts ORB services/manager and awaits that container. These are dependency/setup leads, not a tested modern recipe. Separate alarm archiving, SQL, RabbitMQ and Kafka are not demonstrated as necessary for file-only capture; alarm API availability remains to verify.

| Historical property prefix `alma.acs.extras.archivelogger.` | Observed behavior |
| --- | --- |
| `logDir` | Site-specific default; override with bounded writable PoC directory |
| `maxFileSize` | Default 134,217,728 bytes (128 MiB); rejects values below 100,000 |
| `maxNumberFiles` | Default 750; rejects values below 1 |
| `minloglevel` | Default ACS INFO; getter/setter alone does not establish effective input filtering |

The [queue][queue] adds a trailing newline if absent and rotates before a subsequent push once the current file reaches its threshold; entry offsets are kept in memory. Embedded newlines can remain, so physical lines are not dependable event boundaries. The [specialized handler][handler] adds no document wrapper and renames processed files using creation/closure timestamps. Exceeding the file-count setting produces warning/alarm, **not deletion to enforce a storage cap**. Filename timestamps are not event identity or necessarily event-time bounds.

The [file writer][queuefile] uses `RandomAccessFile.writeBytes` and fixed 23-character timestamp extraction, without an explicit UTF-8 encoder in that path. **I/U:** non-ASCII fidelity needs a release-specific byte test. This code does not prove crash-safe capture or durable occurrence coordinates. Prefer sealed files for the first real import.

## XML, clock, schema, and identity

| Topic | Evidence and consequence |
| --- | --- |
| Namespace/framing | B02 cites `urn:schemas-cosylab-com:logging:1.0`; [historical XSD][xsd] has that target namespace and global Data references; [formatter][formatter] emits unqualified elements. Keep the namespace distinction. Wrapper documents, fragment streams and project NDJSON are different formats. |
| CDATA/Data | Formatter emits CDATA for messages/exceptions/parameters. Preserve ordered/repeated Data and raw bytes; damaged manual examples and simplistic historic CDATA concatenation are not universal fixtures. Test multiline, `]]>`, XML characters and non-ASCII. |
| Time | B02 specifies TAI/milliseconds but requirements mention 100 ns. Formatter uses `LogRecord.getMillis()`; [IsoDateFormat][date] uses local-time SimpleDateFormat without enforcing UTC. Its comment assumes ALMA hosts use UTC, which proves nothing about this host/image. Preserve source strings and verify scale/timezone; assume neither TAI nor UTC globally. |
| Identity | B02 describes LogId as event class; historical Java formatter writes `LogRecord.getSequenceNumber()`. Semantics differ; neither establishes global occurrence identity across processes/restarts. Keep project generation UUID + sequence. |
| Coverage | Manual includes Delouse; historic XSD includes Alarm/Archive and Log wrapper. CT-01 supports nine severity roots, a deliberately narrower profile. Unsupported does not mean invalid ACS. `ACSLogTS.xsd` defines typed-log source definitions/code generation, not the runtime export schema. |

**U:** no 2025APR/2026OCT release-specific XSD/IDL, authentic XML corpus, verified time conversion or deployed ALMA version was obtained. ESO's linked schema page is unavailable; old source is still accessible. A historical namespace-qualified projection passing an old XSD does not validate unqualified wire bytes or current ACS. The 2018 paper corroborates a historical file/bridge approach, not current deployment, retention or transport.

## Reassessed decision and design effects

| Option | Proposal |
| --- | --- |
| Sanitized export from an existing working ACS | Preferred real input when available; avoids local installation. Requires approved provenance, byte/framing/time review and preserved multiplicity. No corpus obtained here. |
| Local producer plus logging client | Practical candidate for authorized main-PC verification; test before a managed store. Temporary total-storage fit unproven. |
| Local LogsXmlStore | Second experiment for archival/rotation; unnecessary merely to obtain one known log. Modern configuration remains unverified. |
| Documented mock | Immediate temporary-host recommendation while real export is absent; reproducible repetitions/errors and declared UTC, explicitly synthetic. |

The blocker is now lack of a proven release-specific runtime/export and capacity margin, not generic Confluence/digest access. A reviewed real corpus can complement synthetic fault fixtures. Do not rebuild legacy ACS just to avoid the fallback or silently discard unsupported real records.

- **CT-01:** retain envelope/NDJSON/identity; add a release-specific sealed-import gate covering byte ranges, namespace, encoding, clock and sanitization. No schema expansion or silent transcoding justified yet.
- **ADR-0002:** retain durable project-capture boundary. B04's discard/reliability limits reinforce that reconnection is not losslessness.
- **ADR-0003:** retain Python/SQLite/Compose proposal. ACS is an external capture experiment, not a mandatory temporary-stack service. ACS digests are known metadata; other component digests/footprints remain separate checks.

## Unexecuted runtime checks

After explicit authorization: verify immutable release/image and `acsConfigReport`; measure installed/peak extraction, writable and volume storage plus RAM; record effective services/instance/CDB/thresholds; prove consumer readiness and known-marker/repetition capture; inspect bytes, wrapper/framing, Unicode/CDATA/Data against release-matched schema/IDL; check clock against an independent reference; exercise closure/rotation/rename and crash tails; retain import coordinates/manifests across retries. Keep upstream loss outside the project capture guarantee. None of these checks passed by virtue of this research.

[client]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/logging/ws/src/loggingClient.cpp
[store]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/src/alma/acs/xmlfilestore/logging/XmlFileStoreLoggerImpl.java
[handler]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/src/alma/acs/xmlfilestore/common/QueueFileHandler.java
[components]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/test/CDB/MACI/Components/Components.xml
[prologue]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsExtras/acsXmlFileStore/test/prologue
[queue]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/jacsutil2/src/alma/acs/util/stringqueue/TimestampedStringQueue.java
[queuefile]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/jacsutil2/src/alma/acs/util/stringqueue/QueueFile.java
[xsd]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/logging/ws/idl/loggingMI.xsd
[formatter]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/acsjlog/src/alma/acs/logging/formatters/AcsXMLLogFormatter.java
[date]: https://github.com/ACS-Community/ACS/blob/e7fd9ce9ac6502dfdf840e920150585867504362/LGPL/CommonSoftware/jacsutil/src/alma/acs/util/IsoDateFormat.java

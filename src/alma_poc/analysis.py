"""CT-04 deterministic analysis; a shared identifier is not proof of causality."""

import re
from collections import defaultdict
from datetime import datetime

from .model import INDEX, VERSION, wire_json

UUID_TOKEN = re.compile(r"(?i)(?<!\w)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(?!\w)")
INTEGER_TOKEN = re.compile(r"(?<!\w)[0-9]+(?!\w)")


def message_template(message):
    return INTEGER_TOKEN.sub("<N>", UUID_TOKEN.sub("<UUID>", re.sub(r"\s+", " ", message).strip()))


def timeline(documents):
    known = [x for x in documents if x["event_time"]["utc"] is not None]
    unknown = [x for x in documents if x["event_time"]["utc"] is None]
    return {
        "events": [{"event_id": x["event_id"], "event_time": x["event_time"], "ingested_at": x["ingested_at"], "severity": x["severity"], "component": x["component"], "message": x["message"]} for x in sorted(known, key=lambda x: (x["event_time"]["utc"], x["event_id"]))],
        "excluded_from_utc_order": [{"event_id": x["event_id"], "event_time": x["event_time"]} for x in sorted(unknown, key=lambda x: x["event_id"])],
        "limitation": "Time/ID order is presentation order, not proven causal order.",
    }


def correlate(documents, seed_id, rule="same-operation"):
    seed = next((x for x in documents if x["event_id"] == seed_id), None)
    if seed is None:
        raise ValueError("seed is absent from selected materialization")
    if rule not in ("same-operation", "same-stack"):
        raise ValueError("unsupported rule")
    key, window = ("operation_id", 60) if rule == "same-operation" else ("stack_id", 10)
    value, seed_time = seed["correlation_keys"][key], seed["event_time"]["utc"]
    related = []
    if value and seed_time and (rule != "same-stack" or seed["source"]["family"] == "ONLINE"):
        start = datetime.fromisoformat(seed_time.replace("Z", "+00:00"))
        for document in documents:
            date = document["event_time"]["utc"]
            if document["event_id"] == seed_id or not date or document["source"]["environment"] != seed["source"]["environment"] or document["correlation_keys"][key] != value:
                continue
            if rule == "same-stack" and (document["source"]["family"] != "ONLINE" or document["source"]["producer"] != seed["source"]["producer"]):
                continue
            if abs((datetime.fromisoformat(date.replace("Z", "+00:00")) - start).total_seconds()) <= window:
                related.append(document)
    return {
        "analysis_version": VERSION, "rule": rule, "rule_version": VERSION,
        "seed_id": seed_id, "related_ids": sorted(x["event_id"] for x in related),
        "materialization": INDEX, "window_seconds": window, "matched_values": {key: value},
        "conditions": ["exact non-null identifier", "same environment", "inclusive absolute UTC distance from seed"] + (["ONLINE and same producer"] if rule == "same-stack" else []),
        "classification": "observed", "synthetic": any(x["source"]["provenance"] == "synthetic" for x in [seed, *related]),
        "explanation": f"{len(related)} other events share {key} within {window} seconds of the seed. This does not establish causality; missing/unresolved timestamps cannot match.",
    }


def patterns(documents):
    groups = defaultdict(list)
    for document in documents:
        key = (document["source"]["family"], document["component"], document["severity"], message_template(document["message"]))
        groups[key].append(document)
    result = []
    for (family, component, severity, template), events in sorted(groups.items(), key=lambda x: wire_json(list(x[0]))):
        dates = [x["event_time"]["utc"] for x in events if x["event_time"]["utc"]]
        result.append({"profile": "message-template", "version": VERSION, "family": family, "component": component, "severity": severity, "template": template, "count": len(events), "recurring": len(events) >= 2, "time_range": [min(dates), max(dates)] if dates else None, "example_ids": sorted(x["event_id"] for x in events)[:5]})
    return {"groups": result, "limitation": "Lexical templates can group semantically different messages. Inspect original examples; no events are merged or deleted."}


def analyze(documents, seed_id):
    return {"analysis_version": VERSION, "materialization": INDEX, "event_count": len(documents), "timeline": timeline(documents), "correlations": [correlate(documents, seed_id, rule) for rule in ("same-operation", "same-stack")], "patterns": patterns(documents)}

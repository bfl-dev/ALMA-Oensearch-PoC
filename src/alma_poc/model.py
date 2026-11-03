"""CT-01/CT-03: strict source identity and deterministic normalization.

The core deliberately uses the standard library so its fault/format tests can
run without a daemon or package download. JSON Schema is also checked in CI.
"""

import base64
import binascii
import hashlib
import json
import logging
import re
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from xml.parsers import expat

from .errors import DataError, EnvelopeError

VERSION = "1.0.0"
INDEX = "poc-events-v1"
RAW_LIMIT = 65536
ENVELOPE_LIMIT = 131072
DOCUMENT_LIMIT = 262144
MAX_SEQUENCE = 9007199254740991
LEVELS = {"TRACE", "DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "CRITICAL", "ALERT", "EMERGENCY"}
XML_NAMES = {x.title() for x in LEVELS}
XML_NS = "urn:schemas-cosylab-com:logging:1.0"
UTC_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\Z")
LOG = logging.getLogger(__name__)


def wire_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("non-finite JSON number")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def event_id(generation_id, sequence):
    return f"urn:alma-poc:event:v1:{generation_id}:{sequence}"


def is_utc(value):
    if not isinstance(value, str) or not UTC_PATTERN.fullmatch(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_envelope(value):
    """Structural and semantic constraints, including those JSON Schema cannot express."""
    def require(condition, reason):
        if not condition:
            raise EnvelopeError(reason)

    require(isinstance(value, dict), "envelope must be an object")
    require(set(value) == {"schema_version", "event_id", "source", "captured_at", "raw"}, "envelope fields/version not supported")
    require(value["schema_version"] == VERSION, "unsupported schema version")
    source, raw = value["source"], value["raw"]
    require(isinstance(source, dict), "source must be an object")
    require(set(source) == {"family", "producer", "environment", "generation_id", "sequence", "provenance", "time_scale"}, "invalid source fields")
    require(source["family"] in ("ONLINE", "OFFLINE"), "invalid source family")
    for field in ("producer", "environment"):
        require(isinstance(source[field], str) and 1 <= len(source[field]) <= 128, f"invalid source {field}")
    generation = source["generation_id"]
    require(isinstance(generation, str), "invalid generation ID")
    try:
        require(str(uuid.UUID(generation)) == generation, "generation UUID must be canonical lowercase")
    except (ValueError, AttributeError):
        raise EnvelopeError("invalid generation UUID") from None
    sequence = source["sequence"]
    require(type(sequence) is int and 1 <= sequence <= MAX_SEQUENCE, "invalid sequence")
    require(value["event_id"] == event_id(generation, sequence), "event ID differs from source coordinates")
    require(source["provenance"] in ("synthetic", "real-export"), "invalid source provenance")
    require(source["time_scale"] in ("UTC", "TAI", "unknown"), "invalid time scale")
    require(is_utc(value["captured_at"]), "capture time must be millisecond UTC")
    require(isinstance(raw, dict) and set(raw) == {"format", "encoding", "data", "sha256"}, "invalid raw fields")
    expected = "acs-xml" if source["family"] == "ONLINE" else "offline-json"
    require(raw["format"] == expected and raw["encoding"] == "base64", "source format/encoding mismatch")
    require(source["family"] != "OFFLINE" or source["time_scale"] == "UTC", "OFFLINE clock must be UTC")
    require(isinstance(raw["data"], str), "base64 data must be a string")
    # Check the encoded bound before decoding to avoid unbounded allocation.
    require(len(raw["data"]) <= 87384, "raw encoding exceeds bound")
    try:
        decoded = base64.b64decode(raw["data"], validate=True)
    except (ValueError, binascii.Error):
        raise EnvelopeError("invalid base64") from None
    require(base64.b64encode(decoded).decode("ascii") == raw["data"], "noncanonical base64")
    require(len(decoded) <= RAW_LIMIT, "raw record exceeds bound")
    require(raw["sha256"] == hashlib.sha256(decoded).hexdigest(), "raw digest mismatch")
    try:
        require(len(wire_json(value)) <= ENVELOPE_LIMIT, "envelope exceeds byte bound")
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise EnvelopeError("invalid envelope JSON value") from None
    return decoded


def decode_envelope(body):
    if len(body) > ENVELOPE_LIMIT:
        raise EnvelopeError("wire envelope exceeds byte bound")
    try:
        value = strict_json(body.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError):
        raise EnvelopeError("invalid wire JSON/UTF-8") from None
    validate_envelope(value)
    return value


def make_envelope(raw, source, sequence, captured_at=None):
    if not isinstance(raw, bytes) or len(raw) > RAW_LIMIT:
        raise EnvelopeError("decoded raw record exceeds bound")
    value = {
        "schema_version": VERSION,
        "event_id": event_id(source["generation_id"], sequence),
        "source": {**source, "sequence": sequence},
        "captured_at": captured_at or utc_now(),
        "raw": {
            "format": "acs-xml" if source["family"] == "ONLINE" else "offline-json",
            "encoding": "base64",
            "data": base64.b64encode(raw).decode("ascii"),
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
    }
    validate_envelope(value)
    return value


def _split_tag(tag):
    if tag.startswith("{"):
        namespace, name = tag[1:].split("}", 1)
        return namespace, name
    return "", tag


def _xml(raw):
    try:
        raw.decode("utf-8", errors="strict")
        guard = expat.ParserCreate()

        def forbidden(*_):
            raise DataError("E_XML_PARSE", "DTD/entities/external resources are forbidden")

        def declaration(_version, encoding, _standalone):
            if encoding and encoding.lower().replace("-", "") != "utf8":
                raise DataError("E_PAYLOAD_PROFILE", "XML encoding requires an explicit conversion policy")

        guard.StartDoctypeDeclHandler = forbidden
        guard.EntityDeclHandler = forbidden
        guard.ExternalEntityRefHandler = forbidden
        guard.XmlDeclHandler = declaration
        guard.Parse(raw, True)
        root = ET.fromstring(raw)
    except (UnicodeError, expat.ExpatError, ET.ParseError):
        raise DataError("E_XML_PARSE", "invalid XML/UTF-8") from None
    namespace, name = _split_tag(root.tag)
    if namespace not in ("", XML_NS) or name not in XML_NAMES:
        raise DataError("E_PAYLOAD_PROFILE", "unsupported XML root/namespace")
    timestamp = root.get("TimeStamp")
    if not timestamp or len(timestamp) > 128:
        raise DataError("E_PAYLOAD_PROFILE", "missing/oversized XML TimeStamp")
    component = root.get("SourceObject") or root.get("Process") or None
    if component is not None and len(component) > 128:
        raise DataError("E_PAYLOAD_PROFILE", "oversized component")
    message, data = [root.text or ""], []
    for child in root:
        child_ns, child_name = _split_tag(child.tag)
        if child_ns != namespace or child_name != "Data" or len(child) or not child.get("Name"):
            raise DataError("E_PAYLOAD_PROFILE", "unsupported XML child/Data shape")
        data.append({"name": child.get("Name"), "value": child.text or ""})
        message.append(child.tail or "")
    return timestamp, name.upper(), component, "".join(message), data, root.attrib


def _offline(raw):
    try:
        value = strict_json(raw.decode("utf-8"))
    except (ValueError, UnicodeError, RecursionError):
        raise DataError("E_JSON_PARSE", "invalid JSON/UTF-8") from None
    required = {"timestamp", "severity", "component", "message"}
    optional = {"request_id", "operation_id", "data"}
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - optional:
        raise DataError("E_PAYLOAD_PROFILE", "invalid OFFLINE fields")
    if any(not isinstance(value[key], str) for key in required):
        raise DataError("E_PAYLOAD_PROFILE", "OFFLINE fields must be strings")
    if not is_utc(value["timestamp"]) or value["severity"] not in LEVELS or not 1 <= len(value["component"]) <= 128:
        raise DataError("E_PAYLOAD_PROFILE", "invalid OFFLINE timestamp/severity/component")
    for key in ("request_id", "operation_id"):
        if key in value and (not isinstance(value[key], str) or not 1 <= len(value[key]) <= 128):
            raise DataError("E_PAYLOAD_PROFILE", "invalid OFFLINE identifier")
    data = value.get("data", [])
    if not isinstance(data, list) or any(not isinstance(x, dict) or set(x) != {"name", "value"} or any(not isinstance(v, str) for v in x.values()) for x in data):
        raise DataError("E_PAYLOAD_PROFILE", "invalid OFFLINE data pairs")
    return value["timestamp"], value["severity"], value["component"], value["message"], data, value


def _time(value, scale):
    projection = {"original": value, "scale": scale, "utc": None, "status": "unsupported_scale"}
    if scale == "UTC":
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            date = date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date
            if date.utcoffset().total_seconds() != 0:
                raise ValueError("UTC-declared input has non-UTC offset")
            projection.update(utc=date.isoformat(timespec="milliseconds").replace("+00:00", "Z"), status="normalized")
        except (ValueError, OverflowError):
            projection["status"] = "invalid"
    return projection


def normalize(envelope):
    raw = validate_envelope(envelope)
    online = envelope["source"]["family"] == "ONLINE"
    timestamp, severity, component, message, data, fields = _xml(raw) if online else _offline(raw)
    keys = {}
    for key, xml_name in (("request_id", "RequestId"), ("operation_id", "OperationId")):
        values = {x["value"] for x in data if x["name"] == xml_name} if online else {fields[key]} if key in fields else set()
        value = next(iter(values)) if len(values) == 1 else None
        keys[key] = value if value and len(value) <= 128 else None
        if len(values) > 1 or value and len(value) > 128:
            LOG.warning("ambiguous_or_oversized_correlation_key event_id=%s key=%s", envelope["event_id"], key)
    for key, xml_name in (("stack_id", "StackId"), ("context", "Context")):
        value = fields.get(xml_name) if online else None
        keys[key] = value if value and len(value) <= 128 else None
        if value and len(value) > 128:
            LOG.warning("oversized_correlation_key event_id=%s key=%s", envelope["event_id"], key)
    keys["provenance"] = "synthetic" if envelope["source"]["provenance"] == "synthetic" else "source"
    document = {
        "document_version": VERSION, "event_id": envelope["event_id"], "source": envelope["source"],
        "event_time": _time(timestamp, envelope["source"]["time_scale"]),
        "ingested_at": envelope["captured_at"], "severity": severity, "component": component,
        "message": message, "data": data, "correlation_keys": keys, "raw": envelope["raw"], "parser_version": VERSION,
    }
    if len(wire_json(document)) > DOCUMENT_LIMIT:
        raise DataError("E_OVERSIZE", "normalized document exceeds byte bound")
    return document

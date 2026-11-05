"""Transport-independent settlement logic, exercised at failure boundaries."""

from dataclasses import dataclass

from .capture import ZERO_PREFIX, fault_point, load_manifest, read_records
from .errors import DataError, EnvelopeError, IdentityCollision, Retryable, SystemFailure
from .model import decode_envelope, normalize


@dataclass(frozen=True)
class Delivery:
    tag: int
    body: bytes


def publish_capture(path, state, publish, *, cursor="live", fault=fault_point):
    generation = load_manifest(path)["source"]["generation_id"]
    checkpoint, saved_prefix = state.checkpoint(generation, cursor)
    seen, published = 0, 0
    verified = checkpoint == 0 and saved_prefix == ZERO_PREFIX
    for record in read_records(path):
        sequence = record.envelope["source"]["sequence"]
        seen = sequence
        if sequence <= checkpoint:
            if sequence == checkpoint:
                if record.prefix != saved_prefix:
                    raise IdentityCollision("previously confirmed capture prefix was modified")
                verified = True
            continue
        if not verified:
            raise SystemFailure("capture no longer contains its confirmed prefix")
        confirmed = publish(record.body, record.envelope["event_id"])
        if confirmed is not True:
            raise Retryable("publication was not positively confirmed and routed")
        fault("adapter.after_confirm")
        state.advance(generation, sequence, record.prefix, cursor=cursor)
        fault("adapter.after_checkpoint")
        published += 1
    if seen < checkpoint or not verified:
        raise SystemFailure("capture was truncated before confirmed progress")
    return published


def process_batch(deliveries, sink, state, ack, *, fault=fault_point):
    if len(deliveries) > 20:
        raise SystemFailure("batch exceeds in-flight limit")
    documents, valid = [], []
    stats = {"indexed": 0, "duplicates": 0, "quarantined": 0, "diagnostics": 0}
    for delivery in deliveries:
        try:
            envelope = decode_envelope(delivery.body)
        except EnvelopeError as exc:
            state.diagnostic(delivery.body, str(exc))
            fault("worker.after_quarantine")
            ack(delivery.tag)
            stats["diagnostics"] += 1
            continue
        try:
            document = normalize(envelope)
        except DataError as exc:
            state.quarantine(envelope, exc.code, str(exc))
            fault("worker.after_quarantine")
            ack(delivery.tag)
            stats["quarantined"] += 1
            continue
        documents.append(document)
        valid.append((delivery, envelope))
    if not documents:
        return stats
    fault("worker.before_index")
    results = sink.bulk_create(documents)
    if not isinstance(results, list) or len(results) != len(documents) or any(not isinstance(item, dict) for item in results):
        raise SystemFailure("unusable per-item bulk response; retain unresolved deliveries")
    failures = []
    for document, (delivery, envelope), result in zip(documents, valid, results):
        status = result.get("status")
        if status == 201:
            fault("worker.after_index")
            ack(delivery.tag)
            stats["indexed"] += 1
        elif status == 409:
            existing = sink.get(document["event_id"])
            if existing is None:
                failures.append(Retryable("conflicting document disappeared; retry"))
            elif existing != document:
                failures.append(IdentityCollision("existing index document differs; no overwrite or acknowledgment"))
            else:
                fault("worker.after_index")
                ack(delivery.tag)
                stats["duplicates"] += 1
        elif status == 429 or isinstance(status, int) and 500 <= status <= 599:
            failures.append(Retryable(f"transient bulk item status {status}"))
        elif status == 413 or status == 400 and isinstance(result.get("error"), dict) and result["error"].get("type") in {"mapper_parsing_exception", "document_parsing_exception"} and sink.mapping_is_current():
            # Only a recognized document-specific failure; unknown 400s pause.
            state.quarantine(envelope, "E_OVERSIZE" if status == 413 else "E_INDEX_DOCUMENT", str(result.get("error", {})), stage="indexing")
            fault("worker.after_quarantine")
            ack(delivery.tag)
            stats["quarantined"] += 1
        else:
            failures.append(SystemFailure(f"unclassified/systemic bulk item status {status}; retain delivery"))
    if failures:
        # Settle every known success in a partially successful response before
        # reconnecting for unresolved deliveries. Collisions/system errors win.
        raise next((x for x in failures if not isinstance(x, Retryable)), failures[0])
    return stats

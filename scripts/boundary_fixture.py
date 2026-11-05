#!/usr/bin/env python3
"""Exercise real broker/index boundaries in an isolated Compose project."""

import base64
import copy
import hashlib
import json
import os
import platform
import sqlite3
import uuid
from importlib.metadata import version
from pathlib import Path

from alma_poc.capture import Capture, read_records
from alma_poc.errors import CapacityError, DataError, IdentityCollision
from alma_poc.model import INDEX, decode_envelope, normalize, utc_now, wire_json
from alma_poc.pipeline import Delivery, process_batch, publish_capture
from alma_poc.runtime import SearchSink, rabbit_connection
from alma_poc.sources import xml_record
from alma_poc.state import State


class BoundaryFailure(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise BoundaryFailure(message)


def capture(root, name, payloads):
    path = root / name
    with Capture(path, "ONLINE", "boundary-mock") as writer:
        for raw in payloads:
            writer.append(raw)
        writer.seal()
    return path, list(read_records(path))


def publisher(pika, channel, queue):
    channel.confirm_delivery()

    def publish(body, identifier):
        channel.basic_publish(
            exchange="", routing_key=queue, body=body, mandatory=True,
            properties=pika.BasicProperties(content_type="application/json",
                                            delivery_mode=2, message_id=identifier))
        return True

    return publish


def fetch(channel, queue):
    method, _, body = channel.basic_get(queue=queue, auto_ack=False)
    require(method is not None, "expected retained delivery is absent")
    return Delivery(method.delivery_tag, body)


def pending(channel, queue):
    return channel.queue_declare(queue=queue, passive=True).method.message_count


def settle(delivery, sink, state, channel, acknowledgments):
    def ack(tag):
        channel.basic_ack(delivery_tag=tag, multiple=False)
        acknowledgments.append(tag)

    return process_batch([delivery], sink, state, ack)


def identity_collision(root, state_root, queue, sink):
    raw = xml_record("original boundary event", timestamp="2026-11-05T00:00:00.000")
    path, records = capture(root, "collision", [raw])
    original = records[0].envelope
    document = normalize(original)
    require(sink.bulk_create([document])[0]["status"] == 201, "initial boundary document was not created")
    changed = copy.deepcopy(original)
    replacement = xml_record("changed content under the same identity", timestamp="2026-11-05T00:00:00.000")
    changed["raw"]["data"] = base64.b64encode(replacement).decode()
    changed["raw"]["sha256"] = hashlib.sha256(replacement).hexdigest()
    body = wire_json(changed)
    decode_envelope(body)
    (path / "injected-collision.json").write_bytes(body)
    pika, connection, channel = rabbit_connection(queue_name=queue)
    try:
        publisher(pika, channel, queue)(body, changed["event_id"])
        delivery = fetch(channel, queue)
        acknowledgments = []
        with State(state_root / "collision.sqlite") as state:
            try:
                settle(delivery, sink, state, channel, acknowledgments)
            except IdentityCollision:
                pass
            else:
                raise BoundaryFailure("changed content did not raise IdentityCollision")
            require(not acknowledgments, "colliding delivery was acknowledged")
            require(not state.report()["entries"], "collision was misclassified as invalid source data")
        require(sink.get(document["event_id"]) == document, "stored original was overwritten")
        channel.basic_nack(delivery_tag=delivery.tag, requeue=True)
        require(pending(channel, queue) == 1, "colliding delivery was not retained by broker")
        require(list(read_records(path))[0].envelope == original, "original capture changed")
        return {"passed": True, "event_id": document["event_id"],
                "original_unchanged": True, "acknowledged": False,
                "pending_after_requeue": 1, "error_code": "E_IDENTITY_COLLISION"}
    finally:
        connection.close()


def broker_capacity(root, state_root, queue, sink):
    raw = xml_record("capacity boundary sample", timestamp="2026-11-05T00:00:00.000")
    path, records = capture(root, "broker-capacity", [raw, raw])
    limit = max(len(record.body) for record in records)
    pika, connection, channel = rabbit_connection(queue_name=queue, max_queue_bytes=limit)
    try:
        publish = publisher(pika, channel, queue)
        with State(state_root / "publisher.sqlite") as state:
            try:
                publish_capture(path, state, publish)
            except pika.exceptions.NackError:
                pass
            else:
                raise BoundaryFailure("full broker did not negatively confirm the second publish")
            generation = records[0].envelope["source"]["generation_id"]
            checkpoint = state.checkpoint(generation)
            require(checkpoint[0] == 1, "checkpoint advanced past refused publication")
        require(pending(channel, queue) == 1, "full queue evicted an accepted message")
        first = fetch(channel, queue)
        require(first.body == records[0].body, "accepted broker message changed")
        channel.basic_ack(delivery_tag=first.tag, multiple=False)
        with State(state_root / "publisher.sqlite") as state:
            require(state.checkpoint(generation) == checkpoint, "checkpoint did not survive reopen")
            require(publish_capture(path, state, publish) == 1, "retained source could not resume")
            require(state.checkpoint(generation)[0] == 2, "resumed confirmation was not checkpointed")
        second = fetch(channel, queue)
        require(second.body == records[1].body, "refused event changed during retry")
        channel.basic_nack(delivery_tag=second.tag, requeue=True)
        require(pending(channel, queue) == 1, "retried event was not retained")
        require([record.body for record in read_records(path)] == [record.body for record in records],
                "source changed during broker capacity test")
        return {"passed": True, "queue_limit_bytes": limit, "negatively_confirmed": True,
                "checkpoint_at_refusal": 1, "checkpoint_after_retry": 2,
                "source_occurrences_retained": 2, "pending_after_retry": 1}
    finally:
        connection.close()


def quarantine_capacity(root, state_root, queue, sink):
    path, records = capture(root, "quarantine-capacity", [b"<Error", b"<Error>"])
    try:
        normalize(records[0].envelope)
    except DataError as exc:
        details = str(exc)
    else:
        raise BoundaryFailure("quarantine fixture unexpectedly normalized")
    limit = len(wire_json(records[0].envelope)) + len(details.encode())
    pika, connection, channel = rabbit_connection(queue_name=queue)
    database = state_root / "quarantine.sqlite"
    try:
        publish = publisher(pika, channel, queue)
        for record in records:
            publish(record.body, record.envelope["event_id"])
        first = fetch(channel, queue)
        first_acks = []
        with State(database, quarantine_budget=limit) as state:
            settle(first, sink, state, channel, first_acks)
            require(first_acks == [first.tag], "first invalid event was not acknowledged after quarantine")
            saved = state.report()["entries"]
            require(len(saved) == 1 and state.report()["logical_bytes"] == limit,
                    "small quarantine did not reach its configured capacity")
            second = fetch(channel, queue)
            second_acks = []
            try:
                settle(second, sink, state, channel, second_acks)
            except CapacityError:
                pass
            else:
                raise BoundaryFailure("full quarantine accepted another event")
            require(not second_acks, "quarantine-full delivery was acknowledged")
            require(state.report()["entries"] == saved, "full quarantine changed its existing entry")
            channel.basic_nack(delivery_tag=second.tag, requeue=True)
            require(pending(channel, queue) == 1, "quarantine-full delivery was lost")
        # Increase the test-local logical limit, keeping the same database.
        with State(database, quarantine_budget=64 * 1024 * 1024) as state:
            require(state.report()["entries"] == saved, "quarantine entry did not survive reopen")
            retried = fetch(channel, queue)
            require(retried.body == records[1].body, "quarantine retry changed the envelope")
            retry_acks = []
            settle(retried, sink, state, channel, retry_acks)
            require(retry_acks == [retried.tag], "quarantine retry was not acknowledged")
            entries = state.report()["entries"]
            require({entry["event_id"] for entry in entries} ==
                    {record.envelope["event_id"] for record in records},
                    "quarantine recovery did not retain both occurrences")
            require(all(entry["envelope"] in [record.envelope for record in records] for entry in entries),
                    "quarantined raw evidence changed")
        require(pending(channel, queue) == 0, "quarantine queue did not drain after recovery")
        require(len(list(read_records(path))) == 2, "invalid source occurrences were lost")
        return {"passed": True, "logical_limit_bytes": limit, "error_code": "E_CAPACITY",
                "acknowledged_while_full": False, "pending_while_full": 1,
                "retained_after_reopen": True, "quarantined_after_retry": 2,
                "pending_after_recovery": 0}
    finally:
        connection.close()


def main():
    report = {"passed": False, "cases": {}, "started_at": utc_now()}
    sink = None
    try:
        run_id = str(uuid.UUID(os.environ["BOUNDARY_RUN_ID"]))
        project = os.environ["BOUNDARY_PROJECT"]
        require(project == "alma-boundary-" + run_id[:12], "unexpected boundary project")
        require(os.environ.get("SOURCE_REVISION") == os.environ["BOUNDARY_EXPECTED_REVISION"],
                "application image revision differs from checkout; rebuild before testing")
        root = Path("/data/corpus/boundaries") / run_id
        state_root = Path("/data/worker/boundaries") / run_id
        sink = SearchSink()
        sink.ensure_index()
        require(sink.query({"size": 0})["hits"]["total"]["value"] == 0,
                "boundary tests require an empty isolated index")
        report.update(project=project, run_id=run_id, source_revision=os.environ["SOURCE_REVISION"],
                      python=platform.python_version(), pika=version("pika"),
                      opensearch_py=version("opensearch-py"),
                      opensearch=sink._call(sink.client.info)["version"]["number"],
                      sqlite=sqlite3.sqlite_version)
        for name, test in (("identity_collision", identity_collision),
                           ("broker_capacity", broker_capacity),
                           ("quarantine_capacity", quarantine_capacity)):
            report["active_case"] = name
            queue = f"poc.boundary.{run_id}.{name}"
            report["cases"][name] = test(root, state_root, queue, sink)
        report.pop("active_case", None)
        report["passed"] = True
    except Exception as exc:
        report.update(error=str(exc), error_type=type(exc).__name__)
    finally:
        if sink is not None:
            try:
                sink.close()
            except Exception as exc:
                report.update(passed=False, close_error=type(exc).__name__)
        report["finished_at"] = utc_now()
    print(json.dumps(report, sort_keys=True), flush=True)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

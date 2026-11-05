"""Pika/OpenSearch adapters. Optional imports keep offline core tests usable."""

import fcntl
import hashlib
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

from .errors import PocError, Retryable, SystemFailure
from .model import INDEX, utc_now, wire_json
from .pipeline import Delivery, process_batch, publish_capture
from .state import State

QUEUE = "poc.events.v1"


def emit(phase, **fields):
    print(json.dumps({"time": utc_now(), "phase": phase, **fields}, ensure_ascii=False), flush=True)


def _object(properties):
    return {"type": "object", "dynamic": "strict", "properties": properties}


def index_definition():
    keyword = {"type": "keyword"}
    properties = {
        **{key: keyword for key in ("document_version", "event_id", "severity", "component", "parser_version")},
        "source": _object({**{key: keyword for key in ("family", "producer", "environment", "generation_id", "provenance", "time_scale")}, "sequence": {"type": "long"}}),
        "event_time": _object({"original": keyword, "scale": keyword, "status": keyword, "utc": {"type": "date", "format": "strict_date_time"}}),
        "ingested_at": {"type": "date", "format": "strict_date_time"}, "message": {"type": "text"},
        "data": {"type": "object", "enabled": False},
        "correlation_keys": _object({key: keyword for key in ("request_id", "operation_id", "stack_id", "context", "provenance")}),
        "raw": _object({"format": keyword, "encoding": keyword, "sha256": keyword, "data": {"type": "binary", "doc_values": False}}),
    }
    return {"settings": {"number_of_shards": 1, "number_of_replicas": 0, "index.translog.durability": "request"}, "mappings": {"dynamic": "strict", "properties": properties}}


def _contains(actual, expected):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        for key, value in expected.items():
            if key == "type" and value == "object" and "type" not in actual and ("properties" in actual or "enabled" in actual):
                continue  # OpenSearch may omit an implicit object type.
            if key == "doc_values" and value is False and key not in actual and actual.get("type") == "binary":
                continue  # binary doc_values defaults to false.
            if key == "properties" and set(actual.get(key, {})) != set(value):
                return False
            if key not in actual or not _contains(actual[key], value):
                return False
        return True
    return actual == expected


class SearchSink:
    def __init__(self):
        try:
            from opensearchpy import OpenSearch
        except ImportError:
            raise SystemFailure("install pinned runtime requirements before using OpenSearch") from None
        password = os.environ.get("OPENSEARCH_PASSWORD") or os.environ.get("OPENSEARCH_INITIAL_ADMIN_PASSWORD")
        if not password:
            raise SystemFailure("OPENSEARCH_PASSWORD is required")
        verify = os.environ.get("OPENSEARCH_VERIFY_CERTS", "true").lower() == "true"
        self.client = OpenSearch(
            hosts=[os.environ.get("OPENSEARCH_URL", "https://localhost:9200")],
            http_auth=(os.environ.get("OPENSEARCH_USERNAME", "admin"), password),
            verify_certs=verify, ssl_assert_hostname=verify, ssl_show_warn=verify,
            timeout=10, max_retries=0, retry_on_timeout=False,
        )

    def _call(self, function, *args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status == 429 or isinstance(status, int) and 500 <= status <= 599 or status is None or status == "N/A":
                raise Retryable("OpenSearch transport/transient failure") from exc
            if status == 413:
                raise RequestTooLarge() from exc
            raise SystemFailure(f"OpenSearch HTTP {status}; check configuration without discarding backlog") from exc

    def mapping_is_current(self):
        mappings = self._call(self.client.indices.get_mapping, index=INDEX)
        actual = mappings.get(INDEX, {}).get("mappings", {})
        if actual.get("_source", {}).get("enabled", True) is not True or not _contains(actual, index_definition()["mappings"]):
            raise SystemFailure("index mapping differs from accepted CT-03; no automatic repair/disposal")
        return True

    def ensure_index(self):
        if not self._call(self.client.indices.exists, index=INDEX):
            self._call(self.client.indices.create, index=INDEX, body=index_definition())
        self.mapping_is_current()
        settings = self._call(self.client.indices.get_settings, index=INDEX)[INDEX]["settings"]["index"]
        if str(settings["number_of_shards"]) != "1" or str(settings["number_of_replicas"]) != "0" or settings.get("translog", {}).get("durability", "request") != "request":
            raise SystemFailure("index shard/durability configuration differs from CT-03")
        return {"index": INDEX, "mapping_verified": True}

    def bulk_create(self, documents):
        lines = []
        for document in documents:
            outgoing = document
            if os.environ.get("ALMA_POC_REJECT_EVENT_ID") == document["event_id"]:
                # Acceptance-only corruption of one derived document; original
                # envelope remains intact for verified permanent-error handling.
                outgoing = {**document, "source": {**document["source"], "sequence": "not-a-long"}}
            lines.extend((wire_json({"create": {"_index": INDEX, "_id": document["event_id"]}}), wire_json(outgoing)))
        body = b"\n".join(lines) + b"\n"
        try:
            response = self._call(self.client.bulk, body=body.decode(), refresh=False)
        except RequestTooLarge:
            if len(documents) == 1:
                return [{"status": 413, "error": {"type": "oversize_document"}}]
            midpoint = len(documents) // 2
            return self.bulk_create(documents[:midpoint]) + self.bulk_create(documents[midpoint:])
        if not isinstance(response, dict) or not isinstance(response.get("items"), list) or len(response["items"]) != len(documents):
            raise SystemFailure("bulk response has no per-item results")
        if os.environ.get("ALMA_POC_FAILPOINT") == "worker.lose_response":
            raise Retryable("injected response loss after destination processed bulk")
        results = []
        for document, item in zip(documents, response["items"]):
            if not isinstance(item, dict) or set(item) != {"create"} or not isinstance(item["create"], dict):
                raise SystemFailure("bulk response does not correspond to create actions")
            if item["create"].get("_id") != document["event_id"] or item["create"].get("_index") != INDEX:
                raise SystemFailure("bulk response identity/destination mismatch")
            results.append(item["create"])
        return results

    def get(self, identifier):
        try:
            return self.client.get(index=INDEX, id=identifier)["_source"]
        except Exception as exc:
            if getattr(exc, "status_code", None) == 404:
                return None
            return self._call(lambda: (_ for _ in ()).throw(exc))

    def scan(self):
        self._call(self.client.indices.refresh, index=INDEX)
        response = self._call(self.client.search, index=INDEX, body={"size": 500, "sort": ["_doc"], "query": {"match_all": {}}}, scroll="1m")
        scroll_id = response.get("_scroll_id")
        try:
            while response["hits"]["hits"]:
                for hit in response["hits"]["hits"]:
                    yield hit["_source"]
                if not scroll_id:
                    break
                response = self._call(self.client.scroll, scroll_id=scroll_id, scroll="1m")
                scroll_id = response.get("_scroll_id", scroll_id)
        finally:
            if scroll_id:
                self._call(self.client.clear_scroll, scroll_id=scroll_id)

    def query(self, body):
        return self._call(self.client.search, index=INDEX, body=body)

    def close(self):
        self.client.close()


class RequestTooLarge(SystemFailure):
    pass


def rabbit_connection():
    try:
        import pika
    except ImportError:
        raise SystemFailure("install pinned runtime requirements before using RabbitMQ") from None
    parameters = pika.URLParameters(os.environ.get("RABBITMQ_URL", "amqp://poc:poc@localhost:5672/%2f"))
    parameters.heartbeat = 60
    parameters.blocked_connection_timeout = 10
    parameters.socket_timeout = 10
    parameters.stack_timeout = 15
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True, exclusive=False, auto_delete=False, arguments={"x-queue-type": "classic", "x-max-length-bytes": 64 * 1024 * 1024, "x-overflow": "reject-publish"})
    channel.basic_qos(prefetch_count=20)
    return pika, connection, channel


def run_adapter(root, state_path, *, once=False, replay=None):
    root, state_path = Path(root), Path(state_path)
    cursor = "live" if replay is None else "replay:" + replay
    lock_root = state_path.parent / "locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    delay, total = 1, 0
    with State(state_path) as state:
        while True:
            connection = None
            try:
                pika, connection, channel = rabbit_connection()
                channel.confirm_delivery()

                def publish(body, identifier):
                    channel.basic_publish(exchange="", routing_key=QUEUE, body=body, mandatory=True, properties=pika.BasicProperties(content_type="application/json", delivery_mode=2, message_id=identifier))
                    # Pika 1.4.4 returns None on a confirmed routed success and
                    # raises NackError/UnroutableError for negative outcomes.
                    return True

                while True:
                    count = 0
                    for manifest in sorted(root.glob("*/manifest.json")):
                        generation = json.loads(manifest.read_text())["source"]["generation_id"]
                        lock_key = hashlib.sha256((generation + ":" + cursor).encode()).hexdigest()
                        with (lock_root / lock_key).open("a+b") as lock:
                            try:
                                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                            except BlockingIOError:
                                raise SystemFailure("another publisher owns this generation/cursor") from None
                            count += publish_capture(manifest.parent, state, publish, cursor=cursor)
                    total += count
                    if count or once:
                        emit("adapter", published=count, cursor=cursor, total_this_process=total)
                    delay = 1
                    if once:
                        return {"published": total, "cursor": cursor}
                    connection.sleep(0.25)
            except KeyboardInterrupt:
                return {"published": total, "interrupted": True}
            except Exception as exc:
                if once:
                    raise
                emit("adapter_blocked", kind=type(exc).__name__, code=getattr(exc, "code", "E_SYSTEM"), retry_seconds=delay)
            finally:
                if connection is not None and connection.is_open:
                    _close(connection)
            time.sleep(delay)
            delay = min(delay * 2, 10)


class HeartbeatingSink:
    """Network I/O runs off-loop; all Pika acknowledgments stay on its thread."""
    def __init__(self, sink, connection, executor):
        self.sink, self.connection, self.executor = sink, connection, executor

    def _call(self, name, *args):
        future = self.executor.submit(getattr(self.sink, name), *args)
        # Wake as soon as the search request finishes. A blocking broker poll
        # here can add 100 ms to every replay conflict lookup.
        while not wait((future,), timeout=0.1).done:
            self.connection.process_data_events(time_limit=0)
        return future.result()

    def bulk_create(self, documents):
        return self._call("bulk_create", documents)

    def get(self, identifier):
        return self._call("get", identifier)

    def mapping_is_current(self):
        return self._call("mapping_is_current")


def run_worker(state_path, *, once=False):
    delay, totals = 1, {"indexed": 0, "duplicates": 0, "quarantined": 0, "diagnostics": 0}
    while True:
        connection, sink = None, None
        try:
            with State(state_path) as state, ThreadPoolExecutor(max_workers=1) as executor:
                _, connection, channel = rabbit_connection()
                sink = SearchSink()
                wrapped = HeartbeatingSink(sink, connection, executor)
                wrapped.mapping_is_current()
                while True:
                    batch, started = [], time.monotonic()
                    while len(batch) < 20 and time.monotonic() - started <= 0.25:
                        method, _, body = channel.basic_get(queue=QUEUE, auto_ack=False)
                        if method is None:
                            break
                        batch.append(Delivery(method.delivery_tag, body or b""))
                    if not batch:
                        if once:
                            return totals
                        connection.sleep(0.25)
                        continue
                    stats = process_batch(batch, wrapped, state, lambda tag: channel.basic_ack(delivery_tag=tag, multiple=False))
                    for key, value in stats.items():
                        totals[key] += value
                    emit("worker", **stats)
                    delay = 1
        except KeyboardInterrupt:
            return {**totals, "interrupted": True}
        except Exception as exc:
            if once:
                raise
            emit("worker_blocked", kind=type(exc).__name__, code=getattr(exc, "code", "E_SYSTEM"), retry_seconds=delay)
        finally:
            if sink is not None:
                _close(sink)
            if connection is not None and connection.is_open:
                _close(connection)  # Unacknowledged deliveries return to broker.
        time.sleep(delay)
        delay = min(delay * 2, 10)


def _close(resource):
    try:
        resource.close()
    except Exception as exc:
        emit("connection_close_failed", kind=type(exc).__name__)

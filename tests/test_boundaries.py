import copy
import json
import tempfile
import unittest
from collections import deque
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts import boundary_checks, boundary_fixture


class NackError(Exception):
    pass


class Broker:
    """Small protocol harness for fixture assertions; live results use Pika."""

    def __init__(self):
        self.queues = {}
        self.limits = {}
        self.requeues = []
        self.sleep_calls = 0

    def sleep(self, seconds):
        self.sleep_calls += 1
        for queue, body in self.requeues:
            self.queues[queue].appendleft(body)
        self.requeues.clear()

    def connect(self, *, queue_name, max_queue_bytes=64 * 1024 * 1024):
        self.queues.setdefault(queue_name, deque())
        self.limits[queue_name] = max_queue_bytes
        channel = Channel(self)
        connection = SimpleNamespace(close=channel.close, sleep=self.sleep)
        pika = SimpleNamespace(BasicProperties=SimpleNamespace,
                               exceptions=SimpleNamespace(NackError=NackError))
        return pika, connection, channel


class Channel:
    def __init__(self, broker):
        self.broker = broker
        self.deliveries = {}
        self.next_tag = 0

    def confirm_delivery(self):
        pass

    def basic_publish(self, *, exchange, routing_key, body, mandatory, properties):
        if exchange != "" or not mandatory or properties.delivery_mode != 2:
            raise AssertionError("boundary messages require persistent mandatory publication")
        queue = self.broker.queues[routing_key]
        if sum(map(len, queue)) + len(body) > self.broker.limits[routing_key]:
            raise NackError()
        queue.append(body)

    def basic_get(self, *, queue, auto_ack):
        if auto_ack:
            raise AssertionError("boundary consumption requires manual acknowledgments")
        if not self.broker.queues[queue]:
            return None, None, None
        body = self.broker.queues[queue].popleft()
        self.next_tag += 1
        self.deliveries[self.next_tag] = (queue, body)
        return SimpleNamespace(delivery_tag=self.next_tag), None, body

    def basic_ack(self, *, delivery_tag, multiple):
        if multiple:
            raise AssertionError("expected individual acknowledgment")
        self.deliveries.pop(delivery_tag)

    def basic_nack(self, *, delivery_tag, requeue):
        if not requeue:
            raise AssertionError("unresolved deliveries must be retained")
        queue, body = self.deliveries.pop(delivery_tag)
        # Model asynchronous nack handling: I/O must make progress before
        # a requeued message becomes ready again.
        self.broker.requeues.append((queue, body))

    def queue_declare(self, *, queue, passive):
        if not passive:
            raise AssertionError("fixture inspection must preserve queue settings")
        return SimpleNamespace(method=SimpleNamespace(message_count=len(self.broker.queues[queue])))

    def close(self):
        for queue, body in self.deliveries.values():
            self.broker.queues[queue].appendleft(body)
        self.deliveries.clear()


class Sink:
    def __init__(self, overwrite=False):
        self.documents = {}
        self.overwrite = overwrite

    def bulk_create(self, documents):
        result = []
        for document in documents:
            exists = document["event_id"] in self.documents
            if not exists or self.overwrite:
                self.documents[document["event_id"]] = copy.deepcopy(document)
            result.append({"status": 409 if exists and not self.overwrite else 201})
        return result

    def get(self, identifier):
        return copy.deepcopy(self.documents.get(identifier))


class BoundaryProtocolTests(unittest.TestCase):
    def test_all_three_fixtures_check_preservation_and_recovery(self):
        broker, sink = Broker(), Sink()
        with tempfile.TemporaryDirectory() as temporary, patch.object(
                boundary_fixture, "rabbit_connection", broker.connect):
            root = Path(temporary)
            collision = boundary_fixture.identity_collision(root / "source", root / "state", "collision", sink)
            capacity = boundary_fixture.broker_capacity(root / "source", root / "state", "capacity", sink)
            quarantine = boundary_fixture.quarantine_capacity(root / "source", root / "state", "quarantine", sink)
            self.assertTrue(collision["passed"])
            self.assertFalse(collision["acknowledged"])
            self.assertEqual(len(broker.queues["collision"]), 1)
            self.assertEqual(capacity["checkpoint_at_refusal"], 1)
            self.assertEqual(capacity["checkpoint_after_retry"], 2)
            self.assertEqual(quarantine["quarantined_after_retry"], 2)
            self.assertEqual(quarantine["pending_after_recovery"], 0)
            self.assertTrue(collision["redelivered_envelope_verified"])
            self.assertGreaterEqual(broker.sleep_calls, 4)

    def test_missing_requeue_still_fails_within_the_deadline(self):
        channel = SimpleNamespace(
            queue_declare=lambda **_: SimpleNamespace(method=SimpleNamespace(message_count=0)))
        connection = SimpleNamespace(sleep=Mock())
        with patch.object(boundary_fixture.time, "monotonic", side_effect=[0, 0, 1]):
            with self.assertRaisesRegex(boundary_fixture.BoundaryFailure, "expected 1 ready messages, observed 0"):
                boundary_fixture.wait_for_count(connection, channel, "queue", 1, timeout=0.1)
        connection.sleep.assert_called_once()

    def test_missing_delivery_does_not_pass_on_count_alone(self):
        channel = SimpleNamespace(basic_get=lambda **_: (None, None, None))
        connection = SimpleNamespace(sleep=Mock())
        with patch.object(boundary_fixture.time, "monotonic", side_effect=[0, 0, 1]):
            with self.assertRaisesRegex(boundary_fixture.BoundaryFailure, "did not become available"):
                boundary_fixture.fetch(connection, channel, "queue", timeout=0.1)
        connection.sleep.assert_called_once()

    def test_collision_fixture_rejects_overwriting_index_behavior(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(
                boundary_fixture, "rabbit_connection", Broker().connect):
            root = Path(temporary)
            with self.assertRaises(boundary_fixture.BoundaryFailure):
                boundary_fixture.identity_collision(root / "source", root / "state", "collision", Sink(overwrite=True))


class BoundaryControllerTests(unittest.TestCase):
    def test_failed_fixture_still_writes_report_and_stops_only_its_own_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".env.images").write_text("OPENSEARCH_IMAGE=example@sha256:abc\n")
            calls = []

            def run(command, **kwargs):
                calls.append((command, kwargs))
                if command[:2] == ["git", "rev-parse"]:
                    output = "revision\n"
                elif command[:3] == ["docker", "compose", "version"]:
                    output = "Compose test\n"
                elif "scripts/check_budget.py" in command:
                    output = '{"passed":true}\n'
                elif "scripts/boundary_fixture.py" in command:
                    output = '{"passed":false,"active_case":"broker_capacity","error":"queue dropped data","cases":{}}\n'
                    return SimpleNamespace(returncode=1, stdout=output, stderr="")
                else:
                    output = ""
                return SimpleNamespace(returncode=0, stdout=output, stderr="")

            with patch.object(boundary_checks, "ROOT", root), patch.object(
                    boundary_checks, "REQUIRED_MEMORY", 0), patch.object(
                    boundary_checks, "run", run), patch("builtins.print"):
                code = boundary_checks.main()
            self.assertEqual(code, 1)
            report_path = next((root / "artifacts/boundaries").glob("*/report.json"))
            report = json.loads(report_path.read_text())
            self.assertEqual(report["fixture"]["active_case"], "broker_capacity")
            self.assertFalse(report["passed"])
            self.assertTrue(report["containers_stopped_volumes_retained"])
            docker_calls = [(command, kwargs) for command, kwargs in calls if "-p" in command]
            for command, kwargs in docker_calls:
                self.assertTrue(command[command.index("-p") + 1].startswith("alma-boundary-"))
                self.assertEqual(kwargs["env"]["POC_OPENSEARCH_PORT"], "0")
                self.assertNotIn("--volumes", command)
            self.assertTrue(any(command[-1] == "down" for command, _ in docker_calls))


if __name__ == "__main__":
    unittest.main()

import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from alma_poc.analysis import analyze, correlate, message_template, patterns, timeline
from alma_poc.capture import Capture, ZERO_PREFIX, atomic_json, load_manifest, read_records
from alma_poc.errors import CapacityError, DataError, EnvelopeError, IdentityCollision, Retryable, SystemFailure
from alma_poc.model import INDEX, decode_envelope, make_envelope, normalize, validate_envelope, wire_json
from alma_poc.pipeline import Delivery, process_batch, publish_capture
from alma_poc.sources import fixture, generate_corpus
from alma_poc.state import State

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "docs/contracts/examples"


class MemorySink:
    """Fault harness, not an OpenSearch or RabbitMQ substitute in the demo."""
    def __init__(self):
        self.documents = {}
        self.statuses = None
        self.lose_response = False
        self.current_mapping = True

    def bulk_create(self, documents):
        results = []
        for index, document in enumerate(documents):
            identifier = document["event_id"]
            result = copy.deepcopy(self.statuses[index]) if self.statuses else {"status": 409 if identifier in self.documents else 201}
            if result["status"] == 201:
                self.documents[identifier] = copy.deepcopy(document)
            results.append(result)
        if self.lose_response:
            self.lose_response = False
            raise Retryable("response lost after destination commit")
        return results

    def get(self, identifier):
        return copy.deepcopy(self.documents.get(identifier))

    def mapping_is_current(self):
        if not self.current_mapping:
            raise SystemFailure("shared mapping drift")
        return True


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.envelope = json.loads((EXAMPLES / "online-envelope.json").read_text())
        self.source = {key: value for key, value in self.envelope["source"].items() if key != "sequence"}

    def envelope_for(self, raw):
        return make_envelope(raw, self.source, 1, self.envelope["captured_at"])

    def test_document_matches_independently_written_contract_example(self):
        self.assertEqual(normalize(self.envelope), json.loads((EXAMPLES / "online-normalized.json").read_text()))

    def test_equal_bodies_and_timestamps_have_different_occurrence_ids(self):
        other = copy.deepcopy(self.envelope)
        other["source"]["sequence"] = 2
        other["event_id"] = other["event_id"].rsplit(":", 1)[0] + ":2"
        first, second = normalize(self.envelope), normalize(other)
        self.assertEqual(first["raw"], second["raw"])
        self.assertEqual(first["event_time"], second["event_time"])
        self.assertNotEqual(first["event_id"], second["event_id"])

    def test_semantic_coordinate_and_digest_checks(self):
        for change in (lambda x: x["source"].update(sequence=True), lambda x: x["source"].update(sequence=2), lambda x: x["raw"].update(sha256="0" * 64), lambda x: x.update(schema_version="2.0.0"), lambda x: x.update(unrecognized=1)):
            value = copy.deepcopy(self.envelope)
            change(value)
            with self.assertRaises(EnvelopeError):
                validate_envelope(value)

    def test_duplicate_keys_nonfinite_and_excessive_wire_rejected(self):
        for wire in (b'{"source":1,"source":2}', b'{"source":NaN}', b'{}' * 70000, b'\xff'):
            with self.assertRaises(EnvelopeError):
                decode_envelope(wire)

    def test_noncanonical_base64_and_invalid_capture_date_rejected(self):
        value = copy.deepcopy(self.envelope)
        value["raw"]["data"] += "\n"
        with self.assertRaises(EnvelopeError):
            validate_envelope(value)
        value = copy.deepcopy(self.envelope)
        value["captured_at"] = "2026-02-30T00:00:00.000Z"
        with self.assertRaises(EnvelopeError):
            validate_envelope(value)

    def test_raw_limit_checked_before_capture(self):
        with self.assertRaises(EnvelopeError):
            self.envelope_for(b"x" * 65537)

    def test_namespaces_mixed_text_unicode_and_duplicate_data(self):
        raw = '<Info xmlns="urn:schemas-cosylab-com:logging:1.0" TimeStamp="2026-11-03T00:00:00.000"><Data Name="x">1</Data><![CDATA[señal <ok>]]><Data Name="x">2</Data> tail</Info>'.encode()
        document = normalize(self.envelope_for(raw))
        self.assertEqual(document["message"], "señal <ok> tail")
        self.assertEqual(document["data"], [{"name": "x", "value": "1"}, {"name": "x", "value": "2"}])
        self.assertIsNone(document["component"])

    def test_dtd_external_entities_and_non_utf8_declaration_rejected(self):
        cases = [b'<!DOCTYPE Info [<!ENTITY x "expanded">]><Info TimeStamp="t">&x;</Info>', b'<!DOCTYPE Info SYSTEM "file:///etc/passwd"><Info TimeStamp="t"/>', b'<?xml version="1.0" encoding="ISO-8859-1"?><Info TimeStamp="t"/>']
        for raw in cases:
            with self.assertRaises(DataError):
                normalize(self.envelope_for(raw))

    def test_xml_profile_failures_are_not_silently_discarded(self):
        for raw in (b'<Alarm TimeStamp="t"/>', b'<Info/>', b'<Info TimeStamp="t"><Data/></Info>', b'<Info TimeStamp="t"><Other/></Info>', b'<Info TimeStamp="t"><Data Name="x"><Nested/></Data></Info>'):
            with self.assertRaises(DataError) as context:
                normalize(self.envelope_for(raw))
            self.assertEqual(context.exception.code, "E_PAYLOAD_PROFILE")

    def test_tai_unknown_and_invalid_time_are_preserved(self):
        for scale in ("TAI", "unknown"):
            value = copy.deepcopy(self.envelope)
            value["source"]["time_scale"] = scale
            result = normalize(value)["event_time"]
            self.assertIsNone(result["utc"])
            self.assertEqual(result["status"], "unsupported_scale")
            self.assertEqual(result["original"], "2026-11-03T12:00:00.000")
        document = normalize(self.envelope_for(b'<Info TimeStamp="not-a-date">message</Info>'))
        self.assertEqual(document["event_time"]["status"], "invalid")
        self.assertIsNone(document["event_time"]["utc"])

    def test_conflicting_correlation_keys_are_visible_and_not_selected(self):
        raw = b'<Info TimeStamp="t"><Data Name="OperationId">a</Data><Data Name="OperationId">b</Data></Info>'
        with self.assertLogs("alma_poc.model", level="WARNING"):
            document = normalize(self.envelope_for(raw))
        self.assertIsNone(document["correlation_keys"]["operation_id"])
        self.assertEqual(len(document["data"]), 2)

    def test_offline_profile_valid_and_invalid(self):
        source = {**self.source, "family": "OFFLINE"}
        document = normalize(make_envelope((EXAMPLES / "offline-valid.json").read_bytes(), source, 1))
        self.assertEqual(document["correlation_keys"]["operation_id"], "op-17")
        for raw in ((EXAMPLES / "offline-invalid.json").read_bytes(), b'[]', b'{"timestamp":1,"timestamp":2}', b'{'):
            with self.assertRaises(DataError):
                normalize(make_envelope(raw, source, 2))

    def test_full_schema_validation_when_runtime_dependency_available(self):
        try:
            from jsonschema import Draft7Validator, FormatChecker
        except ImportError:
            self.skipTest("jsonschema unavailable: full meta/format validation requires pinned runtime dependencies")
        schema = json.loads((ROOT / "docs/contracts/schemas/event-envelope-v1.schema.json").read_text())
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        validator.validate(self.envelope)
        wrong = copy.deepcopy(self.envelope)
        wrong["raw"]["format"] = "offline-json"
        self.assertTrue(list(validator.iter_errors(wrong)))


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def capture(self, name="online", **kwargs):
        return Capture(self.root / name, "ONLINE", "test-producer", **kwargs)

    def test_writer_recovers_partial_tail_without_reusing_an_accepted_id(self):
        with self.capture() as capture:
            first = capture.append(b'<Info TimeStamp="t">first</Info>')
        with (self.root / "online/records.ndjson").open("ab") as handle:
            handle.write(b'{"unfinished":')
        with self.capture() as capture:
            second = capture.append(b'<Info TimeStamp="t">second</Info>')
        records = list(read_records(self.root / "online"))
        self.assertEqual([x.envelope["event_id"] for x in records], [first["event_id"], second["event_id"]])
        self.assertEqual(second["source"]["sequence"], 2)

    def test_crash_after_sync_recovery_commits_uncertain_frame_before_readers(self):
        code = 'import sys; from alma_poc.capture import Capture; c=Capture(sys.argv[1],"ONLINE","test-producer"); c.append(b"<Info TimeStamp=\\\"t\\\">marker</Info>")'
        result = subprocess.run([sys.executable, "-c", code, str(self.root / "online")], env={**os.environ, "ALMA_POC_FAILPOINT": "capture.after_sync"}, capture_output=True)
        self.assertEqual(result.returncode, 86, result.stderr.decode())
        self.assertEqual(list(read_records(self.root / "online")), [])
        with self.capture() as capture:
            self.assertEqual(capture.sequence, 1)
            second = capture.append(b'<Info TimeStamp="t">second</Info>')
        self.assertEqual(second["source"]["sequence"], 2)
        self.assertEqual(len(list(read_records(self.root / "online"))), 2)

    def test_sealed_capture_cannot_be_appended(self):
        with self.capture() as capture:
            capture.append(b"raw")
            capture.seal()
            with self.assertRaises(SystemFailure):
                capture.append(b"more")
        with self.assertRaises(SystemFailure):
            self.capture()

    def test_capacity_failure_never_accepts_a_record(self):
        with self.capture(budget=1) as capture:
            with self.assertRaises(CapacityError):
                capture.append(b"raw")
            self.assertEqual(capture.sequence, 0)
        self.assertEqual(list(read_records(self.root / "online")), [])

    def test_second_writer_cannot_allocate_same_sequence(self):
        with self.capture():
            with self.assertRaises(BlockingIOError):
                self.capture()

    def test_confirm_crash_and_replay_leave_checkpoint_and_identity_safe(self):
        with self.capture() as capture:
            capture.append(b"first")
            capture.append(b"second")
            generation = capture.source["generation_id"]
        published = []

        def publish(body, identifier):
            published.append(identifier)
            return True

        def crash(_):
            raise RuntimeError("crash after broker commit")

        with State(self.root / "adapter.sqlite") as state:
            with self.assertRaises(RuntimeError):
                publish_capture(self.root / "online", state, publish, fault=crash)
            self.assertEqual(state.checkpoint(generation), (0, ZERO_PREFIX))
        with State(self.root / "adapter.sqlite") as state:
            self.assertEqual(publish_capture(self.root / "online", state, publish), 2)
            self.assertEqual(publish_capture(self.root / "online", state, publish), 0)
            self.assertEqual(publish_capture(self.root / "online", state, publish, cursor="replay:first"), 2)
            self.assertEqual(state.checkpoint(generation)[0], 2)
        self.assertEqual(published[0], published[1])

    def test_negative_or_uncertain_publication_does_not_advance(self):
        with self.capture() as capture:
            capture.append(b"record")
            generation = capture.source["generation_id"]
        with State(self.root / "adapter.sqlite") as state:
            with self.assertRaises(Retryable):
                publish_capture(self.root / "online", state, lambda *_: None)
            self.assertEqual(state.checkpoint(generation)[0], 0)
            with self.assertRaises(SystemFailure):
                state.advance(generation, 2, ZERO_PREFIX)

    def test_mutated_or_truncated_confirmed_capture_fails_closed(self):
        with self.capture() as capture:
            capture.append(b"record")
        with State(self.root / "state.sqlite") as state:
            publish_capture(self.root / "online", state, lambda *_: True)
            (self.root / "online/records.ndjson").write_bytes(b"")
            with self.assertRaises(SystemFailure):
                publish_capture(self.root / "online", state, lambda *_: True)

    def test_capture_rename_with_manifest_preserves_replay_id(self):
        with self.capture() as capture:
            original = capture.append(b"record")
        (self.root / "online").rename(self.root / "archive")
        self.assertEqual(next(read_records(self.root / "archive")).envelope["event_id"], original["event_id"])

    def test_changed_early_record_is_detected_before_any_publication(self):
        with self.capture() as capture:
            capture.append(b"first")
            capture.append(b"second")
        path = self.root / "online/records.ndjson"
        rows = path.read_bytes().splitlines()
        changed = json.loads(rows[0])
        replacement = b"changed"
        changed["raw"]["data"] = base64.b64encode(replacement).decode()
        changed["raw"]["sha256"] = hashlib.sha256(replacement).hexdigest()
        path.write_bytes(wire_json(changed) + b"\n" + rows[1] + b"\n")
        published = []
        with State(self.root / "adapter.sqlite") as state:
            with self.assertRaises(IdentityCollision):
                publish_capture(self.root / "online", state, lambda *args: published.append(args) or True)
        self.assertEqual(published, [])


class SettlementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "worker.sqlite"
        self.state = State(self.path)
        self.sink, self.acked = MemorySink(), []
        self.base = json.loads((EXAMPLES / "online-envelope.json").read_text())

    def tearDown(self):
        self.state.close()
        self.temp.cleanup()

    def delivery(self, sequence=1, raw=None):
        source = {k: v for k, v in self.base["source"].items() if k != "sequence"}
        raw = (EXAMPLES / "online-valid.xml").read_bytes() if raw is None else raw
        return Delivery(sequence, wire_json(make_envelope(raw, source, sequence, self.base["captured_at"])))

    def run_batch(self, deliveries, **kwargs):
        return process_batch(deliveries, self.sink, self.state, self.acked.append, **kwargs)

    def test_three_replays_preserve_two_equal_legitimate_occurrences(self):
        deliveries = [self.delivery(1), self.delivery(2)]
        for _ in range(3):
            self.run_batch(deliveries)
        self.assertEqual(len(self.sink.documents), 2)
        self.assertEqual(self.acked, [1, 2] * 3)

    def test_lost_response_after_indexing_retries_via_content_checked_conflict(self):
        self.sink.lose_response = True
        with self.assertRaises(Retryable):
            self.run_batch([self.delivery()])
        self.assertEqual(self.acked, [])
        self.assertEqual(self.run_batch([self.delivery()])["duplicates"], 1)
        self.assertEqual(self.acked, [1])

    def test_crash_after_index_before_ack_reconciles(self):
        def crash(name):
            if name == "worker.after_index":
                raise RuntimeError("crash")
        with self.assertRaises(RuntimeError):
            self.run_batch([self.delivery()], fault=crash)
        self.assertEqual(self.acked, [])
        self.run_batch([self.delivery()])
        self.assertEqual(len(self.sink.documents), 1)
        self.assertEqual(self.acked, [1])

    def test_identity_collision_never_overwrites_or_acknowledges(self):
        self.run_batch([self.delivery()])
        self.acked.clear()
        existing = copy.deepcopy(self.sink.documents)
        with self.assertRaises(IdentityCollision):
            self.run_batch([self.delivery(raw=b'<Info TimeStamp="t">changed</Info>')])
        self.assertEqual(self.acked, [])
        self.assertEqual(self.sink.documents, existing)

    def test_partial_bulk_settles_successes_on_both_sides_of_transient_failure(self):
        self.sink.statuses = [{"status": 201}, {"status": 429}, {"status": 201}]
        with self.assertRaises(Retryable):
            self.run_batch([self.delivery(x) for x in (1, 2, 3)])
        self.assertEqual(self.acked, [1, 3])
        self.sink.statuses = None
        self.run_batch([self.delivery(2)])
        self.assertEqual(len(self.sink.documents), 3)

    def test_quarantine_commit_before_ack_survives_reopen_and_redelivery(self):
        delivery = self.delivery(raw=b"<broken")
        def crash(name):
            if name == "worker.after_quarantine":
                raise RuntimeError("crash")
        with self.assertRaises(RuntimeError):
            self.run_batch([delivery], fault=crash)
        self.assertEqual(self.acked, [])
        self.state.close()
        self.state = State(self.path)
        self.run_batch([delivery])
        self.assertEqual(len(self.state.report()["entries"]), 1)
        self.assertEqual(self.acked, [1])

    def test_quarantine_full_does_not_acknowledge(self):
        self.state.budget = 1
        with self.assertRaises(CapacityError):
            self.run_batch([self.delivery(raw=b"<broken")])
        self.assertEqual(self.acked, [])

    def test_document_rejection_isolated_but_shared_mapping_error_pauses(self):
        self.sink.statuses = [{"status": 400, "error": {"type": "mapper_parsing_exception"}}, {"status": 201}]
        self.run_batch([self.delivery(1), self.delivery(2)])
        self.assertEqual(self.acked, [1, 2])
        self.assertEqual(self.state.report()["entries"][0]["stage"], "indexing")
        self.acked.clear()
        self.sink.current_mapping = False
        with self.assertRaises(SystemFailure):
            self.run_batch([self.delivery(3), self.delivery(4)])
        self.assertNotIn(3, self.acked)

    def test_unknown_status_or_malformed_bulk_response_never_acknowledged(self):
        self.sink.statuses = [{"status": 403}]
        with self.assertRaises(SystemFailure):
            self.run_batch([self.delivery()])
        self.assertEqual(self.acked, [])
        self.sink.bulk_create = lambda _: []
        with self.assertRaises(SystemFailure):
            self.run_batch([self.delivery()])

    def test_bad_wire_is_diagnostic_not_a_fabricated_source_identity(self):
        for _ in range(2):
            self.run_batch([Delivery(7, b'{')])
        report = self.state.report()
        self.assertEqual(report["entries"], [])
        self.assertEqual(len(report["diagnostics"]), 1)
        self.assertEqual(report["diagnostics"][0]["observations"], 2)
        self.assertEqual(self.acked, [7, 7])


class CorpusAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        generate_corpus(self.root / "corpus", count=12)
        self.oracle = json.loads((self.root / "corpus/oracle.json").read_text())

    def tearDown(self):
        self.temp.cleanup()

    def documents(self):
        result = []
        for name in ("online", "offline"):
            for record in read_records(self.root / "corpus" / name):
                try:
                    result.append(normalize(record.envelope))
                except DataError:
                    pass
        return result

    def test_corpus_restart_is_idempotent_and_payload_oracle_is_independent(self):
        generate_corpus(self.root / "corpus", count=12)
        expected = {x["event_id"]: x for x in self.oracle["occurrences"]}
        for document in self.documents():
            entry = expected[document["event_id"]]
            self.assertEqual(document["raw"]["sha256"], entry["raw_sha256"])
            self.assertEqual(document["message"], entry["message"])
            self.assertEqual(document["event_time"]["utc"], entry["event_time"])
        self.assertEqual(len(self.documents()), 24)

    def test_cross_source_link_is_explicit_and_nearby_other_operation_excluded(self):
        documents = self.documents()
        result = correlate(documents, self.oracle["seed_id"])
        self.assertTrue(result["synthetic"])
        self.assertNotIn(self.oracle["negative_id"], result["related_ids"])
        linked = {x["source"]["family"] for x in documents if x["event_id"] in result["related_ids"]}
        self.assertEqual(linked, {"ONLINE", "OFFLINE"})

    def test_inclusive_window_and_no_transitive_chain(self):
        documents = self.documents()
        seed = next(x for x in documents if x["event_id"] == self.oracle["seed_id"])
        target = copy.deepcopy(seed)
        target["event_id"] = "boundary"
        target["event_time"]["utc"] = "2026-11-03T00:01:01.000Z"
        self.assertIn("boundary", correlate([seed, target], seed["event_id"])["related_ids"])
        target["event_time"]["utc"] = "2026-11-03T00:01:01.001Z"
        self.assertNotIn("boundary", correlate([seed, target], seed["event_id"])["related_ids"])

    def test_unknown_time_visible_separately_and_never_correlated(self):
        documents = self.documents()
        documents[0]["event_time"].update(utc=None, status="unsupported_scale")
        report = timeline(documents)
        self.assertEqual(len(report["excluded_from_utc_order"]), 1)
        self.assertEqual(correlate(documents, documents[0]["event_id"])["related_ids"], [])

    def test_patterns_preserve_repetitions_singletons_and_original_documents(self):
        documents = self.documents()
        before = copy.deepcopy(documents)
        groups = patterns(documents)["groups"]
        timeout = next(x for x in groups if "timeout" in x["template"])
        self.assertEqual(timeout["count"], 2)
        self.assertTrue(any(x["count"] == 1 for x in groups))
        self.assertEqual(sum(x["count"] for x in groups), len(documents))
        self.assertEqual(documents, before)
        self.assertEqual(message_template("  a17  22\n23 550e8400-e29b-41d4-a716-446655440000 "), "a17 <N> <N> <UUID>")


if __name__ == "__main__":
    unittest.main()

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from alma_poc.capture import read_records
from alma_poc.errors import Retryable, SystemFailure
from alma_poc.model import INDEX, normalize
from alma_poc.runtime import SearchSink, _contains, index_definition
from alma_poc.sources import generate_corpus, stream
from alma_poc.verification import reconcile

ROOT = Path(__file__).resolve().parents[1]


class DashboardContractTests(unittest.TestCase):
    def test_dashboard_panels_have_versions_and_resolvable_saved_objects(self):
        objects = {
            (obj["type"], obj["id"]): obj
            for obj in map(json.loads, (ROOT / "deployment/dashboards.ndjson").read_text().splitlines())
        }
        dashboard = objects[("dashboard", "poc-overview")]
        references = {ref["name"]: ref for ref in dashboard["references"]}
        panels = json.loads(dashboard["attributes"]["panelsJSON"])
        self.assertTrue(panels)
        for panel in panels:
            with self.subTest(panel=panel["panelIndex"]):
                # The installed 3.9.0 migration dereferences semver.coerce(version).
                # Without this field import can report success after migration fails.
                self.assertRegex(panel["version"], r"^\d+\.\d+\.\d+$")
                reference = references[panel["panelRefName"]]
                self.assertIn((reference["type"], reference["id"]), objects)
                self.assertEqual(panel["gridData"]["i"], panel["panelIndex"])
        for obj in objects.values():
            for reference in obj["references"]:
                self.assertIn((reference["type"], reference["id"]), objects)


class SearchProtocolTests(unittest.TestCase):
    def setUp(self):
        self.sink = SearchSink.__new__(SearchSink)
        envelope = json.loads((ROOT / "docs/contracts/examples/online-envelope.json").read_text())
        self.document = normalize(envelope)

    def test_bulk_wire_is_ndjson_create_with_original_id_and_concrete_index(self):
        captured = {}
        def bulk(**kwargs):
            captured.update(kwargs)
            return {"items": [{"create": {"status": 201, "_id": self.document["event_id"], "_index": INDEX}}]}
        self.sink.client = SimpleNamespace(bulk=bulk)
        self.assertEqual(self.sink.bulk_create([self.document])[0]["status"], 201)
        lines = captured["body"].splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), {"create": {"_id": self.document["event_id"], "_index": INDEX}})
        self.assertEqual(json.loads(lines[1]), self.document)
        self.assertTrue(captured["body"].endswith("\n"))
        self.assertFalse(captured["refresh"])

    def test_response_with_wrong_id_or_index_is_not_acknowledgeable(self):
        for field in ("_id", "_index"):
            item = {"status": 201, "_id": self.document["event_id"], "_index": INDEX}
            item[field] = "wrong"
            self.sink.client = SimpleNamespace(bulk=lambda **_: {"items": [{"create": item}]})
            with self.assertRaises(SystemFailure):
                self.sink.bulk_create([self.document])

    def test_http_413_is_split_then_single_document_isolated(self):
        class TooLarge(Exception):
            status_code = 413
        calls = []
        def bulk(**kwargs):
            calls.append(kwargs)
            raise TooLarge()
        self.sink.client = SimpleNamespace(bulk=bulk)
        result = self.sink.bulk_create([self.document, self.document])
        self.assertEqual([x["status"] for x in result], [413, 413])
        self.assertEqual(len(calls), 3)

    def test_auth_failure_pauses_and_transport_failure_retries(self):
        for status, expected in ((403, SystemFailure), (503, Retryable), (None, Retryable)):
            class Failure(Exception):
                status_code = status
            def fail():
                raise Failure()
            with self.assertRaises(expected):
                self.sink._call(fail)

    def test_mapping_verification_allows_only_documented_implicit_defaults(self):
        expected = index_definition()["mappings"]
        actual = copy.deepcopy(expected)
        actual["properties"]["source"].pop("type")
        actual["properties"]["raw"]["properties"]["data"].pop("doc_values")
        self.assertTrue(_contains(actual, expected))
        actual["properties"]["source"]["properties"]["sequence"] = {"type": "keyword"}
        self.assertFalse(_contains(actual, expected))
        actual = copy.deepcopy(expected)
        actual["properties"]["unexpected"] = {"type": "keyword"}
        self.assertFalse(_contains(actual, expected))

    def test_disabled_source_is_not_a_compatible_index(self):
        actual = {**index_definition()["mappings"], "_source": {"enabled": False}}
        self.sink.client = SimpleNamespace(indices=SimpleNamespace(get_mapping=lambda **_: {INDEX: {"mappings": actual}}))
        with self.assertRaises(SystemFailure):
            self.sink.mapping_is_current()

    def test_explicit_lost_response_fault_keeps_create_unresolved(self):
        self.sink.client = SimpleNamespace(bulk=lambda **_: {"items": [{"create": {"status": 201, "_id": self.document["event_id"], "_index": INDEX}}]})
        with patch.dict(os.environ, {"ALMA_POC_FAILPOINT": "worker.lose_response"}):
            with self.assertRaises(Retryable):
                self.sink.bulk_create([self.document])


class StreamOracleTests(unittest.TestCase):
    def test_scheduled_stream_declares_expected_coordinates_before_capture(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generate_corpus(root, count=6)
            oracle_path = root / "oracle.json"
            before = json.loads(oracle_path.read_text())
            with patch("alma_poc.sources.time.sleep"):
                result = stream(root, rate=10, seconds=1, oracle_path=oracle_path)
            oracle = json.loads(oracle_path.read_text())
            self.assertEqual(result["captured"], 10)
            self.assertEqual(len(oracle["occurrences"]) - len(before["occurrences"]), 10)
            expected = {x["event_id"]: x for x in oracle["occurrences"]}
            for manifest in root.glob("live-*/manifest.json"):
                for record in read_records(manifest.parent):
                    document = normalize(record.envelope)
                    self.assertEqual(document["raw"]["sha256"], expected[document["event_id"]]["raw_sha256"])
                    self.assertEqual(document["event_time"]["utc"], expected[document["event_id"]]["event_time"])

    def test_unbounded_plan_is_rejected_before_allocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(ValueError):
                stream(temporary, rate=1000, seconds=3600)


if __name__ == "__main__":
    unittest.main()

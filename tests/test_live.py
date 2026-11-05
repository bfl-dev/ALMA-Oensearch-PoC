import io
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from alma_poc.analysis import correlate
from alma_poc.capture import read_records
from alma_poc.model import normalize
from alma_poc.scenarios import mixed_events
from alma_poc.sources import generate_corpus, stream

ROOT = Path(__file__).resolve().parents[1]


class MixedScenarioTests(unittest.TestCase):
    def test_cascade_is_complete_across_components_with_one_operation(self):
        events, incidents = mixed_events(7, "job", random.Random(17), 1)
        self.assertEqual(len(incidents), 1)
        self.assertEqual([event["severity"] for event in events],
                         ["INFO", "ERROR", "WARNING", "ERROR", "ERROR", "NOTICE", "INFO"])
        self.assertEqual({event["operation_id"] for event in events}, {"live-job-0"})
        self.assertEqual({event["family"] for event in events}, {"ONLINE", "OFFLINE"})
        self.assertEqual({event["component"] for event in events},
                         {"mock.api", "mock.receiver", "mock.processor", "mock.pipeline"})
        self.assertIn("resumed successfully", events[-1]["message"])

    def test_short_tail_never_truncates_a_cascade(self):
        for count in range(1, 31):
            with self.subTest(count=count):
                events, incidents = mixed_events(count, "job", random.Random(3), 1)
                self.assertEqual(len(events), count)
                for incident in incidents:
                    related = [event for event in events if event["operation_id"] == incident["operation_id"]]
                    self.assertEqual(len(related), 7)
                    self.assertEqual(related[-1]["message"], "operation resumed successfully")

    def test_seed_repeats_scenarios_and_zero_rate_has_no_errors(self):
        first = mixed_events(200, "job", random.Random(17), 0.5)
        self.assertEqual(first, mixed_events(200, "job", random.Random(17), 0.5))
        self.assertNotEqual(first, mixed_events(200, "job", random.Random(18), 0.5))
        events, incidents = mixed_events(200, "job", random.Random(17), 0)
        self.assertEqual(incidents, [])
        self.assertEqual({event["severity"] for event in events}, {"INFO"})

    def test_stream_capture_oracle_and_correlation_agree_on_complete_cases(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generate_corpus(root, count=6)
            oracle_path = root / "oracle.json"
            baseline = json.loads(oracle_path.read_text())["occurrences"]
            with redirect_stdout(io.StringIO()), patch("alma_poc.sources.time.sleep"):
                result = stream(root, rate=20, seconds=1, oracle_path=oracle_path,
                                scenario="mixed", incident_rate=1, seed=17)
            oracle = json.loads(oracle_path.read_text())
            self.assertEqual(oracle["occurrences"][:len(baseline)], baseline)
            expected = {entry["event_id"]: entry for entry in oracle["occurrences"][len(baseline):]}
            documents = []
            for manifest in root.glob("live-*/manifest.json"):
                self.assertTrue(json.loads(manifest.read_text())["sealed"])
                for record in read_records(manifest.parent):
                    document = normalize(record.envelope)
                    entry = expected[document["event_id"]]
                    for field in ("component", "severity", "message"):
                        self.assertEqual(document[field], entry[field])
                    self.assertEqual(document["raw"]["sha256"], entry["raw_sha256"])
                    self.assertEqual(document["event_time"]["utc"], entry["event_time"])
                    documents.append(document)
            self.assertEqual(len(documents), 20)
            self.assertEqual(len({doc["event_id"] for doc in documents}), 20)
            self.assertEqual(result["incidents"], 2)
            for incident in oracle["streams"][-1]["incidents"]:
                matches = correlate(documents, incident["seed_id"])
                self.assertEqual(set(matches["related_ids"]),
                                 set(incident["event_ids"]) - {incident["seed_id"]})
                self.assertTrue(matches["synthetic"])
                self.assertEqual(matches["matched_values"]["operation_id"], incident["operation_id"])

    def test_same_seed_allocates_new_occurrence_identities_on_each_run(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with redirect_stdout(io.StringIO()), patch("alma_poc.sources.time.sleep"):
                first = stream(root, rate=7, seconds=1, scenario="mixed", incident_rate=1, seed=17)
                second = stream(root, rate=7, seconds=1, scenario="mixed", incident_rate=1, seed=17)
            first_case, second_case = first["incident_examples"][0], second["incident_examples"][0]
            self.assertEqual(first_case["scenario"], second_case["scenario"])
            self.assertFalse(set(first_case["event_ids"]) & set(second_case["event_ids"]))

    def test_invalid_settings_fail_before_creating_capture(self):
        for options in ({"incident_rate": -0.1}, {"incident_rate": 1.1},
                        {"seed": True}, {"family": "ONLINE"}, {"rate": 0.05},
                        {"scenario": "unknown"}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "capture"
                settings = {"scenario": "mixed", **options}
                with self.assertRaises(ValueError):
                    stream(root, **settings)
                self.assertFalse(root.exists())

    def test_cli_produces_a_bounded_stream_and_prints_searchable_incidents(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [sys.executable, "-m", "alma_poc", "stream", "--root", temporary,
                 "--scenario", "mixed", "--incident-rate", "1", "--seed", "17",
                 "--rate", "1000", "--seconds", "0.021"],
                cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
                text=True, capture_output=True, timeout=10, check=True)
            planned, completed = map(json.loads, result.stdout.splitlines())
            self.assertEqual(planned["phase"], "stream_plan")
            self.assertEqual(planned["incidents"], 3)
            self.assertEqual(completed["captured"], 21)
            self.assertEqual(completed["incident_examples"], planned["incident_examples"])


if __name__ == "__main__":
    unittest.main()

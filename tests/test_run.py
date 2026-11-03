import copy
import json
import tempfile
import unittest
from pathlib import Path

from alma_poc.capture import read_records
from alma_poc.model import normalize
from alma_poc.pipeline import Delivery, process_batch, publish_capture
from alma_poc.sources import generate_corpus
from alma_poc.state import State
from alma_poc.verification import reconcile
from test_core import MemorySink


class FullCoreRun(unittest.TestCase):
    def test_2000_valid_events_and_two_invalids_across_restart_and_two_replays(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generate_corpus(root / "corpus", count=1000)
            oracle = json.loads((root / "corpus/oracle.json").read_text())
            sink, captures = MemorySink(), {}
            for family in ("online", "offline"):
                for record in read_records(root / "corpus" / family):
                    captures[record.envelope["event_id"]] = record.envelope
            for cursor in ("live", "replay:first", "replay:second"):
                queue = []
                def publish(body, identifier):
                    queue.append(body)
                    return True
                with State(root / "adapter.sqlite") as adapter:
                    for family in ("online", "offline"):
                        publish_capture(root / "corpus" / family, adapter, publish, cursor=cursor)
                acked = []
                with State(root / "worker.sqlite") as worker:
                    for start in range(0, len(queue), 20):
                        deliveries = [Delivery(index, body) for index, body in enumerate(queue[start:start + 20], start)]
                        process_batch(deliveries, sink, worker, acked.append)
                    report = reconcile(list(sink.documents.values()), oracle, worker.report(), captures)
                self.assertEqual(len(acked), 2002)
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["indexed"], 2000)
                self.assertEqual(report["quarantined"], 2)
            # Equal totals cannot hide a missing event plus a duplicate.
            corrupted = list(copy.deepcopy(sink.documents).values())
            corrupted[0] = copy.deepcopy(corrupted[1])
            with State(root / "worker.sqlite") as worker:
                report = reconcile(corrupted, oracle, worker.report(), captures)
            self.assertFalse(report["passed"])
            self.assertTrue(report["errors"]["missing_indexed"])
            self.assertTrue(report["errors"]["duplicate_indexed"])


if __name__ == "__main__":
    unittest.main()

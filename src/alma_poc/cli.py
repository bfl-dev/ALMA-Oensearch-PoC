"""Small explicit commands; live operations never run as a side effect of import."""

import argparse
import json
import logging
import sys
import time
import uuid
from pathlib import Path

from .analysis import analyze
from .capture import atomic_json
from .errors import PocError, SystemFailure
from .model import INDEX, utc_now
from .sources import generate_corpus, serve_api, stream
from .state import State

ROOT = Path(__file__).resolve().parents[2]


def parser():
    result = argparse.ArgumentParser(description="Independent ALMA-inspired OpenSearch PoC")
    commands = result.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="create/resume synthetic corpus and independent oracle")
    generate.add_argument("--root", default="data/corpus")
    generate.add_argument("--count", type=int, default=1000)
    generate.add_argument("--invalid", type=int, choices=(0, 1), default=1)
    live = commands.add_parser("stream", help="bounded continuous synthetic ONLINE/OFFLINE capture")
    live.add_argument("--root", default="data/corpus")
    live.add_argument("--rate", type=float, default=10)
    live.add_argument("--seconds", type=float, default=120)
    live.add_argument("--family", choices=("ONLINE", "OFFLINE", "both"), default="both")
    live.add_argument("--oracle", help="extend an existing acceptance oracle before generating the scheduled stream")
    live.add_argument("--scenario", choices=("normal", "mixed"), default="normal")
    live.add_argument("--incident-rate", type=float, default=0.1,
                      help="probability of a cascade per operation in mixed mode (0..1)")
    live.add_argument("--seed", type=int, help="repeat the scenario choices while allocating new event identities")
    api = commands.add_parser("api", help="synthetic OFFLINE API; captures before returning 202")
    api.add_argument("--root", default="data/corpus")
    api.add_argument("--host", default="0.0.0.0")
    api.add_argument("--port", type=int, default=8080)
    adapter = commands.add_parser("adapter", help="confirmed publication and independent historical replay")
    adapter.add_argument("--root", default="data/corpus")
    adapter.add_argument("--state", default="data/adapter/checkpoints.sqlite")
    adapter.add_argument("--once", action="store_true")
    adapter.add_argument("--replay", help="durable replay-job identifier; use a new ID for a full repeat")
    worker = commands.add_parser("worker")
    worker.add_argument("--state", default="data/worker/quarantine.sqlite")
    worker.add_argument("--once", action="store_true")
    commands.add_parser("init", help="explicitly create/verify the strict v1 index")
    report = commands.add_parser("analyze")
    report.add_argument("--oracle", default="data/corpus/oracle.json")
    report.add_argument("--seed")
    report.add_argument("--output", default="artifacts/analysis.json")
    verify = commands.add_parser("verify")
    verify.add_argument("--oracle", default="data/corpus/oracle.json")
    verify.add_argument("--state", default="data/worker/quarantine.sqlite")
    verify.add_argument("--output", default="artifacts/reconciliation.json")
    quarantine = commands.add_parser("quarantine", help="inspect/export retained invalid-input evidence")
    quarantine.add_argument("--state", default="data/worker/quarantine.sqlite")
    quarantine.add_argument("--output")
    query = commands.add_parser("queries", help="execute reproducible queries and record actual timings")
    query.add_argument("--output", default="artifacts/queries.json")
    commands.add_parser("validate-schema", help="Draft-07 meta/format validation with positive/negative envelopes")
    return result


def _documents(sink):
    documents = []
    for document in sink.scan():
        documents.append(document)
        if len(documents) > 20000:
            raise SystemFailure("analysis scan exceeds 20,000-event bound; choose a smaller explicit run")
    return documents


def run(args):
    if args.command == "generate":
        return generate_corpus(args.root, args.count, args.invalid)
    if args.command == "stream":
        return stream(args.root, args.rate, args.seconds, args.family, args.oracle,
                      scenario=args.scenario, incident_rate=args.incident_rate, seed=args.seed)
    if args.command == "api":
        serve_api(args.root, args.host, args.port)
        return {"stopped": True}
    if args.command == "adapter":
        from .runtime import run_adapter
        return run_adapter(args.root, args.state, once=args.once, replay=args.replay)
    if args.command == "worker":
        from .runtime import run_worker
        return run_worker(args.state, once=args.once)
    if args.command == "validate-schema":
        try:
            from jsonschema import Draft7Validator, FormatChecker
        except ImportError:
            raise SystemFailure("install pinned jsonschema requirement to execute full schema validation") from None
        schema = json.loads((ROOT / "docs/contracts/schemas/event-envelope-v1.schema.json").read_text())
        Draft7Validator.check_schema(schema)
        example = json.loads((ROOT / "docs/contracts/examples/online-envelope.json").read_text())
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        validator.validate(example)
        wrong = json.loads(json.dumps(example))
        wrong["raw"]["format"] = "offline-json"
        if not list(validator.iter_errors(wrong)):
            raise SystemFailure("negative schema example was incorrectly accepted")
        return {"schema": "Draft-07", "meta_valid": True, "positive": "accepted", "negative": "rejected"}
    if args.command == "quarantine":
        if not Path(args.state).is_file():
            raise SystemFailure("worker state does not exist")
        with State(args.state) as state:
            report = state.report()
        if args.output and args.output != "-":
            atomic_json(args.output, report)
        return report
    from .runtime import SearchSink
    sink = SearchSink()
    try:
        if args.command == "init":
            return sink.ensure_index()
        if args.command == "analyze":
            seed = args.seed or json.loads(Path(args.oracle).read_text())["seed_id"]
            report = {"generated_at": utc_now(), "result": analyze(_documents(sink), seed)}
        elif args.command == "verify":
            from .verification import verify_live
            if not Path(args.state).is_file():
                raise SystemFailure("worker quarantine state must exist before reconciliation")
            with State(args.state) as state:
                report = verify_live(sink, args.oracle, state)
        else:
            definitions = json.loads((ROOT / "deployment/queries.json").read_text())
            runs = []
            for query in definitions:
                start = time.perf_counter()
                response = sink.query(query["body"])
                runs.append({"name": query["name"], "body": query["body"], "elapsed_seconds": time.perf_counter() - start, "response": response})
            report = {"generated_at": utc_now(), "materialization": INDEX, "runs": runs, "limitation": "Measured query times are local synthetic observations, not production SLOs."}
        if args.output == "-":
            return report
        atomic_json(args.output, report)
        return {"output": args.output, **({"passed": report["passed"]} if "passed" in report else {"recorded": True})}
    finally:
        sink.close()


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    try:
        result = run(parser().parse_args(argv))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
        return 1 if isinstance(result, dict) and result.get("passed") is False else 0
    except KeyboardInterrupt:
        return 130
    except (PocError, ValueError, OSError) as exc:
        print(json.dumps({"error": getattr(exc, "code", "E_SYSTEM"), "message": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

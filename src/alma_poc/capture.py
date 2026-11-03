"""Append-only durable capture; replay identity does not depend on filenames."""

import fcntl
import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

from .errors import CapacityError, EnvelopeError, IdentityCollision, SystemFailure
from .model import ENVELOPE_LIMIT, RAW_LIMIT, VERSION, decode_envelope, make_envelope, strict_json, wire_json

ZERO_PREFIX = "0" * 64


def sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as handle:
            handle.write(wire_json(value) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def fault_point(name):
    """Opt-in crash points for acceptance tests; never enabled by default."""
    if os.environ.get("ALMA_POC_FAILPOINT") == name:
        os._exit(86)


def directory_bytes(path):
    return sum(item.stat().st_size for item in Path(path).rglob("*") if item.is_file())


@dataclass(frozen=True)
class Record:
    envelope: dict
    body: bytes
    prefix: str
    end: int


def load_manifest(path):
    try:
        manifest = strict_json((Path(path) / "manifest.json").read_text(encoding="utf-8"))
        if set(manifest) != {"version", "source", "sealed"} or manifest["version"] != VERSION or type(manifest["sealed"]) is not bool:
            raise ValueError("unsupported manifest")
        # Reuse semantic validation without inventing a source event.
        make_envelope(b"", manifest["source"], 1)
        return manifest
    except (OSError, ValueError, TypeError, KeyError, EnvelopeError) as exc:
        raise SystemFailure(f"invalid capture manifest: {exc}") from exc


def read_records(path, *, include_pending=False, _verified=False):
    path = Path(path)
    manifest = load_manifest(path)
    try:
        committed = strict_json((path / "committed.json").read_text())
        if set(committed) != {"sequence", "prefix"} or type(committed["sequence"]) is not int or committed["sequence"] < 0:
            raise ValueError("invalid committed watermark")
    except (OSError, ValueError, TypeError) as exc:
        raise SystemFailure("capture has no valid committed watermark") from exc
    data_path = path / "records.ndjson"
    if not data_path.exists():
        if committed["sequence"]:
            raise SystemFailure("committed capture data is missing")
        return
    if not _verified:
        # Validate the entire committed prefix before exposing even the first
        # record. Otherwise a changed early record could escape before the
        # final chained watermark reveals corruption. Two bounded passes avoid
        # buffering the whole source corpus in the adapter's memory.
        for _ in read_records(path, include_pending=include_pending, _verified=True):
            pass
    prefix, sequence = ZERO_PREFIX, 0
    verified = committed == {"sequence": 0, "prefix": ZERO_PREFIX}
    with data_path.open("rb") as handle:
        while True:
            if not include_pending and sequence == committed["sequence"]:
                if not verified:
                    raise SystemFailure("committed prefix does not match source")
                return
            line = handle.readline(ENVELOPE_LIMIT + 2)
            if not line:
                if sequence < committed["sequence"] or not verified:
                    raise SystemFailure("capture is shorter than committed watermark")
                return
            if len(line) > ENVELOPE_LIMIT + 1:
                raise SystemFailure("capture frame exceeds bound")
            if not line.endswith(b"\n"):
                if manifest["sealed"] or sequence < committed["sequence"]:
                    raise SystemFailure("sealed capture has an incomplete frame")
                return  # An active writer may not have finished this frame.
            envelope = decode_envelope(line[:-1])
            sequence += 1
            if envelope["source"] != {**manifest["source"], "sequence": sequence}:
                raise SystemFailure("capture source/sequence changed")
            prefix = hashlib.sha256(bytes.fromhex(prefix) + line).hexdigest()
            if sequence == committed["sequence"]:
                if prefix != committed["prefix"]:
                    raise IdentityCollision("committed capture prefix was modified")
                verified = True
            yield Record(envelope, line[:-1], prefix, handle.tell())


class Capture:
    def __init__(self, path, family, producer, *, generation_id=None, environment="poc", time_scale="UTC", budget=100 * 1024 * 1024, budget_root=None):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.budget_root = Path(budget_root) if budget_root else self.path
        self.budget = budget
        self.lock = (self.path / ".writer.lock").open("a+b")
        try:
            fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            manifest_path = self.path / "manifest.json"
            if manifest_path.exists():
                self.manifest = load_manifest(self.path)
                source = self.manifest["source"]
                if self.manifest["sealed"]:
                    raise SystemFailure("cannot append to a sealed capture")
                expected = {"family": family, "producer": producer, "environment": environment, "provenance": "synthetic", "time_scale": time_scale}
                if any(source.get(k) != value for k, value in expected.items()) or generation_id and generation_id != source["generation_id"]:
                    raise SystemFailure("capture manifest differs from requested source")
            else:
                if (self.path / "records.ndjson").exists() and (self.path / "records.ndjson").stat().st_size:
                    raise SystemFailure("orphan source records have no manifest; restore provenance before reopening")
                source = {"family": family, "producer": producer, "environment": environment, "generation_id": generation_id or str(uuid.uuid4()), "provenance": "synthetic", "time_scale": time_scale}
                make_envelope(b"", source, 1)
                self.manifest = {"version": VERSION, "source": source, "sealed": False}
                atomic_json(self.path / "committed.json", {"sequence": 0, "prefix": ZERO_PREFIX})
                atomic_json(manifest_path, self.manifest)
            self.sequence, self.prefix, end = 0, ZERO_PREFIX, 0
            for record in read_records(self.path, include_pending=True):
                self.sequence, end = record.envelope["source"]["sequence"], record.end
                self.prefix = record.prefix
            data_path = self.path / "records.ndjson"
            self.handle = data_path.open("a+b")
            if self.handle.seek(0, os.SEEK_END) != end:
                self.handle.truncate(end)  # Only an unfinished, unaccepted final frame.
                self.handle.flush()
            # Promote complete uncertain frames only after recovery sync. Normal
            # readers never publish beyond this durable watermark.
            os.fsync(self.handle.fileno())
            atomic_json(self.path / "committed.json", {"sequence": self.sequence, "prefix": self.prefix})
            self.failed = False
            sync_directory(self.path)
        except BaseException:
            if getattr(self, "handle", None):
                self.handle.close()
            self.lock.close()
            raise

    @property
    def source(self):
        return self.manifest["source"]

    def append(self, raw, *, captured_at=None):
        if self.manifest["sealed"] or self.failed:
            raise SystemFailure("cannot append to a sealed capture")
        if not isinstance(raw, bytes) or len(raw) > RAW_LIMIT:
            raise CapacityError("record exceeds decoded byte bound")
        envelope = make_envelope(raw, self.source, self.sequence + 1, captured_at)
        frame = wire_json(envelope) + b"\n"
        with (self.budget_root / ".budget.lock").open("a+b") as budget_lock:
            fcntl.flock(budget_lock, fcntl.LOCK_EX)
            if directory_bytes(self.budget_root) + len(frame) + 256 > self.budget:
                raise CapacityError("source capture budget reached; event not accepted")
            try:
                self.handle.write(frame)
                self.handle.flush()
                fault_point("capture.before_sync")
                os.fsync(self.handle.fileno())
                fault_point("capture.after_sync")
                prefix = hashlib.sha256(bytes.fromhex(self.prefix) + frame).hexdigest()
                atomic_json(self.path / "committed.json", {"sequence": self.sequence + 1, "prefix": prefix})
            except BaseException:
                self.failed = True  # Reopen/recover before allocating another ID.
                raise
        self.sequence, self.prefix = self.sequence + 1, prefix
        fault_point("capture.after_commit")
        return envelope

    def seal(self):
        if self.failed:
            raise SystemFailure("failed capture must be recovered before sealing")
        self.manifest["sealed"] = True
        atomic_json(self.path / "manifest.json", self.manifest)

    def close(self):
        if getattr(self, "handle", None):
            self.handle.close()
        if not self.lock.closed:
            self.lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

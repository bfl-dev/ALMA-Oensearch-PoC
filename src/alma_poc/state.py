"""Local durable progress/quarantine. A failed transaction never permits ack."""

import hashlib
import json
import sqlite3
from pathlib import Path

from .capture import ZERO_PREFIX
from .errors import CapacityError, IdentityCollision, SystemFailure
from .model import INDEX, utc_now, wire_json


class State:
    def __init__(self, path, quarantine_budget=64 * 1024 * 1024):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        if self.db.execute("PRAGMA synchronous").fetchone()[0] != 2:
            raise SystemFailure("SQLite FULL durability setting did not take effect")
        self.budget = quarantine_budget
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS checkpoints (
              generation TEXT NOT NULL, destination TEXT NOT NULL, cursor TEXT NOT NULL,
              sequence INTEGER NOT NULL, prefix TEXT NOT NULL,
              PRIMARY KEY(generation,destination,cursor));
            CREATE TABLE IF NOT EXISTS quarantine (
              event_id TEXT NOT NULL, materialization TEXT NOT NULL, envelope BLOB NOT NULL,
              code TEXT NOT NULL, stage TEXT NOT NULL, details TEXT NOT NULL, observed_at TEXT NOT NULL,
              PRIMARY KEY(event_id,materialization));
            CREATE TABLE IF NOT EXISTS diagnostics (
              fingerprint TEXT PRIMARY KEY, wire BLOB NOT NULL, details TEXT NOT NULL,
              observations INTEGER NOT NULL, observed_at TEXT NOT NULL);
        """)

    def checkpoint(self, generation, cursor="live", destination=INDEX):
        row = self.db.execute("SELECT sequence,prefix FROM checkpoints WHERE generation=? AND destination=? AND cursor=?", (generation, destination, cursor)).fetchone()
        return (row["sequence"], row["prefix"]) if row else (0, ZERO_PREFIX)

    def advance(self, generation, sequence, prefix, *, cursor="live", destination=INDEX):
        with self.db:
            current, _ = self.checkpoint(generation, cursor, destination)
            if sequence != current + 1:
                raise SystemFailure("checkpoint cannot skip/unconfirm source progress")
            self.db.execute("INSERT INTO checkpoints VALUES(?,?,?,?,?) ON CONFLICT(generation,destination,cursor) DO UPDATE SET sequence=excluded.sequence,prefix=excluded.prefix", (generation, destination, cursor, sequence, prefix))

    def _used(self):
        records = self.db.execute("SELECT coalesce(sum(length(envelope)+length(CAST(details AS BLOB))),0) FROM quarantine").fetchone()[0]
        diagnostics = self.db.execute("SELECT coalesce(sum(length(wire)+length(CAST(details AS BLOB))),0) FROM diagnostics").fetchone()[0]
        return records + diagnostics

    def quarantine(self, envelope, code, details, stage="normalization", materialization=INDEX):
        encoded = wire_json(envelope)
        with self.db:
            existing = self.db.execute("SELECT envelope FROM quarantine WHERE event_id=? AND materialization=?", (envelope["event_id"], materialization)).fetchone()
            if existing:
                if bytes(existing[0]) != encoded:
                    raise IdentityCollision("quarantine identity reused with different envelope")
                return False
            if self._used() + len(encoded) + len(details.encode()) > self.budget:
                raise CapacityError("quarantine budget reached; delivery must remain unacknowledged")
            self.db.execute("INSERT INTO quarantine VALUES(?,?,?,?,?,?,?)", (envelope["event_id"], materialization, encoded, code, stage, details, utc_now()))
        return True

    def diagnostic(self, wire, details):
        fingerprint = "wire:" + hashlib.sha256(wire).hexdigest()
        with self.db:
            found = self.db.execute("SELECT 1 FROM diagnostics WHERE fingerprint=?", (fingerprint,)).fetchone()
            if not found and self._used() + len(wire) + len(details.encode()) > self.budget:
                raise CapacityError("diagnostic budget reached; delivery must remain unacknowledged")
            self.db.execute("INSERT INTO diagnostics VALUES(?,?,?,?,?) ON CONFLICT(fingerprint) DO UPDATE SET observations=observations+1", (fingerprint, wire, details, 1, utc_now()))

    def report(self):
        entries = []
        for row in self.db.execute("SELECT * FROM quarantine ORDER BY event_id,materialization"):
            item = dict(row)
            item["envelope"] = json.loads(bytes(item["envelope"]))
            entries.append(item)
        return {"sqlite_version": sqlite3.sqlite_version, "synchronous": self.db.execute("PRAGMA synchronous").fetchone()[0], "entries": entries, "diagnostics": [dict(row) | {"wire": bytes(row["wire"]).hex()} for row in self.db.execute("SELECT * FROM diagnostics ORDER BY fingerprint")], "logical_bytes": self._used()}

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

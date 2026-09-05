from __future__ import annotations

import json
import os
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA = "vertex-relay/1"
BRIDGE_SCHEMA = "vertex-relay-mcp-store/1"

ALLOWED_TYPES = {
    "CANONICAL",
    "ARCHITECTURE_CONTRACT",
}

ALLOWED_ACTIONS = {
    "SHARE",
    "DRAFT",
    "AMEND",
}

ALLOWED_SOURCES = {
    "VERTEX_WORKSTATION",
    "VERA",
}

ALLOWED_TARGETS = {
    "VERA",
    "VERTEX_WORKSTATION",
}


def _local_appdata() -> Path:
    raw = os.environ.get("LOCALAPPDATA")
    if raw:
        return Path(raw)
    return Path.home() / "AppData" / "Local"


def default_db_path() -> Path:
    return (
        _local_appdata()
        / "VertexWorkstation"
        / "relay_mcp"
        / "vertex_relay.db"
    )


def now_ms() -> int:
    return int(time.time() * 1000)


def validate_envelope(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("RELAY_BODY_NOT_OBJECT")

    if value.get("schema") != SCHEMA:
        raise ValueError("RELAY_SCHEMA_INVALID")

    if value.get("type") not in ALLOWED_TYPES:
        raise ValueError("RELAY_TYPE_INVALID")

    if value.get("action") not in ALLOWED_ACTIONS:
        raise ValueError("RELAY_ACTION_INVALID")

    if value.get("source") not in ALLOWED_SOURCES:
        raise ValueError("RELAY_SOURCE_INVALID")

    if value.get("target") not in ALLOWED_TARGETS:
        raise ValueError("RELAY_TARGET_INVALID")

    subject = value.get("subject")
    if not isinstance(subject, dict):
        raise ValueError("RELAY_SUBJECT_INVALID")

    if not isinstance(subject.get("id"), str) or not subject["id"]:
        raise ValueError("RELAY_SUBJECT_ID_INVALID")

    if not isinstance(subject.get("name"), str) or not subject["name"]:
        raise ValueError("RELAY_SUBJECT_NAME_INVALID")

    timestamp = value.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("RELAY_TIMESTAMP_INVALID")

    if "payload" not in value:
        raise ValueError("RELAY_PAYLOAD_MISSING")

    return value


@dataclass(frozen=True)
class RelayRecord:
    relay_id: str
    received_at_ms: int
    state: str
    envelope: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "bridge_schema": BRIDGE_SCHEMA,
            "relay_id": self.relay_id,
            "received_at_ms": self.received_at_ms,
            "state": self.state,
            "envelope": self.envelope,
        }


class RelayStore:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path or default_db_path())
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            timeout=10,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS relays (
                    relay_id TEXT PRIMARY KEY,
                    received_at_ms INTEGER NOT NULL,
                    state TEXT NOT NULL,
                    target TEXT NOT NULL,
                    source TEXT NOT NULL,
                    relay_type TEXT NOT NULL,
                    action TEXT NOT NULL,
                    subject_id TEXT NOT NULL,
                    subject_name TEXT NOT NULL,
                    envelope_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_relays_target_state_time
                ON relays(target, state, received_at_ms DESC);

                CREATE TABLE IF NOT EXISTS acknowledgements (
                    ack_id TEXT PRIMARY KEY,
                    relay_id TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL,
                    FOREIGN KEY(relay_id) REFERENCES relays(relay_id)
                );

                CREATE TABLE IF NOT EXISTS replies (
                    reply_id TEXT PRIMARY KEY,
                    created_at_ms INTEGER NOT NULL,
                    envelope_json TEXT NOT NULL
                );
                """
            )

    def ingest(self, envelope: dict[str, Any]) -> RelayRecord:
        envelope = validate_envelope(envelope)

        relay_id = (
            f"{now_ms()}-"
            f"{uuid.uuid4().hex[:12]}"
        )
        received_at = now_ms()
        subject = envelope["subject"]

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO relays (
                    relay_id,
                    received_at_ms,
                    state,
                    target,
                    source,
                    relay_type,
                    action,
                    subject_id,
                    subject_name,
                    envelope_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relay_id,
                    received_at,
                    "PENDING",
                    envelope["target"],
                    envelope["source"],
                    envelope["type"],
                    envelope["action"],
                    subject["id"],
                    subject["name"],
                    json.dumps(
                        envelope,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                ),
            )

        return RelayRecord(
            relay_id=relay_id,
            received_at_ms=received_at,
            state="PENDING",
            envelope=envelope,
        )

    def _row_to_record(
        self,
        row: sqlite3.Row,
    ) -> RelayRecord:
        return RelayRecord(
            relay_id=row["relay_id"],
            received_at_ms=row["received_at_ms"],
            state=row["state"],
            envelope=json.loads(row["envelope_json"]),
        )

    def latest(
        self,
        target: str = "VERA",
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM relays
                WHERE target = ?
                ORDER BY received_at_ms DESC
                LIMIT 1
                """,
                (target,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_record(row).as_dict()

    def pending(
        self,
        target: str = "VERA",
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), 50))

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM relays
                WHERE target = ?
                  AND state = 'PENDING'
                ORDER BY received_at_ms ASC
                LIMIT ?
                """,
                (target, safe_limit),
            ).fetchall()

        return [
            self._row_to_record(row).as_dict()
            for row in rows
        ]

    def get(
        self,
        relay_id: str,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM relays
                WHERE relay_id = ?
                """,
                (relay_id,),
            ).fetchone()

        if row is None:
            return None

        return self._row_to_record(row).as_dict()

    def acknowledge(
        self,
        relay_id: str,
        actor: str = "VERA",
        note: str = "",
    ) -> dict[str, Any]:
        ack_id = (
            f"ack-{now_ms()}-"
            f"{uuid.uuid4().hex[:10]}"
        )
        created_at = now_ms()

        with self._connect() as conn:
            existing = conn.execute(
                """
                SELECT relay_id
                FROM relays
                WHERE relay_id = ?
                """,
                (relay_id,),
            ).fetchone()

            if existing is None:
                raise KeyError("RELAY_NOT_FOUND")

            conn.execute(
                """
                UPDATE relays
                SET state = 'ACKNOWLEDGED'
                WHERE relay_id = ?
                """,
                (relay_id,),
            )

            conn.execute(
                """
                INSERT INTO acknowledgements (
                    ack_id,
                    relay_id,
                    actor,
                    note,
                    created_at_ms
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    ack_id,
                    relay_id,
                    actor,
                    note[:2000],
                    created_at,
                ),
            )

        return {
            "ack_id": ack_id,
            "relay_id": relay_id,
            "actor": actor,
            "state": "ACKNOWLEDGED",
            "created_at_ms": created_at,
        }

    def put_reply(
        self,
        envelope: dict[str, Any],
    ) -> dict[str, Any]:
        envelope = validate_envelope(envelope)

        if envelope["source"] != "VERA":
            raise ValueError("REPLY_SOURCE_MUST_BE_VERA")

        if envelope["target"] != "VERTEX_WORKSTATION":
            raise ValueError(
                "REPLY_TARGET_MUST_BE_VERTEX_WORKSTATION"
            )

        reply_id = (
            f"reply-{now_ms()}-"
            f"{uuid.uuid4().hex[:10]}"
        )
        created_at = now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO replies (
                    reply_id,
                    created_at_ms,
                    envelope_json
                ) VALUES (?, ?, ?)
                """,
                (
                    reply_id,
                    created_at,
                    json.dumps(
                        envelope,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                ),
            )

        return {
            "reply_id": reply_id,
            "created_at_ms": created_at,
            "state": "QUEUED_FOR_WORKSTATION",
        }

    def latest_reply(self) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM replies
                ORDER BY created_at_ms DESC
                LIMIT 1
                """
            ).fetchone()

        if row is None:
            return None

        return {
            "reply_id": row["reply_id"],
            "created_at_ms": row["created_at_ms"],
            "envelope": json.loads(
                row["envelope_json"]
            ),
        }

    def status(self) -> dict[str, Any]:
        with self._connect() as conn:
            relay_count = conn.execute(
                "SELECT COUNT(*) FROM relays"
            ).fetchone()[0]
            pending_count = conn.execute(
                """
                SELECT COUNT(*)
                FROM relays
                WHERE state = 'PENDING'
                """
            ).fetchone()[0]
            reply_count = conn.execute(
                "SELECT COUNT(*) FROM replies"
            ).fetchone()[0]

        return {
            "bridge_schema": BRIDGE_SCHEMA,
            "relay_schema": SCHEMA,
            "database": str(self.db_path),
            "relays": relay_count,
            "pending": pending_count,
            "replies": reply_count,
        }

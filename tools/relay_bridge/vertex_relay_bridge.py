from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCHEMA = "vertex-relay/1"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 47821
MAX_BODY_BYTES = 2 * 1024 * 1024

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


def local_appdata() -> Path:
    raw = os.environ.get("LOCALAPPDATA")
    if raw:
        return Path(raw)
    return Path.home() / "AppData" / "Local"


def default_store_root() -> Path:
    return (
        local_appdata()
        / "VertexWorkstation"
        / "relay_bridge"
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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

    if "payload" not in value:
        raise ValueError("RELAY_PAYLOAD_MISSING")

    timestamp = value.get("timestamp")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("RELAY_TIMESTAMP_INVALID")

    return value


class RelayStore:
    def __init__(self, root: Path):
        self.root = root
        self.inbox = root / "inbox"
        self.outbox = root / "outbox"
        self.meta = root / "meta"
        self.lock = threading.Lock()

        for path in (self.inbox, self.outbox, self.meta):
            path.mkdir(parents=True, exist_ok=True)

    def write_inbox(
        self,
        envelope: dict[str, Any],
        remote: str,
    ) -> dict[str, Any]:
        relay_id = (
            f"{int(time.time() * 1000)}-"
            f"{uuid.uuid4().hex[:10]}"
        )
        received_at = utc_now()
        date_dir = self.inbox / received_at[:10]
        date_dir.mkdir(parents=True, exist_ok=True)

        record = {
            "bridge_schema": "vertex-relay-bridge/1",
            "relay_id": relay_id,
            "received_at": received_at,
            "remote": remote,
            "state": "RECEIVED",
            "envelope": envelope,
        }

        path = date_dir / f"{relay_id}.json"
        tmp = path.with_suffix(".json.tmp")

        with self.lock:
            tmp.write_text(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            os.replace(tmp, path)

            latest = self.meta / "latest.json"
            latest_tmp = latest.with_suffix(".json.tmp")
            latest_tmp.write_text(
                json.dumps(
                    {
                        "relay_id": relay_id,
                        "received_at": received_at,
                        "path": str(path),
                        "target": envelope["target"],
                        "type": envelope["type"],
                        "action": envelope["action"],
                        "subject": envelope["subject"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            os.replace(latest_tmp, latest)

        return {
            "relay_id": relay_id,
            "received_at": received_at,
            "state": "RECEIVED",
            "stored_at": str(path),
        }

    def read_latest(self) -> dict[str, Any] | None:
        path = self.meta / "latest.json"
        if not path.exists():
            return None

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None


class RelayHandler(BaseHTTPRequestHandler):
    server_version = "VertexRelayBridge/0.1"

    @property
    def relay_server(self) -> "RelayServer":
        return self.server  # type: ignore[return-value]

    def log_message(
        self,
        format: str,
        *args: object,
    ) -> None:
        print(
            "[relay-bridge] "
            + format % args,
            flush=True,
        )

    def _cors(self) -> None:
        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Accept",
        )
        self.send_header(
            "Access-Control-Max-Age",
            "600",
        )

    def _json(
        self,
        status: int,
        body: dict[str, Any],
    ) -> None:
        raw = json.dumps(
            body,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        self.send_response(status)
        self._cors()
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Cache-Control",
            "no-store",
        )
        self.send_header(
            "Content-Length",
            str(len(raw)),
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors()
        self.send_header(
            "Content-Length",
            "0",
        )
        self.end_headers()

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route == "/health":
            self._json(
                200,
                {
                    "service": "Vertex Relay Bridge",
                    "bridge_schema": "vertex-relay-bridge/1",
                    "relay_schema": SCHEMA,
                    "status": "READY",
                    "host": self.relay_server.server_address[0],
                    "port": self.relay_server.server_address[1],
                    "store_root": str(
                        self.relay_server.store.root
                    ),
                    "timestamp": utc_now(),
                },
            )
            return

        if route == "/vertex-relay/latest":
            latest = self.relay_server.store.read_latest()
            if latest is None:
                self._json(
                    404,
                    {
                        "error": "NO_RELAY_RECEIVED",
                    },
                )
                return

            self._json(
                200,
                latest,
            )
            return

        self._json(
            404,
            {
                "error": "ROUTE_NOT_FOUND",
            },
        )

    def do_POST(self) -> None:
        route = urlparse(self.path).path

        if route != "/vertex-relay":
            self._json(
                404,
                {
                    "error": "ROUTE_NOT_FOUND",
                },
            )
            return

        raw_length = self.headers.get(
            "Content-Length",
            "",
        )

        try:
            length = int(raw_length)
        except ValueError:
            self._json(
                411,
                {
                    "error": "CONTENT_LENGTH_REQUIRED",
                },
            )
            return

        if length <= 0:
            self._json(
                400,
                {
                    "error": "EMPTY_BODY",
                },
            )
            return

        if length > MAX_BODY_BYTES:
            self._json(
                413,
                {
                    "error": "RELAY_BODY_TOO_LARGE",
                    "max_bytes": MAX_BODY_BYTES,
                },
            )
            return

        raw = self.rfile.read(length)

        try:
            value = json.loads(raw.decode("utf-8"))
            envelope = validate_envelope(value)
        except UnicodeDecodeError:
            self._json(
                400,
                {
                    "error": "BODY_NOT_UTF8",
                },
            )
            return
        except json.JSONDecodeError:
            self._json(
                400,
                {
                    "error": "BODY_NOT_JSON",
                },
            )
            return
        except ValueError as exc:
            self._json(
                422,
                {
                    "error": str(exc),
                },
            )
            return

        remote = (
            f"{self.client_address[0]}:"
            f"{self.client_address[1]}"
        )

        receipt = self.relay_server.store.write_inbox(
            envelope,
            remote,
        )

        self._json(
            202,
            {
                "bridge_schema": "vertex-relay-bridge/1",
                **receipt,
                "next": "VERA_ADAPTER_NOT_CONNECTED",
            },
        )


class RelayServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        address: tuple[str, int],
        store: RelayStore,
    ):
        super().__init__(
            address,
            RelayHandler,
        )
        self.store = store


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Vertex Relay Bridge local ingress service."
        ),
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"default: {DEFAULT_HOST}",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"default: {DEFAULT_PORT}",
    )
    parser.add_argument(
        "--store-root",
        type=Path,
        default=default_store_root(),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.host not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        print(
            "REFUSED: Relay Bridge binds loopback only "
            "in this foundation pass.",
            file=sys.stderr,
        )
        return 2

    store = RelayStore(
        args.store_root.expanduser(),
    )

    try:
        server = RelayServer(
            (args.host, args.port),
            store,
        )
    except OSError as exc:
        print(
            "START FAILED: "
            f"{exc}",
            file=sys.stderr,
        )
        return 3

    endpoint = (
        f"http://{server.server_address[0]}:"
        f"{server.server_address[1]}"
        "/vertex-relay"
    )

    print(
        "VERTEX RELAY BRIDGE READY",
        flush=True,
    )
    print(
        f"ENDPOINT={endpoint}",
        flush=True,
    )
    print(
        "HEALTH="
        f"http://{server.server_address[0]}:"
        f"{server.server_address[1]}/health",
        flush=True,
    )
    print(
        f"STORE={store.root}",
        flush=True,
    )
    print(
        "VERA_ADAPTER=NOT_CONNECTED",
        flush=True,
    )

    stop = threading.Event()

    def request_stop(
        signum: int,
        frame: object,
    ) -> None:
        del signum, frame
        if not stop.is_set():
            stop.set()
            threading.Thread(
                target=server.shutdown,
                daemon=True,
            ).start()

    signal.signal(
        signal.SIGINT,
        request_stop,
    )
    if hasattr(signal, "SIGTERM"):
        signal.signal(
            signal.SIGTERM,
            request_stop,
        )

    try:
        server.serve_forever(
            poll_interval=0.25,
        )
    finally:
        server.server_close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

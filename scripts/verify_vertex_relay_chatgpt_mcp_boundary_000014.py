from __future__ import annotations

import ast
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

CORE = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "relay_mcp_core.py"
)

SERVER = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "vertex_relay_mcp.py"
)

REQ = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "requirements.txt"
)

SETUP = ROOT / "VERTEX_RELAY_MCP_SETUP.cmd"
START = ROOT / "VERTEX_RELAY_MCP.cmd"

required = [
    CORE,
    SERVER,
    REQ,
    SETUP,
    START,
]

for path in required:
    if not path.exists():
        raise SystemExit(
            "MISSING=" + str(path)
        )

core_text = CORE.read_text(
    encoding="utf-8",
    errors="replace",
)

server_text = SERVER.read_text(
    encoding="utf-8",
    errors="replace",
)

req_text = REQ.read_text(
    encoding="utf-8",
    errors="replace",
)

ast.parse(core_text)
ast.parse(server_text)

checks = {
    "MCP_FASTMCP":
        "FastMCP" in server_text,
    "MCP_STREAMABLE_HTTP":
        'transport="streamable-http"' in server_text,
    "MCP_ENDPOINT_DEFAULT":
        "/mcp" in server_text,
    "INGEST_ROUTE":
        '"/vertex-relay"' in server_text
        and "methods=[\"POST\"]" in server_text,
    "HEALTH_ROUTE":
        '"/health"' in server_text,
    "MCP_STATUS_TOOL":
        "def vertex_relay_status" in server_text,
    "MCP_LATEST_TOOL":
        "def vertex_relay_latest" in server_text,
    "MCP_PENDING_TOOL":
        "def vertex_relay_pending" in server_text,
    "MCP_GET_TOOL":
        "def vertex_relay_get" in server_text,
    "MCP_ACK_TOOL":
        "def vertex_relay_acknowledge" in server_text,
    "MCP_REPLY_TOOL":
        "def vertex_relay_reply" in server_text,
    "MCP_REPLY_READ_TOOL":
        "def vertex_relay_latest_reply" in server_text,
    "SQLITE_STORE":
        "sqlite3" in core_text
        and "CREATE TABLE IF NOT EXISTS relays" in core_text,
    "WAL":
        "journal_mode=WAL" in core_text,
    "RELAY_SCHEMA_GATE":
        "RELAY_SCHEMA_INVALID" in core_text,
    "REPLY_DIRECTION_GATE":
        "REPLY_SOURCE_MUST_BE_VERA" in core_text
        and "REPLY_TARGET_MUST_BE_VERTEX_WORKSTATION" in core_text,
    "INGEST_TOKEN_SUPPORT":
        "VERTEX_RELAY_INGEST_TOKEN" in server_text
        and "hmac.compare_digest" in server_text,
    "PUBLIC_CHAT_PUSH_NOT_FAKED":
        '"push_into_current_chat": False' in server_text,
    "MCP_V1_PIN":
        "mcp>=1.22,<2" in req_text,
}

for key, ok in checks.items():
    print(
        key + "=" + ("PASS" if ok else "FAIL")
    )

if not all(checks.values()):
    raise SystemExit(1)

spec = importlib.util.spec_from_file_location(
    "relay_mcp_core_verify",
    CORE,
)

if spec is None or spec.loader is None:
    raise SystemExit("CORE_IMPORT_SPEC=FAIL")

module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory(
    prefix="vertex-relay-mcp-"
) as tmp:
    db = Path(tmp) / "relay.db"
    store = module.RelayStore(db)

    inbound = {
        "schema": "vertex-relay/1",
        "type": "CANONICAL",
        "action": "SHARE",
        "source": "VERTEX_WORKSTATION",
        "target": "VERA",
        "subject": {
            "id": "summit-test",
            "name": "Summit Test",
        },
        "timestamp":
            "2026-09-05T00:00:00+00:00",
        "payload": {
            "summit": True,
        },
    }

    record = store.ingest(inbound)

    if record.state != "PENDING":
        raise SystemExit("INGEST_STATE=FAIL")

    latest = store.latest("VERA")
    if (
        latest is None
        or latest["envelope"]["subject"]["id"]
        != "summit-test"
    ):
        raise SystemExit("LATEST=FAIL")

    pending = store.pending("VERA", 10)
    if len(pending) != 1:
        raise SystemExit("PENDING=FAIL")

    ack = store.acknowledge(
        record.relay_id,
        actor="VERA",
        note="verified",
    )
    if ack["state"] != "ACKNOWLEDGED":
        raise SystemExit("ACK=FAIL")

    reply = {
        "schema": "vertex-relay/1",
        "type": "CANONICAL",
        "action": "DRAFT",
        "source": "VERA",
        "target": "VERTEX_WORKSTATION",
        "subject": {
            "id": "summit-test-reply",
            "name": "Summit Test Reply",
        },
        "timestamp":
            "2026-09-05T00:01:00+00:00",
        "payload": {
            "round_trip": True,
        },
    }

    queued = store.put_reply(reply)
    if queued["state"] != "QUEUED_FOR_WORKSTATION":
        raise SystemExit("REPLY_QUEUE=FAIL")

    latest_reply = store.latest_reply()
    if (
        latest_reply is None
        or latest_reply["envelope"]["source"]
        != "VERA"
    ):
        raise SystemExit("REPLY_READ=FAIL")

print("CORE_INGEST=PASS")
print("CORE_LATEST=PASS")
print("CORE_PENDING=PASS")
print("CORE_ACK=PASS")
print("CORE_REPLY_QUEUE=PASS")
print("CORE_REPLY_READ=PASS")
print("MCP_RUNTIME_DEPENDENCY=SETUP_REQUIRED")
print("CHATGPT_PUBLIC_HTTPS=NEXT_GATE")
print("CHATGPT_CUSTOM_APP_CONNECTION=NEXT_GATE")
print("CURRENT_CHAT_PUSH=NOT_CLAIMED")
print("VERTEX_RELAY_CHATGPT_MCP_BOUNDARY_000014_STATIC=PASS")

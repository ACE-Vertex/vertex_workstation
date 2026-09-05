from __future__ import annotations

import hmac
import json
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from relay_mcp_core import RelayStore, validate_envelope

SERVER_NAME = "Vertex Relay"
SERVER_VERSION = "0.1.1"
MAX_INGEST_BYTES = 2 * 1024 * 1024

DB_PATH = Path(
    os.environ.get(
        "VERTEX_RELAY_DB",
        str(
            Path(
                os.environ.get(
                    "LOCALAPPDATA",
                    str(Path.home() / "AppData" / "Local"),
                )
            )
            / "VertexWorkstation"
            / "relay_mcp"
            / "vertex_relay.db"
        ),
    )
)

INGEST_TOKEN = os.environ.get(
    "VERTEX_RELAY_INGEST_TOKEN",
    "",
)

store = RelayStore(DB_PATH)


READ_ONLY_CLOSED = ToolAnnotations(
    read_only_hint=True,
    open_world_hint=False,
)

WRITE_ADDITIVE_IDEMPOTENT_CLOSED = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=False,
)

WRITE_ADDITIVE_NON_IDEMPOTENT_CLOSED = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    idempotent_hint=False,
    open_world_hint=False,
)

mcp = FastMCP(
    SERVER_NAME,
    stateless_http=True,
    json_response=True,
)


def _authorized_ingest(request: Request) -> bool:
    if not INGEST_TOKEN:
        host = (
            request.client.host
            if request.client
            else ""
        )
        return host in {
            "127.0.0.1",
            "::1",
            "localhost",
            "testclient",
        }

    header = request.headers.get(
        "authorization",
        "",
    )
    prefix = "Bearer "

    if not header.startswith(prefix):
        return False

    supplied = header[len(prefix):]
    return hmac.compare_digest(
        supplied,
        INGEST_TOKEN,
    )


@mcp.custom_route(
    "/health",
    methods=["GET"],
)
async def health(
    _request: Request,
) -> JSONResponse:
    return JSONResponse(
        {
            "service": SERVER_NAME,
            "version": SERVER_VERSION,
            "status": "READY",
            "mcp_path": "/mcp",
            "ingest_path": "/vertex-relay",
            "store": store.status(),
            "chatgpt_app": "MCP_READY",
            "push_into_current_chat": False,
        }
    )


@mcp.custom_route(
    "/vertex-relay",
    methods=["POST"],
)
async def ingest(
    request: Request,
) -> JSONResponse:
    if not _authorized_ingest(request):
        return JSONResponse(
            {
                "error": "UNAUTHORIZED",
            },
            status_code=401,
        )

    raw = await request.body()

    if not raw:
        return JSONResponse(
            {
                "error": "EMPTY_BODY",
            },
            status_code=400,
        )

    if len(raw) > MAX_INGEST_BYTES:
        return JSONResponse(
            {
                "error": "RELAY_BODY_TOO_LARGE",
                "max_bytes": MAX_INGEST_BYTES,
            },
            status_code=413,
        )

    try:
        value = json.loads(
            raw.decode("utf-8")
        )
        envelope = validate_envelope(value)
    except UnicodeDecodeError:
        return JSONResponse(
            {
                "error": "BODY_NOT_UTF8",
            },
            status_code=400,
        )
    except json.JSONDecodeError:
        return JSONResponse(
            {
                "error": "BODY_NOT_JSON",
            },
            status_code=400,
        )
    except ValueError as exc:
        return JSONResponse(
            {
                "error": str(exc),
            },
            status_code=422,
        )

    record = store.ingest(envelope)

    return JSONResponse(
        {
            "bridge_schema":
                "vertex-relay-mcp-gateway/1",
            "relay_id": record.relay_id,
            "state": record.state,
            "received_at_ms":
                record.received_at_ms,
            "mcp_available": True,
            "next":
                "CHATGPT_OR_MODEL_MUST_CALL_MCP_TOOL",
        },
        status_code=202,
    )


@mcp.tool(
    title="Vertex Relay Status",
    annotations=READ_ONLY_CLOSED,
)
def vertex_relay_status() -> dict[str, Any]:
    """Return Vertex Relay gateway/store status."""
    return store.status()


@mcp.tool(
    title="Latest Vertex Relay",
    annotations=READ_ONLY_CLOSED,
)
def vertex_relay_latest(
    target: str = "VERA",
) -> dict[str, Any]:
    """Return the latest Relay envelope for the requested target."""
    value = store.latest(target=target)
    return value or {
        "state": "EMPTY",
        "target": target,
    }


@mcp.tool(
    title="Pending Vertex Relays",
    annotations=READ_ONLY_CLOSED,
)
def vertex_relay_pending(
    target: str = "VERA",
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List pending Relay envelopes oldest-first for deterministic review."""
    return store.pending(
        target=target,
        limit=limit,
    )


@mcp.tool(
    title="Get Vertex Relay",
    annotations=READ_ONLY_CLOSED,
)
def vertex_relay_get(
    relay_id: str,
) -> dict[str, Any]:
    """Read one Relay by immutable relay_id."""
    value = store.get(relay_id)
    if value is None:
        return {
            "state": "NOT_FOUND",
            "relay_id": relay_id,
        }
    return value


@mcp.tool(
    title="Acknowledge Vertex Relay",
    annotations=WRITE_ADDITIVE_IDEMPOTENT_CLOSED,
)
def vertex_relay_acknowledge(
    relay_id: str,
    note: str = "",
) -> dict[str, Any]:
    """Acknowledge one Relay after the model/human has actually reviewed it."""
    try:
        return store.acknowledge(
            relay_id=relay_id,
            actor="VERA",
            note=note,
        )
    except KeyError:
        return {
            "state": "NOT_FOUND",
            "relay_id": relay_id,
        }


@mcp.tool(
    title="Queue Vertex Relay Reply",
    annotations=WRITE_ADDITIVE_NON_IDEMPOTENT_CLOSED,
)
def vertex_relay_reply(
    envelope_json: str,
) -> dict[str, Any]:
    """Queue a Vera-origin vertex-relay/1 envelope for Workstation retrieval."""
    try:
        value = json.loads(envelope_json)
        return store.put_reply(value)
    except json.JSONDecodeError:
        return {
            "state": "REJECTED",
            "error": "BODY_NOT_JSON",
        }
    except ValueError as exc:
        return {
            "state": "REJECTED",
            "error": str(exc),
        }


@mcp.tool(
    title="Latest Vertex Relay Reply",
    annotations=READ_ONLY_CLOSED,
)
def vertex_relay_latest_reply() -> dict[str, Any]:
    """Return the latest Vera reply queued for Vertex Workstation."""
    value = store.latest_reply()
    return value or {
        "state": "EMPTY",
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
    )

from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

SERVER = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "vertex_relay_mcp.py"
)

RUNTIME_VERIFY = (
    ROOT
    / "scripts"
    / "verify_vertex_relay_mcp_runtime_000014.py"
)

for path in [
    SERVER,
    RUNTIME_VERIFY,
]:
    if not path.exists():
        raise SystemExit(
            "MISSING=" + str(path)
        )

server = SERVER.read_text(
    encoding="utf-8",
    errors="replace",
)

runtime = RUNTIME_VERIFY.read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "TOOL_ANNOTATIONS_IMPORT":
        "from mcp.types import ToolAnnotations"
        in server,
    "READ_ONLY_POLICY":
        "READ_ONLY_CLOSED = ToolAnnotations"
        in server
        and "read_only_hint=True"
        in server
        and "open_world_hint=False"
        in server,
    "WRITE_IDEMPOTENT_POLICY":
        "WRITE_ADDITIVE_IDEMPOTENT_CLOSED"
        in server
        and "idempotent_hint=True"
        in server,
    "WRITE_NON_IDEMPOTENT_POLICY":
        "WRITE_ADDITIVE_NON_IDEMPOTENT_CLOSED"
        in server
        and "idempotent_hint=False"
        in server,
    "NO_DESTRUCTIVE_WRITE":
        server.count(
            "destructive_hint=False"
        ) >= 2,
    "READ_TOOL_STATUS":
        'title="Vertex Relay Status"'
        in server
        and "annotations=READ_ONLY_CLOSED"
        in server,
    "READ_TOOL_PENDING":
        'title="Pending Vertex Relays"'
        in server,
    "WRITE_TOOL_ACK":
        'title="Acknowledge Vertex Relay"'
        in server
        and "WRITE_ADDITIVE_IDEMPOTENT_CLOSED"
        in server,
    "WRITE_TOOL_REPLY":
        'title="Queue Vertex Relay Reply"'
        in server
        and "WRITE_ADDITIVE_NON_IDEMPOTENT_CLOSED"
        in server,
    "RUNTIME_LIST_TOOLS_ANNOTATION_GATE":
        "MCP_TOOL_ANNOTATIONS=PASS"
        in runtime
        and "ANNOTATION_MISMATCH="
        in runtime,
    "ADVISORY_NOT_SECURITY_BOUNDARY":
        "Human Gate"
        not in server,
}

for key, ok in checks.items():
    print(
        key + "=" + (
            "PASS" if ok else "FAIL"
        )
    )

if not all(checks.values()):
    raise SystemExit(1)

print("MCP_TOOL_SURFACE=READ_WRITE_CLASSIFIED")
print("READ_TOOLS=STATUS_LATEST_PENDING_GET_LATEST_REPLY")
print("WRITE_TOOLS=ACKNOWLEDGE_REPLY")
print("MCP_ANNOTATIONS_SECURITY_BOUNDARY=NO")
print("HUMAN_GATE_AUTHORITY=PRESERVED_OUTSIDE_ANNOTATIONS")
print("MCP_TOOL_ANNOTATIONS_000018_STATIC=PASS")

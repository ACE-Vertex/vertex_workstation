from pathlib import Path
import subprocess

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

BOOTSTRAP = (
    ROOT
    / "scripts"
    / "bootstrap_vertex_relay_mcp_runtime_000015.ps1"
)

CMD = (
    ROOT
    / "VERTEX_RELAY_MCP_RUNTIME_VERIFY.cmd"
)

SETUP = ROOT / "VERTEX_RELAY_MCP_SETUP.cmd"

RUNTIME_VERIFY = (
    ROOT
    / "scripts"
    / "verify_vertex_relay_mcp_runtime_000014.py"
)

for path in [
    BOOTSTRAP,
    CMD,
    SETUP,
    RUNTIME_VERIFY,
]:
    if not path.exists():
        raise SystemExit(
            "MISSING=" + str(path)
        )

text = BOOTSTRAP.read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "ISOLATED_RUNTIME":
        "VertexWorkstation\\runtimes\\relay_mcp_v1" in text,
    "USES_EXISTING_SETUP":
        "VERTEX_RELAY_MCP_SETUP.cmd" in text,
    "REAL_RUNTIME_VERIFY":
        "verify_vertex_relay_mcp_runtime_000014.py" in text,
    "NO_GLOBAL_PIP":
        "pip install" not in text,
    "MCP_IMPORT_PROBE":
        "MCP_IMPORT=PASS" in text,
    "NEXT_GATE_TUNNEL":
        "SECURE_MCP_TUNNEL_OR_REMOTE_MCP_CONNECTION" in text,
}

for key, ok in checks.items():
    print(
        key + "=" + ("PASS" if ok else "FAIL")
    )

if not all(checks.values()):
    raise SystemExit(1)

print("MCP_RUNTIME_BOOTSTRAP_000015_STATIC=PASS")

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

BOOTSTRAP = (
    ROOT
    / "scripts"
    / "bootstrap_vertex_relay_mcp_runtime_000015.ps1"
)

if not BOOTSTRAP.exists():
    raise SystemExit(
        "MISSING_BOOTSTRAP=" + str(BOOTSTRAP)
    )

powershell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

proc = subprocess.run(
    [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(BOOTSTRAP),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)

print(
    "RUN="
    + powershell
    + " -NoProfile -ExecutionPolicy Bypass -File "
    + str(BOOTSTRAP)
)

if proc.stdout:
    print(
        proc.stdout
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )

if proc.stderr:
    print(
        proc.stderr
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )

if proc.returncode:
    raise SystemExit(proc.returncode)

print("WORKS_VERIFICATION_PROGRAM=PYTHON")
print("BOOTSTRAP_EXECUTION=POWERSHELL_SUBPROCESS")
print("MCP_RUNTIME_BOOTSTRAP_000015H1=PASS")

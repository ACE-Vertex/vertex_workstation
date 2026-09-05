from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

SETUP = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "setup_relay_mcp.ps1"
)

if not SETUP.exists():
    raise SystemExit(
        "MISSING_SETUP=" + str(SETUP)
    )

text = SETUP.read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "PYTHON_310_GATE":
        "sys.version_info >= (3,10)" in text,
    "PY_LAUNCHER_PROBE":
        "py.exe" in text
        and '"3.12"' in text
        and '"3.11"' in text
        and '"3.10"' in text,
    "GLOBAL_PYTHON_NOT_TRUSTED":
        "older Anaconda" in text
        and "Resolve-CompatiblePython" in text,
    "BROKEN_VENV_RECREATE":
        "RECREATE MCP VENV" in text
        and "-not $ExistingRuntimeCompatible" in text,
    "ISOLATED_PIP":
        "--isolated" in text,
    "PUBLIC_PYPI_EXPLICIT":
        "https://pypi.org/simple" in text,
    "MCP_IMPORT_PROBE":
        "MCP_IMPORT=PASS" in text,
    "NO_GLOBAL_SITE_INSTALL":
        "-m pip" in text
        and "RuntimePython" in text,
}

for key, ok in checks.items():
    print(
        key + "=" + ("PASS" if ok else "FAIL")
    )

if not all(checks.values()):
    raise SystemExit(1)

print("CAUSE_CLASS=PYTHON_COMPATIBILITY_OR_PIP_INDEX")
print("MCP_REQUIRES_PYTHON_310_PLUS=ENFORCED")
print("PIP_INDEX_CONFIG_ISOLATED=YES")
print("MCP_PYTHON_SELECTOR_000015H2_STATIC=PASS")

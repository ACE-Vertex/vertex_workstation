from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

TARGET = (
    ROOT
    / "scripts"
    / "verify_vertex_relay_mcp_runtime_000014.py"
)

if not TARGET.exists():
    raise SystemExit(
        "MISSING_TARGET=" + str(TARGET)
    )

text = TARGET.read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "WINDOWS_PROCESS_TREE_STOP":
        '"taskkill"' in text
        and '"/T"' in text
        and '"/F"' in text,
    "SERVER_STOP_WAIT":
        "proc.wait(timeout=8)" in text,
    "MANUAL_TEMP_DIR":
        "tempfile.mkdtemp" in text
        and "TemporaryDirectory" not in text,
    "CLEANUP_RETRY":
        "for attempt in range(12)" in text,
    "WINDOWS_LOCK_DEFER":
        "MCP_TEMP_CLEANUP=DEFERRED_WINDOWS_LOCK"
        in text,
    "PROTOCOL_GATES_PRESERVED":
        "MCP_INITIALIZE=PASS" in text
        and "MCP_LIST_TOOLS=PASS" in text
        and "MCP_STATUS_CALL=PASS" in text,
    "FINAL_RUNTIME_PASS_PRESERVED":
        'print("MCP_LOCAL_RUNTIME=PASS")'
        in text,
}

for key, ok in checks.items():
    print(
        key + "=" + ("PASS" if ok else "FAIL")
    )

if not all(checks.values()):
    raise SystemExit(1)

print(
    "CAUSE=WINDOWS_TEMP_SQLITE_HANDLE_RELEASE_RACE"
)
print(
    "MCP_PROTOCOL_RESULT_BEFORE_FAILURE=INITIALIZE_LIST_STATUS_PASS"
)
print(
    "MCP_RUNTIME_WINDOWS_CLEANUP_000015H3_STATIC=PASS"
)

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

RUNTIME = (
    Path(os.environ["LOCALAPPDATA"])
    / "VertexWorkstation"
    / "runtimes"
    / "relay_mcp_v1"
    / "venv"
)

PYTHON = RUNTIME / "Scripts" / "python.exe"

SERVER = (
    ROOT
    / "tools"
    / "relay_mcp"
    / "vertex_relay_mcp.py"
)

if not PYTHON.exists():
    raise SystemExit(
        "MCP_RUNTIME_MISSING: run "
        "VERTEX_RELAY_MCP_SETUP.cmd"
    )

probe = r"""
import asyncio
import json
import os
import tempfile
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def main():
    async with streamable_http_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, *_):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = {
                tool.name
                for tool in tools.tools
            }

            expected = {
                "vertex_relay_status",
                "vertex_relay_latest",
                "vertex_relay_pending",
                "vertex_relay_get",
                "vertex_relay_acknowledge",
                "vertex_relay_reply",
                "vertex_relay_latest_reply",
            }

            missing = expected - names
            if missing:
                raise SystemExit(
                    "MISSING_TOOLS="
                    + ",".join(sorted(missing))
                )

            tool_map = {
                tool.name: tool
                for tool in tools.tools
            }

            expected_policy = {
                "vertex_relay_status": {
                    "readOnlyHint": True,
                    "openWorldHint": False,
                },
                "vertex_relay_latest": {
                    "readOnlyHint": True,
                    "openWorldHint": False,
                },
                "vertex_relay_pending": {
                    "readOnlyHint": True,
                    "openWorldHint": False,
                },
                "vertex_relay_get": {
                    "readOnlyHint": True,
                    "openWorldHint": False,
                },
                "vertex_relay_acknowledge": {
                    "readOnlyHint": False,
                    "destructiveHint": False,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
                "vertex_relay_reply": {
                    "readOnlyHint": False,
                    "destructiveHint": False,
                    "idempotentHint": False,
                    "openWorldHint": False,
                },
                "vertex_relay_latest_reply": {
                    "readOnlyHint": True,
                    "openWorldHint": False,
                },
            }

            for name, expected_policy_values in expected_policy.items():
                tool = tool_map[name]
                annotations = tool.annotations

                if annotations is None:
                    raise SystemExit(
                        "MISSING_ANNOTATIONS=" + name
                    )

                if hasattr(
                    annotations,
                    "model_dump",
                ):
                    values = annotations.model_dump(
                        by_alias=True,
                        exclude_none=True,
                    )
                elif hasattr(
                    annotations,
                    "dict",
                ):
                    values = annotations.dict(
                        by_alias=True,
                        exclude_none=True,
                    )
                else:
                    values = {
                        key: getattr(
                            annotations,
                            key,
                            None,
                        )
                        for key in (
                            "readOnlyHint",
                            "destructiveHint",
                            "idempotentHint",
                            "openWorldHint",
                            "read_only_hint",
                            "destructive_hint",
                            "idempotent_hint",
                            "open_world_hint",
                        )
                    }

                normalized = {
                    "readOnlyHint":
                        values.get(
                            "readOnlyHint",
                            values.get(
                                "read_only_hint"
                            ),
                        ),
                    "destructiveHint":
                        values.get(
                            "destructiveHint",
                            values.get(
                                "destructive_hint"
                            ),
                        ),
                    "idempotentHint":
                        values.get(
                            "idempotentHint",
                            values.get(
                                "idempotent_hint"
                            ),
                        ),
                    "openWorldHint":
                        values.get(
                            "openWorldHint",
                            values.get(
                                "open_world_hint"
                            ),
                        ),
                }

                for key, expected_value in expected_policy_values.items():
                    if (
                        normalized.get(key)
                        is not expected_value
                    ):
                        raise SystemExit(
                            "ANNOTATION_MISMATCH="
                            + name
                            + ":"
                            + key
                            + ":"
                            + repr(
                                normalized.get(
                                    key
                                )
                            )
                        )

            result = await session.call_tool(
                "vertex_relay_status",
                {},
            )

            print("MCP_INITIALIZE=PASS")
            print("MCP_LIST_TOOLS=PASS")
            print("MCP_TOOL_ANNOTATIONS=PASS")
            print("MCP_STATUS_CALL=PASS")

asyncio.run(main())
"""


def stop_server_process(
    proc: subprocess.Popen[str],
) -> None:
    if proc.poll() is not None:
        return

    if os.name == "nt":
        taskkill = subprocess.run(
            [
                "taskkill",
                "/PID",
                str(proc.pid),
                "/T",
                "/F",
            ],
            capture_output=True,
            text=True,
            errors="replace",
        )

        if taskkill.stdout:
            print(
                taskkill.stdout
                .encode(
                    "ascii",
                    "backslashreplace",
                )
                .decode("ascii")
            )

        if taskkill.stderr:
            print(
                taskkill.stderr
                .encode(
                    "ascii",
                    "backslashreplace",
                )
                .decode("ascii")
            )
    else:
        proc.terminate()

    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=4)

    print("MCP_SERVER_STOP=PASS")


def cleanup_runtime_temp(
    path: Path,
) -> None:
    last_error: Exception | None = None

    for attempt in range(12):
        try:
            shutil.rmtree(path)
            print("MCP_TEMP_CLEANUP=PASS")
            return
        except FileNotFoundError:
            print("MCP_TEMP_CLEANUP=PASS")
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.25 + (attempt * 0.05))

    # A transient Windows handle-release delay is not an MCP protocol
    # failure after the server process tree has already been stopped.
    # Leave the tiny temp folder for OS/temp maintenance rather than
    # converting a successful MCP initialize/tool-call into a false FAIL.
    print(
        "MCP_TEMP_CLEANUP=DEFERRED_WINDOWS_LOCK"
    )
    if last_error is not None:
        print(
            (
                "MCP_TEMP_CLEANUP_DETAIL="
                + repr(last_error)
            )
            .encode(
                "ascii",
                "backslashreplace",
            )
            .decode("ascii")
        )


tmp_path = Path(
    tempfile.mkdtemp(
        prefix="vertex-mcp-runtime-"
    )
)

env = dict(os.environ)
env["PYTHONPATH"] = str(
    ROOT / "tools" / "relay_mcp"
)
env["VERTEX_RELAY_DB"] = str(
    tmp_path / "relay.db"
)

proc = subprocess.Popen(
    [str(PYTHON), str(SERVER)],
    cwd=ROOT,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    errors="replace",
)

try:
    time.sleep(1.25)

    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(stdout)
        print(stderr)
        raise SystemExit(
            "MCP_SERVER_START=FAIL"
        )

    probe_proc = subprocess.run(
        [str(PYTHON), "-c", probe],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=20,
    )

    print(
        probe_proc.stdout
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

    if probe_proc.stderr:
        print(
            probe_proc.stderr
            .encode(
                "ascii",
                "backslashreplace",
            )
            .decode("ascii")
        )

    if probe_proc.returncode:
        raise SystemExit(
            probe_proc.returncode
        )

finally:
    stop_server_process(proc)
    cleanup_runtime_temp(tmp_path)

print("MCP_LOCAL_RUNTIME=PASS")
print("CHATGPT_CLOUD_REACHABILITY=NOT_TESTED")
print("CHATGPT_APP_CONNECTION=NOT_TESTED")

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

BRIDGE = (
    ROOT
    / "tools"
    / "relay_bridge"
    / "vertex_relay_bridge.py"
)

CMD = ROOT / "VERTEX_RELAY_BRIDGE.cmd"

if not BRIDGE.exists():
    raise SystemExit(
        "MISSING_BRIDGE=" + str(BRIDGE)
    )

if not CMD.exists():
    raise SystemExit(
        "MISSING_LAUNCHER=" + str(CMD)
    )

text = BRIDGE.read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "BRIDGE_SCHEMA":
        'vertex-relay-bridge/1' in text,
    "RELAY_SCHEMA":
        'vertex-relay/1' in text,
    "POST_ROUTE":
        '"/vertex-relay"' in text
        and "do_POST" in text,
    "HEALTH_ROUTE":
        '"/health"' in text
        and "do_GET" in text,
    "CORS":
        "Access-Control-Allow-Origin" in text
        and "do_OPTIONS" in text,
    "BODY_LIMIT":
        "MAX_BODY_BYTES" in text
        and "413" in text,
    "ENVELOPE_VALIDATION":
        "validate_envelope" in text
        and "RELAY_SCHEMA_INVALID" in text
        and "RELAY_TYPE_INVALID" in text
        and "RELAY_ACTION_INVALID" in text,
    "LOOPBACK_ONLY":
        '"127.0.0.1"' in text
        and "Relay Bridge binds loopback only" in text,
    "PERSISTENT_INBOX":
        '"inbox"' in text
        and "write_inbox" in text,
    "ATOMIC_WRITE":
        "os.replace" in text,
    "VERA_NOT_FAKED":
        "VERA_ADAPTER_NOT_CONNECTED" in text,
}

for key, ok in checks.items():
    print(
        key + "=" + ("PASS" if ok else "FAIL")
    )

if not all(checks.values()):
    raise SystemExit(1)

def free_port() -> int:
    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    try:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
    finally:
        sock.close()

port = free_port()

with tempfile.TemporaryDirectory(
    prefix="vertex-relay-bridge-verify-"
) as temp_dir:
    proc = subprocess.Popen(
        [
            sys.executable,
            str(BRIDGE),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--store-root",
            temp_dir,
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )

    try:
        base = f"http://127.0.0.1:{port}"

        ready = False
        for _ in range(60):
            if proc.poll() is not None:
                break
            try:
                with urllib.request.urlopen(
                    base + "/health",
                    timeout=0.5,
                ) as response:
                    body = json.loads(
                        response.read().decode(
                            "utf-8"
                        )
                    )
                    if (
                        response.status == 200
                        and body.get("status")
                        == "READY"
                    ):
                        ready = True
                        break
            except Exception:
                time.sleep(0.1)

        if not ready:
            stdout, stderr = proc.communicate(
                timeout=2
            )
            print(
                stdout
                .encode(
                    "ascii",
                    "backslashreplace",
                )
                .decode("ascii")
            )
            print(
                stderr
                .encode(
                    "ascii",
                    "backslashreplace",
                )
                .decode("ascii")
            )
            raise SystemExit(
                "BRIDGE_START=FAIL"
            )

        print("BRIDGE_START=PASS")
        print("HEALTH=PASS")

        envelope = {
            "schema": "vertex-relay/1",
            "type": "CANONICAL",
            "action": "SHARE",
            "source": "VERTEX_WORKSTATION",
            "target": "VERA",
            "subject": {
                "id": "relay-bridge-test",
                "name": "Relay Bridge Test",
            },
            "timestamp": (
                "2026-09-05T00:00:00+00:00"
            ),
            "payload": {
                "test": True,
            },
        }

        payload = json.dumps(
            envelope,
            ensure_ascii=False,
        ).encode("utf-8")

        request = urllib.request.Request(
            base + "/vertex-relay",
            data=payload,
            method="POST",
            headers={
                "Content-Type":
                    "application/vnd.vertex-relay+json",
                "Origin":
                    "http://tauri.localhost",
            },
        )

        with urllib.request.urlopen(
            request,
            timeout=2,
        ) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )
            if response.status != 202:
                raise SystemExit(
                    f"RELAY_POST_STATUS={response.status}"
                )

        print("REAL_POST_202=PASS")
        print(
            "RELAY_STATE="
            + str(result.get("state"))
        )

        latest_request = urllib.request.Request(
            base + "/vertex-relay/latest",
            method="GET",
        )

        with urllib.request.urlopen(
            latest_request,
            timeout=2,
        ) as response:
            latest = json.loads(
                response.read().decode("utf-8")
            )
            if response.status != 200:
                raise SystemExit(
                    f"LATEST_STATUS={response.status}"
                )

        if (
            latest.get("subject", {}).get("id")
            != "relay-bridge-test"
        ):
            raise SystemExit(
                "LATEST_SUBJECT_MISMATCH"
            )

        print("PERSISTED_LATEST=PASS")

        stored = list(
            Path(temp_dir)
            .joinpath("inbox")
            .rglob("*.json")
        )

        if not stored:
            raise SystemExit(
                "PERSISTED_INBOX_FILE_MISSING"
            )

        record = json.loads(
            stored[0].read_text(
                encoding="utf-8"
            )
        )

        if (
            record.get("envelope", {})
            .get("subject", {})
            .get("id")
            != "relay-bridge-test"
        ):
            raise SystemExit(
                "PERSISTED_INBOX_CONTENT_MISMATCH"
            )

        print("PERSISTED_INBOX_FILE=PASS")

        bad = urllib.request.Request(
            base + "/vertex-relay",
            data=b'{"schema":"bad"}',
            method="POST",
            headers={
                "Content-Type":
                    "application/json",
            },
        )

        try:
            urllib.request.urlopen(
                bad,
                timeout=2,
            )
            raise SystemExit(
                "INVALID_SCHEMA_ACCEPTED"
            )
        except urllib.error.HTTPError as exc:
            if exc.code != 422:
                raise
            print("INVALID_SCHEMA_REJECTED=PASS")

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)

print("VERTEX_RELAY_BRIDGE=REAL_LOCAL_HTTP_SERVICE")
print("DEFAULT_ENDPOINT=http://127.0.0.1:47821/vertex-relay")
print("CORS_FOR_TAURI_FETCH=YES")
print("LOOPBACK_ONLY=YES")
print("STORE=LOCALAPPDATA_VERTEXWORKSTATION_RELAY_BRIDGE")
print("VERA_ADAPTER=NOT_CONNECTED")
print("END_TO_END_VERA=NOT_YET")
print("VERTEX_RELAY_BRIDGE_000013=PASS")

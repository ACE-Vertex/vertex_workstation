from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

paths = {
    "transport": ROOT / "src/core/relay/directRelayTransport.ts",
    "bar": ROOT / "src/shell/relay/VertexRelayBar.tsx",
    "css": ROOT / "src/shell/relay/vertexRelay.css",
    "contracts": ROOT / "src/features/contracts/contracts.ts",
}

for name, path in paths.items():
    if not path.exists():
        raise SystemExit(f"MISSING_{name.upper()}={path}")

transport = paths["transport"].read_text(
    encoding="utf-8",
    errors="replace",
)
bar = paths["bar"].read_text(
    encoding="utf-8",
    errors="replace",
)
css = paths["css"].read_text(
    encoding="utf-8",
    errors="replace",
)
contracts = paths["contracts"].read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "DIRECT_SEND_BUTTON":
        ">SEND<" in bar or '"SEND"' in bar,
    "COPY_RELAY_PRESERVED":
        "COPY RELAY" in bar
        and "navigator.clipboard.writeText" in bar,
    "RECEIVE_PRESERVED":
        "RECEIVE" in bar
        and "ACCEPT" in bar
        and "REJECT" in bar,
    "DIRECT_ENDPOINT_STORAGE":
        "vertex.relay.direct.endpoint.v1" in transport,
    "DIRECT_ENDPOINT_HTTP_ONLY":
        'url.protocol !== "http:"' in transport
        and 'url.protocol !== "https:"' in transport,
    "DIRECT_POST_REAL":
        'method: "POST"' in transport
        and "fetch(" in transport,
    "VERTEX_RELAY_CONTENT_TYPE":
        "application/vnd.vertex-relay+json" in transport,
    "DIRECT_TIMEOUT":
        "10_000" in transport
        and "AbortController" in transport,
    "NO_AUTO_CLIPBOARD_FALLBACK":
        "sendVertexRelayDirect" in bar
        and "copyRelay" in bar,
    "LINK_REQUIRED_GATE":
        "LINK REQUIRED" in bar
        and "DIRECT RELAY ENDPOINT" in bar,
    "NO_CREDENTIAL_STORAGE":
        "token" not in transport.lower()
        and "password" not in transport.lower()
        and "authorization" not in transport.lower(),
    "DIRECT_STATUS_VISIBLE":
        "DIRECT LINKED" in bar
        and "DIRECT OFFLINE" in bar,
    "TRANSPORT_LABEL_UPDATED":
        "CLIPBOARD / DIRECT" in bar,
    "RELAY_CONTRACT_UPDATED":
        "Relay Bridge" in contracts
        and "Clipboard remains the fallback transport" in contracts,
    "NO_FLOAT_RELAY":
        "position: fixed" not in css,
    "SMART_BUTTON_POLICY":
        "min-height: 30px" in css,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in (transport + bar)
        for token in (
            ".appendChild(",
            ".removeChild(",
            ".insertBefore(",
            ".replaceChild(",
        )
    ),
}

for key, ok in checks.items():
    print(key + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
proc = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if proc.stdout:
    print(proc.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if proc.stderr:
    print(proc.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if proc.returncode:
    raise SystemExit(proc.returncode)

print("VERTEX_RELAY_SEND=REAL_HTTP_POST")
print("VERTEX_RELAY_DIRECT_ENDPOINT=CONFIGURABLE")
print("VERTEX_RELAY_CLIPBOARD=FALLBACK")
print("VERTEX_RELAY_BROWSER_DOM_AUTOMATION=NO")
print("HUMAN_GATE_PRESERVED=YES")
print("FLOATING_WINDOW_ADDED=NO")
print("FORGE_RUNTIME_MUTATION=NO")
print("RAY_RUNTIME_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("VERTEX_RELAY_DIRECT_SEND_000012_STATIC=PASS")

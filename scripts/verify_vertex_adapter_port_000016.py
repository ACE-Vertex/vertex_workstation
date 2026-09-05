from pathlib import Path
import subprocess

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

paths = {
    "types":
        ROOT / "src/core/adapters/types.ts",
    "registry":
        ROOT / "src/core/adapters/registry.ts",
    "port":
        ROOT / "src/core/adapters/relayAdapterPort.ts",
    "transport":
        ROOT / "src/core/relay/directRelayTransport.ts",
    "bar":
        ROOT / "src/shell/relay/VertexRelayBar.tsx",
    "css":
        ROOT / "src/shell/relay/vertexRelay.css",
    "contracts":
        ROOT / "src/features/contracts/contracts.ts",
}

for name, path in paths.items():
    if not path.exists():
        raise SystemExit(
            f"MISSING_{name.upper()}={path}"
        )

texts = {
    name: path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for name, path in paths.items()
}

joined = "\n".join(texts.values())

checks = {
    "ADAPTER_PORT_KEY":
        "vertex.adapter.port.active.v1"
        in texts["port"],
    "ADAPTER_REGISTRY":
        "class VertexAdapterRegistry"
        in texts["registry"],
    "DUPLICATE_ID_GATE":
        "ADAPTER_DUPLICATE_ID"
        in texts["registry"],
    "REAL_HTTP_ADAPTER":
        "VERTEX_RELAY_HTTP"
        in texts["port"]
        and "sendVertexRelayDirect"
        in texts["port"],
    "CHATGPT_MCP_SLOT":
        "CHATGPT_MCP"
        in texts["port"]
        and "EXTERNAL_GATE"
        in texts["port"],
    "OPENAI_API_SLOT":
        "OPENAI_API"
        in texts["port"],
    "OPENAI_API_REAL_ADAPTER":
        "sendVertexRelayViaOpenAiApi"
        in texts["port"]
        and 'state: "READY"'
        in texts["port"],
    "LOCAL_LLM_SLOT":
        "LOCAL_LLM"
        in texts["port"],
    "HYPER_AGENT_SLOT":
        "HYPER_AGENT"
        in texts["port"],
    "NO_FAKE_PROVIDER_SEND":
        (
            "ADAPTER_EXTERNAL_GATE"
            in texts["port"]
        )
        or (
            "ADAPTER_ROUTE_BLOCKED"
            in texts["port"]
            and "evaluateVertexAdapterRoute"
            in texts["port"]
            and "sendable: false"
            in texts["port"]
        ),
    "UI_ADAPTER_SELECTOR":
        "ADAPTER" in texts["bar"]
        and "listVertexAdapters"
        in texts["bar"]
        and "changeAdapter"
        in texts["bar"],
    "CLIPBOARD_FALLBACK_PRESERVED":
        "COPY RELAY"
        in texts["bar"]
        and "navigator.clipboard.writeText"
        in texts["bar"],
    "RECEIVE_HUMAN_GATE_PRESERVED":
        "RECEIVE"
        in texts["bar"]
        and "ACCEPT"
        in texts["bar"]
        and "REJECT"
        in texts["bar"],
    "DIRECT_HTTP_TRANSPORT_REAL":
        'method: "POST"'
        in texts["transport"]
        and "fetch("
        in texts["transport"],
    "PROVIDER_CREDENTIAL_NOT_EMBEDDED":
        all(
            token not in joined.lower()
            for token in (
                "sk-",
                "api_key=",
                "authorization: bearer",
                "password=",
            )
        ),
    "ADAPTER_CONTRACT":
        'title: "Adapter Boundary"'
        in texts["contracts"]
        and "門番はCoreの停止理由ではなく"
        in texts["contracts"],
    "NO_FLOAT_ADAPTER_UI":
        "position: fixed"
        not in texts["css"],
    "NO_DOM_INJECTION":
        all(
            token not in joined
            for token in (
                ".appendChild(",
                ".removeChild(",
                ".insertBefore(",
                ".replaceChild(",
            )
        ),
}

for key, ok in checks.items():
    print(
        key + "=" + (
            "PASS" if ok else "FAIL"
        )
    )

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
    print(
        proc.stdout
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if proc.stderr:
    print(
        proc.stderr
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if proc.returncode:
    raise SystemExit(
        proc.returncode
    )

print("VERTEX_ADAPTER_PORT=REAL_REGISTRY_BOUNDARY")
print("REAL_ACTIVE_ADAPTER=VERTEX_RELAY_HTTP")
print("CHATGPT_MCP=EXTERNAL_GATE_NOT_FAKED")
print("OPENAI_API=REAL_TAURI_RESPONSES_ADAPTER")
print("LOCAL_LLM=ADAPTER_SLOT_ONLY")
print("HYPER_AGENT=ADAPTER_SLOT_ONLY")
print("PROVIDER_GATE_CORE_COUPLING=NO")
print("HUMAN_GATE_PRESERVED=YES")
print("FLOATING_WINDOW_ADDED=NO")
print("VERTEX_ADAPTER_PORT_000016_STATIC=PASS")
print("NO_FAKE_PROVIDER_SEND_GUARD=000016_OR_000017_EVOLVED")

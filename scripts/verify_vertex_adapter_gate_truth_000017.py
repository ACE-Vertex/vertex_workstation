from pathlib import Path
import subprocess

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

paths = {
    "types":
        ROOT / "src/core/adapters/types.ts",
    "port":
        ROOT / "src/core/adapters/relayAdapterPort.ts",
    "bar":
        ROOT / "src/shell/relay/VertexRelayBar.tsx",
    "contracts":
        ROOT / "src/features/contracts/contracts.ts",
    "transport":
        ROOT / "src/core/relay/directRelayTransport.ts",
}

for name, path in paths.items():
    if not path.exists():
        raise SystemExit(
            f"MISSING_{name.upper()}={path}"
        )

text = {
    name: path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for name, path in paths.items()
}

checks = {
    "ROUTE_EVALUATION_TYPE":
        "VertexAdapterRouteEvaluation"
        in text["types"],
    "ROUTE_EVALUATOR_OWNER":
        "evaluateVertexAdapterRoute"
        in text["port"],
    "HTTP_LINK_REQUIRED_CORE_OWNED":
        "VERTEX_RELAY_HTTP_ENDPOINT_REQUIRED"
        in text["port"],
    "CHATGPT_EXTERNAL_GATE_CORE_OWNED":
        '"EXTERNAL_GATE"'
        in text["port"]
        and "adapter.descriptor.gate"
        in text["port"],
    "UNCONFIGURED_CORE_OWNED":
        '"UNCONFIGURED"'
        in text["port"],
    "SEND_ENFORCES_ROUTE":
        "ADAPTER_ROUTE_BLOCKED"
        in text["port"],
    "NO_FAKE_EXTERNAL_SEND":
        "sendable: false"
        in text["port"]
        and "CHATGPT_MCP"
        in text["port"],
    "UI_ASKS_CORE_ROUTE":
        "evaluateVertexAdapterRoute"
        in text["bar"],
    "UI_DOES_NOT_OWN_PROVIDER_GATE":
        '"EXTERNAL_GATE"'
        not in text["bar"]
        and '"UNCONFIGURED"'
        not in text["bar"]
        and "evaluateVertexAdapterRoute"
        in text["bar"],
    "LINK_EDITOR_STILL_AVAILABLE":
        "setLinkOpen(true)"
        in text["bar"],
    "REAL_HTTP_POST_PRESERVED":
        'method: "POST"'
        in text["transport"]
        and "fetch("
        in text["transport"],
    "HUMAN_GATE_PRESERVED":
        "ACCEPT"
        in text["bar"]
        and "REJECT"
        in text["bar"],
    "CONTRACT_ROUTE_TRUTH":
        "Presentation must ask Adapter Port for route truth"
        in text["contracts"],
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
    raise SystemExit(proc.returncode)

print("GATEKEEPER_OWNER=VERTEX_ADAPTER_PORT")
print("PRESENTATION_GATE_LOGIC=DIRECT_PROVIDER_CHECK_REMOVED")
print("CHATGPT_MCP_ROUTE=EXTERNAL_GATE")
print("CHATGPT_MCP_FAKE_SEND=NO")
print("VERTEX_RELAY_HTTP_ROUTE=REAL")
print("VERTEX_ADAPTER_GATE_TRUTH_000017_STATIC=PASS")

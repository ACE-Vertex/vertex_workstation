from pathlib import Path
import subprocess

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)

paths = {
    "cargo":
        ROOT / "src-tauri/Cargo.toml",
    "lib":
        ROOT / "src-tauri/src/lib.rs",
    "rust":
        ROOT / "src-tauri/src/openai_api.rs",
    "openai_ts":
        ROOT / "src/core/adapters/openAiApiAdapter.ts",
    "types":
        ROOT / "src/core/adapters/types.ts",
    "port":
        ROOT / "src/core/adapters/relayAdapterPort.ts",
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

text = {
    name: path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for name, path in paths.items()
}

frontend_joined = "\n".join([
    text["openai_ts"],
    text["types"],
    text["port"],
    text["bar"],
    text["css"],
])

checks = {
    "REQWEST_RUSTLS":
        'reqwest = { version = "0.12"'
        in text["cargo"]
        and '"rustls-tls"'
        in text["cargo"],
    "TAURI_COMMAND_STATUS":
        "openai_api_status"
        in text["lib"]
        and "#[tauri::command]"
        in text["rust"],
    "TAURI_COMMAND_SEND":
        "openai_api_send_relay"
        in text["lib"]
        and "pub async fn openai_api_send_relay"
        in text["rust"],
    "RESPONSES_API_ENDPOINT":
        "https://api.openai.com/v1/responses"
        in text["rust"],
    "USER_OWNED_ENV_CREDENTIAL":
        'env::var("OPENAI_API_KEY")'
        in text["rust"]
        and 'env::var("OPENAI_MODEL")'
        in text["rust"],
    "DEFAULT_MODEL_GPT_5_6":
        'DEFAULT_OPENAI_MODEL'
        in text["rust"]
        and '"gpt-5.6"'
        in text["rust"],
    "BEARER_AUTH_BACKEND_ONLY":
        ".bearer_auth(api_key)"
        in text["rust"]
        and ".bearer_auth"
        not in frontend_joined,
    "NO_RAW_KEY_IN_STATUS":
        "credential_source"
        in text["rust"]
        and "api_key:"
        not in text["rust"].lower(),
    "RELAY_SCHEMA_DIRECTION_GATE":
        'schema != "vertex-relay/1"'
        in text["rust"]
        and 'source != "VERTEX_WORKSTATION"'
        in text["rust"]
        and 'target != "VERA"'
        in text["rust"],
    "OPENAI_REAL_ADAPTER":
        "sendVertexRelayViaOpenAiApi"
        in text["port"]
        and 'id: "OPENAI_API"'
        in text["port"]
        and 'state: "READY"'
        in text["port"],
    "OPENAI_RUNTIME_ROUTE_GATE":
        "openAiApiAvailable"
        in text["port"]
        and "openAiApiConfigured"
        in text["port"]
        and "OPENAI_API_KEY_REQUIRED"
        in text["port"],
    "PRESENTATION_ASKS_CORE_ROUTE":
        "evaluateVertexAdapterRoute"
        in text["bar"]
        and "adapterRuntime"
        in text["bar"],
    "PRESENTATION_QUERIES_BACKEND_STATUS":
        "getOpenAiApiRuntimeStatus"
        in text["bar"],
    "API_KEY_NOT_IN_LOCALSTORAGE":
        "OPENAI_API_KEY"
        not in text["bar"]
        and "OPENAI_API_KEY"
        not in text["openai_ts"],
    "PROVIDER_RESPONSE_DOCK":
        "OPENAI RESPONSE · HUMAN REVIEW"
        in text["bar"]
        and "providerResponse"
        in text["bar"],
    "NO_AUTO_APPLY_PROVIDER_RESPONSE":
        "review-only"
        in text["bar"]
        and "onReceive?.("
        in text["bar"],
    "PROCESSING_ANIMATION":
        "vertex-relay-processing"
        in text["bar"]
        and "@keyframes vertex-relay-processing-pulse"
        in text["css"],
    "NO_FLOAT":
        "position: fixed"
        not in text["css"],
    "CHATGPT_MCP_EXTERNAL_GATE_PRESERVED":
        'id: "CHATGPT_MCP"'
        in text["port"]
        and 'state: "EXTERNAL_GATE"'
        in text["port"],
    "CONTRACT_BACKEND_CREDENTIAL_OWNERSHIP":
        "OpenAI API credentials are read only by the Tauri/Rust backend"
        in text["contracts"],
    "CONTRACT_RESPONSE_HUMAN_REVIEW":
        "Provider responses remain review-only"
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

cargo = "cargo"
proc = subprocess.run(
    [
        cargo,
        "test",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
        "--lib",
        "openai_api::tests",
        "--",
        "--nocapture",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)

print(
    "RUN=cargo test --manifest-path "
    + str(ROOT / "src-tauri/Cargo.toml")
    + " --lib openai_api::tests"
)

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

print("OPENAI_API_TRANSPORT=TAURI_RUST_RESPONSES_API")
print("OPENAI_API_CREDENTIAL=USER_OWNED_ENV_ONLY")
print("OPENAI_API_KEY_FRONTEND_EXPOSURE=NO")
print("OPENAI_API_RESPONSE_AUTO_APPLY=NO")
print("CHATGPT_MCP_EXTERNAL_GATE=PRESERVED")
print("OPENAI_API_ADAPTER_000019=PASS")

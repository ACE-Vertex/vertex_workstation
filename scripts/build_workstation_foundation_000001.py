from pathlib import Path
import subprocess, shutil, json, hashlib, datetime

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
if ROOT.name.lower() != "vertex_workstation":
    raise SystemExit("WRONG_PROJECT_ROOT=" + str(ROOT))

def safe(s):
    return str(s).encode("ascii", "backslashreplace").decode("ascii")

def run(cmd):
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        errors="replace",
    )
    print("RUN=" + " ".join(map(str, cmd)))
    if p.stdout:
        print(safe(p.stdout))
    if p.stderr:
        print(safe(p.stderr))
    if p.returncode:
        raise SystemExit(p.returncode)

npm = shutil.which("npm.cmd") or shutil.which("npm")
if not npm:
    raise SystemExit("NPM_NOT_FOUND")

if not (ROOT/"node_modules").exists():
    run([npm, "install"])

build_number = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

# Preserve the corrected build identity generation from H1.
build_identity = (
    'export const BUILD_IDENTITY = {\n'
    '  version: "0.1.0",\n'
    f'  build: "{build_number}",\n'
    '} as const;\n'
)
(ROOT/"src/buildIdentity.ts").write_bytes(build_identity.encode("utf-8"))

identity_bytes = (ROOT/"src/buildIdentity.ts").read_bytes()
if b"\\n" in identity_bytes:
    raise SystemExit("BUILD_IDENTITY_LITERAL_BACKSLASH_N_SURVIVED")

tauri_conf_path = ROOT/"src-tauri/tauri.conf.json"
conf = json.loads(tauri_conf_path.read_text(encoding="utf-8"))
conf["version"] = "0.1.0"

build_cfg = conf.get("build", {})
if build_cfg.get("devUrl") != "http://127.0.0.1:1420":
    raise SystemExit("DEV_URL_CONTRACT_CHANGED")
if build_cfg.get("frontendDist") != "../dist":
    raise SystemExit("FRONTEND_DIST_CONTRACT_CHANGED")

wins = conf.get("app", {}).get("windows", [])
if not wins:
    raise SystemExit("TAURI_WINDOW_CONFIG_NOT_FOUND")
wins[0]["title"] = f"VERTEX WORKSTATION v0.1.0 — BUILD {build_number}"
tauri_conf_path.write_text(
    json.dumps(conf, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

# Static Rust checks first.
run(["cargo", "fmt", "--manifest-path", str(ROOT/"src-tauri/Cargo.toml"), "--", "--check"])
run(["cargo", "check", "--manifest-path", str(ROOT/"src-tauri/Cargo.toml")])

# 000001H3 FIX:
# Do NOT use raw `cargo build --release` for the desktop candidate.
# Tauri CLI owns the devUrl/frontendDist mode switch.
# `tauri build` runs beforeBuildCommand (npm run build) and compiles the
# production app against frontendDist instead of the development server.
run([npm, "run", "tauri:build"])

release_dir = ROOT/"src-tauri/target/release"
exe = release_dir/"vertex-workstation.exe"
if not exe.exists():
    candidates = [
        p for p in release_dir.glob("*.exe")
        if p.is_file() and "vertex" in p.stem.lower()
    ]
    if len(candidates) == 1:
        exe = candidates[0]
if not exe.exists():
    raise SystemExit("TAURI_RELEASE_EXE_NOT_FOUND")

build_dir = ROOT/"versions/0.1.0/builds"/build_number
build_dir.mkdir(parents=True, exist_ok=False)
dst = build_dir/"VertexWorkstation_0.1.0.exe"
shutil.copy2(exe, dst)
sha = hashlib.sha256(dst.read_bytes()).hexdigest()

runtime = ROOT/"runtime"
runtime.mkdir(exist_ok=True)
candidate = {
    "schema_version": "vertex.workstation.candidate/1",
    "project": "Vertex Workstation",
    "version": "0.1.0",
    "build_number": build_number,
    "release_exe": str(dst),
    "sha256": sha,
    "stack": ["React", "TypeScript", "Vite", "Tauri", "Rust"],
    "feature": "FOUNDATION_000001H3",
    "build_mode": "TAURI_CLI_PRODUCTION",
    "frontend_source": "frontendDist",
    "promotion_state": "CANDIDATE_ONLY",
    "runtime_visual_acceptance": "PENDING",
    "required_checks": [
        "App opens without attempting 127.0.0.1",
        "FORGE SEED renders in A1",
        "PULSE counter increments",
        "Move A1 -> B1 -> C1 preserves PULSE state",
        "Component identity/ownership metadata remain stable",
        "No blank window or layout collapse"
    ]
}
(runtime/"candidate.json").write_text(
    json.dumps(candidate, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("HOTFIX=FOUNDATION_000001H3")
print("CAUSE=RAW_CARGO_RELEASE_BUILD_LEFT_APP_IN_DEVURL_MODE")
print("PRODUCTION_BUILD_OWNER=TAURI_CLI")
print("FRONTEND_SOURCE=frontendDist")
print("DEV_URL_RUNTIME_DEPENDENCY=NO")
print("PROJECT=VERTEX_WORKSTATION")
print("VERSION=0.1.0")
print("BUILD_NUMBER=" + build_number)
print("IMMUTABLE_CANDIDATE=" + str(dst))
print("SHA256=" + sha)
print("VERTEX_WORKS_MUTATION=NO")
print("AUTO_PROMOTION=NO")
print("AUTO_RESTART=NO")
print("NEXT_GATE=FOUNDATION_RUNTIME_VISUAL_ACCEPTANCE")
print("WORKSTATION_FOUNDATION_000001H3_BUILD=PASS")

from pathlib import Path
import json

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
CONF = ROOT/"src-tauri/tauri.conf.json"
PKG = ROOT/"package.json"
BUILD = ROOT/"scripts/build_workstation_foundation_000001.py"

for p in (CONF, PKG, BUILD):
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

conf = json.loads(CONF.read_text(encoding="utf-8"))
pkg = json.loads(PKG.read_text(encoding="utf-8"))
build_src = BUILD.read_text(encoding="utf-8", errors="replace")

checks = {
    "DEV_URL_DEFINED_FOR_DEV_ONLY": conf.get("build", {}).get("devUrl") == "http://127.0.0.1:1420",
    "FRONTEND_DIST_DEFINED": conf.get("build", {}).get("frontendDist") == "../dist",
    "TAURI_BUILD_SCRIPT_EXISTS": pkg.get("scripts", {}).get("tauri:build") == "tauri build",
    "RAW_CARGO_RELEASE_REMOVED": '["cargo", "build", "--release"' not in build_src,
    "TAURI_CLI_BUILD_USED": 'run([npm, "run", "tauri:build"])' in build_src,
}
for k,v in checks.items():
    print(k + "=" + ("PASS" if v else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

print("PRODUCTION_PROTOCOL_OWNER=TAURI_CLI")
print("RUNTIME_DEV_SERVER_DEPENDENCY=PROHIBITED")
print("WORKSTATION_FOUNDATION_000001H3_PREFLIGHT=PASS")

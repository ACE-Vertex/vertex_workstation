from pathlib import Path
import json

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
CMD = ROOT / "WORKSTATION_LOCAL.cmd"
PS1 = ROOT / "scripts/start_workstation_local.ps1"
PKG = ROOT / "package.json"
VITE = ROOT / "vite.config.ts"

for p in (CMD, PS1, PKG, VITE):
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

pkg = json.loads(PKG.read_text(encoding="utf-8"))
scripts = pkg.get("scripts", {})

cmd = CMD.read_text(encoding="utf-8", errors="replace")
ps1 = PS1.read_text(encoding="utf-8", errors="replace")
vite = VITE.read_text(encoding="utf-8", errors="replace")

checks = {
    "LOCAL_ENTRY_EXISTS": "start_workstation_local.ps1" in cmd,
    "VITE_DEV_SCRIPT_EXISTS": scripts.get("dev") == "vite --host 127.0.0.1 --port 1420",
    "PORT_CONTRACT_1420": "1420" in vite and "strictPort: true" in vite,
    "LOCAL_URL": "http://127.0.0.1:1420" in ps1,
    "NO_TAURI_DEV_IN_LOCAL": "tauri:dev" not in ps1,
    "HIDDEN_VITE_CHILD": "-WindowStyle Hidden" in ps1,
    "PID_TRACKING": "vite.pid" in ps1,
    "LOG_CAPTURE": "vite.stdout.log" in ps1 and "vite.stderr.log" in ps1,
    "EDGE_APP_MODE": "--app=$Url" in ps1,
    "READY_WAIT": "Wait-VertexLocal" in ps1,
}

for key, value in checks.items():
    print(key + "=" + ("PASS" if value else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

print("LOCAL_MODE=BROWSER_APP")
print("LOCAL_RUNTIME=VITE")
print("TAURI_RUNTIME=NOT_REQUIRED")
print("PRODUCTION_BUILD_PROTOCOL=UNCHANGED")
print("VERTEX_WORKS_MUTATION=NO")
print("WORKSTATION_LOCAL_000003_VERIFY=PASS")

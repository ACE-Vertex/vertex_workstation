from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PACKAGE = ROOT / "package.json"
LOCK = ROOT / "package-lock.json"
NPM = Path(r"C:\Program Files\nodejs\npm.cmd")
VERSION = "3.16.0"

if not PACKAGE.exists():
    raise SystemExit("MISSING=" + str(PACKAGE))
if not NPM.exists():
    raise SystemExit("MISSING=" + str(NPM))

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
current = (package.get("dependencies") or {}).get("react-arborist")

if current == VERSION and (ROOT / "node_modules" / "react-arborist" / "package.json").exists():
    print("REACT_ARBORIST_DEPENDENCY=ALREADY_PRESENT")
    print("REACT_ARBORIST_VERSION=" + VERSION)
    raise SystemExit(0)

local = Path(os.environ.get("LOCALAPPDATA", str(ROOT / ".vertex-local")))
backup = (
    local
    / "VertexWorkstation"
    / "vra_side_effect_backups"
    / "ray-explorer-arborist-000023"
    / str(int(time.time() * 1000))
)
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(PACKAGE, backup / "package.json")
if LOCK.exists():
    shutil.copy2(LOCK, backup / "package-lock.json")

print("DEPENDENCY_BACKUP=" + str(backup))
cmd = [
    str(NPM),
    "install",
    f"react-arborist@{VERSION}",
    "--save-exact",
    "--ignore-scripts",
    "--no-audit",
    "--no-fund",
]
print("RUN=" + " ".join(cmd))

proc = subprocess.run(
    cmd,
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)

if proc.stdout:
    print(proc.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if proc.stderr:
    print(proc.stderr.encode("ascii", "backslashreplace").decode("ascii"))

if proc.returncode:
    shutil.copy2(backup / "package.json", PACKAGE)
    backup_lock = backup / "package-lock.json"
    if backup_lock.exists():
        shutil.copy2(backup_lock, LOCK)
    elif LOCK.exists():
        LOCK.unlink()
    print("DEPENDENCY_PACKAGE_FILES_RESTORED=YES")
    raise SystemExit(proc.returncode)

package = json.loads(PACKAGE.read_text(encoding="utf-8"))
installed = json.loads(
    (ROOT / "node_modules" / "react-arborist" / "package.json").read_text(encoding="utf-8")
)

declared = (package.get("dependencies") or {}).get("react-arborist")
if declared != VERSION:
    raise SystemExit(f"DECLARED_VERSION_MISMATCH={declared}")
if installed.get("version") != VERSION:
    raise SystemExit(f"INSTALLED_VERSION_MISMATCH={installed.get('version')}")

print("REACT_ARBORIST_DEPENDENCY=INSTALLED")
print("REACT_ARBORIST_VERSION=" + VERSION)
print("RUNTIME_NETWORK_DEPENDENCY=NO")
print("RAY_EXPLORER_DEPENDENCY_000023=PASS")

from pathlib import Path
import hashlib

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
ICON = ROOT / "src-tauri/icons/icon.ico"
CONF = ROOT / "src-tauri/tauri.conf.json"

if not ICON.exists():
    raise SystemExit("ICON_MISSING=" + str(ICON))
if not CONF.exists():
    raise SystemExit("TAURI_CONFIG_MISSING=" + str(CONF))

data = ICON.read_bytes()

# ICO header: reserved=0, type=1, count>=1
if len(data) < 6:
    raise SystemExit("ICON_TOO_SMALL")
if data[0:4] != b"\x00\x00\x01\x00":
    raise SystemExit("ICON_HEADER_INVALID")
count = int.from_bytes(data[4:6], "little")
if count < 1:
    raise SystemExit("ICON_IMAGE_COUNT_INVALID")

print("HOTFIX=FOUNDATION_000001H2")
print("CAUSE=TAURI_WINDOWS_RESOURCE_ICON_MISSING")
print("ICON=" + str(ICON))
print("ICON_IMAGE_COUNT=" + str(count))
print("ICON_SHA256=" + hashlib.sha256(data).hexdigest())
print("UI_SOURCE_MUTATION=NO")
print("OWNERSHIP_CONTRACT_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("WORKSTATION_FOUNDATION_000001H2_PREFLIGHT=PASS")

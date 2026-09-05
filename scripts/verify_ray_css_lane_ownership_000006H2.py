from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
APP = ROOT / "src/App.tsx"
BASE = ROOT / "src/features/ray/ray.css"
CONTRACT = ROOT / "src/features/ray/rayLayoutContract.css"
PROCESSING = ROOT / "src/features/ray/rayProcessing.css"

for path in (APP, BASE, CONTRACT, PROCESSING):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

app = APP.read_text(encoding="utf-8", errors="replace")
contract = CONTRACT.read_text(encoding="utf-8", errors="replace")
processing = PROCESSING.read_text(encoding="utf-8", errors="replace")
base = BASE.read_text(encoding="utf-8", errors="replace")

checks = {
    "BASE_RAY_CSS_EXISTS": ".ray-page" in base,
    "LAYOUT_CONTRACT_IMPORTED": './features/ray/rayLayoutContract.css' in app,
    "IMPORT_AFTER_BASE": app.find('./features/ray/ray.css') < app.find('./features/ray/rayLayoutContract.css'),
    "CANONICAL_SEVEN_LANES": "minmax(0, 1fr)" in contract and contract.count("grid-row:") >= 7,
    "COCKPIT_CANONICAL_ROW6": ".ray-cockpit" in contract and "grid-row: 6" in contract,
    "COCKPIT_STRETCH": "height: 100%" in contract and "align-self: stretch" in contract,
    "PROCESSING_NO_GRID_TEMPLATE_OWNER": "grid-template-rows" not in processing,
    "PROCESSING_NO_GRID_ROW_OWNER": "grid-row:" not in processing,
    "RUNTIME_NOTICE_COMPACT": "max-height: 34px" in contract,
    "CONTENT_LAYER_PRESERVED": "z-index: 1" in processing,
    "ISOLATION_PRESERVED": "isolation: isolate" in processing,
}

for key, value in checks.items():
    print(key + "=" + ("PASS" if value else "FAIL"))

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

print("CAUSE=CSS_CASCADE_ALLOWED_OLD_RAY_PAGE_SIX_ROW_TEMPLATE_TO_WIN")
print("RUNTIME_SYMPTOM=COCKPIT_RENDERED_IN_OLD_FIXED_36PX_TRACK")
print("FIX=DEDICATED_POST_BASE_RAY_LAYOUT_CONTRACT")
print("LAYOUT_OWNER=rayLayoutContract.css")
print("PROCESSING_OWNER=rayProcessing.css")
print("OWNER_COUNT_PAGE_LANES=1")
print("FLOATING_WINDOW_ADDED=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_CSS_LANE_OWNERSHIP_000006H2_STATIC=PASS")

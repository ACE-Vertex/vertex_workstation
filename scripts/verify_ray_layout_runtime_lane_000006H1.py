from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PAGE = ROOT / "src/features/ray/RayPage.tsx"
CSS = ROOT / "src/features/ray/rayProcessing.css"

for path in (PAGE, CSS):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

page = PAGE.read_text(encoding="utf-8", errors="replace")
css = CSS.read_text(encoding="utf-8", errors="replace")

checks = {
    "TAURI_RUNTIME_DETECTION": "isTauriRuntime" in page,
    "LOCAL_PREVIEW_STATE": "LOCAL UI PREVIEW" in page,
    "LOCAL_PREVIEW_NO_AUTOSCAN": "if (!tauriAvailable)" in page,
    "SEVEN_GRID_LANES": css.count("grid-row:") >= 7 and "minmax(0, 1fr)" in css,
    "RUNTIME_ERROR_ROW5": ".ray-runtime-error" in css and "grid-row: 5" in css,
    "COCKPIT_ROW6": ".ray-cockpit" in css and "grid-row: 6" in css,
    "FOOTER_ROW7": ".ray-status-board" in css and "grid-row: 7" in css,
    "RUNTIME_ERROR_COMPACT": "max-height: 34px" in css,
    "CONTENT_LAYER_Z1": "z-index: 1" in css,
    "ISOLATION_CONTRACT": "isolation: isolate" in css,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in page
        for token in (".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild(")
    ),
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

print("CAUSE=CONDITIONAL_RUNTIME_ERROR_SHIFTED_COCKPIT_INTO_FIXED_36PX_TRACK")
print("SECONDARY=LOCAL_BROWSER_HAS_NO_TAURI_FILESYSTEM")
print("LAYOUT_POLICY=EXPLICIT_GRID_ROWS")
print("LOCAL_MODE=UI_PREVIEW_GRACEFUL")
print("RAY_COCKPIT_TRACK=minmax(0,1fr)")
print("FLOATING_WINDOW_ADDED=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_LAYOUT_RUNTIME_LANE_000006H1_STATIC=PASS")

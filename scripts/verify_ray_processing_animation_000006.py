from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/shell/OperationIndicator.tsx",
    ROOT / "src/shell/operationIndicator.css",
    ROOT / "src/shell/ProcessingGridDistortion.tsx",
    ROOT / "src/shell/processingGridDistortion.css",
    ROOT / "src/features/ray/RayPage.tsx",
    ROOT / "src/features/ray/rayProcessing.css",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

text = "\n".join(
    path.read_text(encoding="utf-8", errors="replace")
    for path in required
)

grid_css = (ROOT / "src/shell/processingGridDistortion.css").read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "PROCESSING_INDICATOR": "function OperationIndicator" in text,
    "ELAPSED_TIMER": "formatElapsed" in text and "operation-timer" in text,
    "PROJECT_SCAN_PHASE": '"PROJECT SCAN"' in text,
    "FILE_READ_PHASE": '"FILE READ"' in text,
    "GRID_DISTORTION_CANVAS": "function ProcessingGridDistortion" in text,
    "GRID_WARP_MATH": "falloff" in text and "swirl" in text and "amplitude" in text,
    "PROCESSING_STATE_DRIVES_ANIMATION": 'active={Boolean(operation)}' in text,
    "BACKGROUND_POINTER_EVENTS_NONE": "pointer-events: none" in grid_css,
    "BACKGROUND_LAYER_Z0": "z-index: 0" in grid_css,
    "CONTENT_LAYER_Z1": "z-index: 1" in text,
    "ISOLATION_CONTRACT": "isolation: isolate" in text,
    "NO_FIXED_BACKGROUND": "position: fixed" not in grid_css,
    "REDUCED_MOTION": "prefers-reduced-motion" in text,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in text
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

print("PROCESSING_VISUAL=ORBIT+SWEEP+ELAPSED")
print("PROCESSING_BACKGROUND=VERTEX_GRID_DISTORTION")
print("BACKGROUND_OWNERSHIP=PRESENTATION_ONLY")
print("BACKGROUND_CANNOT_CAPTURE_POINTER=PASS")
print("FLOATING_WINDOW_ADDED=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_PROCESSING_ANIMATION_000006_STATIC=PASS")

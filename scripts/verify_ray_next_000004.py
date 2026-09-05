from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/App.tsx",
    ROOT / "src/shell/workstationShell.css",
    ROOT / "src/features/ray/RayPage.tsx",
    ROOT / "src/features/ray/RayProjectTree.tsx",
    ROOT / "src/features/ray/RayTargetSet.tsx",
    ROOT / "src/features/ray/RayInspector.tsx",
    ROOT / "src/features/ray/RayEvidence.tsx",
    ROOT / "src/features/ray/models.ts",
    ROOT / "src/features/ray/seedData.ts",
    ROOT / "src/features/ray/ray.css",
]

for p in required:
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in required)

checks = {
    "RAY_PAGE": "function RayPage" in text,
    "PROJECT_TREE": "Project Tree" in text,
    "TARGET_SET": "Target Set" in text,
    "TARGET_LOCK": "TARGET LOCK" in text,
    "QUICK_RAY": "QUICK RAY" in text,
    "DEEP_RAY": "DEEP RAY" in text,
    "RAY_INSPECTOR": "RAY INSPECTOR" in text,
    "EVIDENCE_FINDINGS": "Evidence / Findings" in text,
    "PROVENANCE": "Provenance" in text or "PROVENANCE" in text,
    "HUMAN_PRIORITY": "HUMAN PRIORITY" in text,
    "RAY_RELEVANCE": "RAY RELEVANCE" in text,
    "OWNERSHIP_LENSES": "OWNERSHIP LENSES" in text,
    "FORGE_RAY_SWITCHER": 'setWorkspace("forge")' in text and 'setWorkspace("ray")' in text,
    "PERSISTENT_FLOAT_PROHIBITED": "FLOATING_WINDOW_POLICY=PROHIBITED_FOR_PERSISTENT_TOOLS" in text,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in text
        for token in (".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild(")
    ),
    "NO_RAY_FIXED_POSITION": "position: fixed" not in (ROOT / "src/features/ray/ray.css").read_text(encoding="utf-8"),
    "GRID_COCKPIT": "ray-cockpit" in text and "grid-template-columns" in text,
}

for key, value in checks.items():
    print(key + "=" + ("PASS" if value else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
p = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if p.stdout:
    print(p.stdout.encode("ascii","backslashreplace").decode("ascii"))
if p.stderr:
    print(p.stderr.encode("ascii","backslashreplace").decode("ascii"))
if p.returncode:
    raise SystemExit(p.returncode)

print("RAY_NEXT_STAGE=FOUNDATION_COCKPIT")
print("ANALYSIS_CORE=STUB")
print("FILESYSTEM_SERVICE=NOT_WIRED")
print("FLOAT_POLICY=NO_PERSISTENT_FLOAT_WINDOWS")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_NEXT_000004_STATIC=PASS")

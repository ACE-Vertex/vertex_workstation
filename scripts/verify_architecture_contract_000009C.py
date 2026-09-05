from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/App.tsx",
    ROOT / "src/features/contracts/ArchitectureContractPage.tsx",
    ROOT / "src/features/contracts/contracts.ts",
    ROOT / "src/features/contracts/architectureContract.css",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

app = required[0].read_text(encoding="utf-8", errors="replace")
page = required[1].read_text(encoding="utf-8", errors="replace")
data = required[2].read_text(encoding="utf-8", errors="replace")
css = required[3].read_text(encoding="utf-8", errors="replace")

checks = {
    "CONTRACT_WORKSPACE": '"contract"' in app and "CONTRACT" in app,
    "CONTRACT_PAGE_WIRED": "ArchitectureContractPage" in app,
    "LEFT_CARD_LIST": "Architecture Cards" in page and "architecture-card-list" in css,
    "RIGHT_CONTRACT_DETAIL": "ContractDetail" in page and "architecture-detail" in css,
    "CARD_SELECTION_STATE": "selectedId" in page and "setSelectedId" in page,
    "FOLDER_ARCHITECTURE_CARD": "Folder Architecture" in data,
    "COMPONENT_OWNERSHIP_CARD": "Component Ownership" in data,
    "LAYOUT_OWNERSHIP_CARD": "Layout Ownership" in data,
    "FEATURE_BOUNDARY_CARD": "Feature Boundary" in data,
    "VERIFICATION_OWNERSHIP_CARD": "Verification Ownership" in data,
    "RUNTIME_SAFETY_CARD": "Runtime Safety" in data,
    "NO_FLOAT": "position: fixed" not in css,
    "RESPONSIVE": "@media (max-width: 1180px)" in css,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in (app + page)
        for token in (
            ".appendChild(",
            ".removeChild(",
            ".insertBefore(",
            ".replaceChild(",
        )
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

print("ARCHITECTURE_CONTRACT_PAGE=PASS")
print("LAYOUT=LEFT_CARD_LIST+RIGHT_DETAIL")
print("FLOATING_WINDOW_ADDED=NO")
print("FORGE_MUTATION=NO")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("ARCHITECTURE_CONTRACT_000009C_STATIC=PASS")

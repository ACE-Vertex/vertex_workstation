from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
SRC = ROOT/"src"

required = [
    SRC/"App.tsx",
    SRC/"features/forge/ForgePage.tsx",
    SRC/"features/forge/IncomingCargo.tsx",
    SRC/"features/forge/ArtifactInspector.tsx",
    SRC/"features/forge/ConsolePanel.tsx",
    SRC/"features/forge/PathSwitcher.tsx",
    SRC/"features/forge/ForgeStatusCards.tsx",
    SRC/"features/forge/models.ts",
    SRC/"features/forge/seedData.ts",
    SRC/"styles.css",
]
for p in required:
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in required)

checks = {
    "FORGE_PAGE": "function ForgePage" in text,
    "INCOMING_CARGO": "Incoming Cargo" in text,
    "ARTIFACT_INSPECTOR": "Artifact Inspector" in text,
    "VERTEX_SHELL": "Vertex Shell" in text,
    "WORKS_LEDGER": "Works Ledger" in text,
    "RECEIVING_BAY_SWITCHABLE": 'label="RECEIVING BAY"' in text and "PathSwitcher" in text,
    "PRODUCTION_ROOT_SWITCHABLE": 'label="AUTHORIZED PRODUCTION ROOT"' in text and "PathSwitcher" in text,
    "SELECTED_CARGO_DRIVES_INSPECTOR": "setSelectedId" in text and "ArtifactInspector artifact={selected}" in text,
    "NO_DIRECT_DOM_REPARENT": all(
        token not in text
        for token in (".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild(")
    ),
    "LEGACY_LAYOUT_GRID": "forge-grid" in text and "status-cards" in text,
}
for k,v in checks.items():
    print(k + "=" + ("PASS" if v else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
p = subprocess.run([npm, "run", "build"], cwd=ROOT, capture_output=True, text=True, errors="replace")
print("RUN=" + npm + " run build")
if p.stdout:
    print(p.stdout.encode("ascii","backslashreplace").decode("ascii"))
if p.stderr:
    print(p.stderr.encode("ascii","backslashreplace").decode("ascii"))
if p.returncode:
    raise SystemExit(p.returncode)

print("FORGE_LEGACY_FIDELITY_000002_STATIC=PASS")

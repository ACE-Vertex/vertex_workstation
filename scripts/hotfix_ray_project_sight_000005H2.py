from pathlib import Path

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
RAY_DIR = ROOT / "src/features/ray"
STALE = RAY_DIR / "seedData.ts"

# RAY 000005 replaced demo/static RayFile data with real filesystem scanning.
# The old 000004 seedData.ts is no longer part of the runtime architecture,
# but TypeScript still compiles every source file under src/.
#
# Delete only after proving no current source imports it.
references = []
for path in ROOT.joinpath("src").rglob("*"):
    if not path.is_file():
        continue
    if path == STALE:
        continue
    if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx"}:
        continue

    text = path.read_text(encoding="utf-8", errors="replace")
    if (
        "./seedData" in text
        or "../ray/seedData" in text
        or "features/ray/seedData" in text
        or 'from "./seedData"' in text
        or "from './seedData'" in text
    ):
        references.append(str(path))

if references:
    print("STALE_SEEDDATA_REFERENCED=FAIL")
    for ref in references:
        print("REFERENCE=" + ref)
    raise SystemExit(1)

print("STALE_SEEDDATA_REFERENCED=NO")

if STALE.exists():
    STALE.unlink()
    print("RETIRED=" + str(STALE))
else:
    print("ALREADY_RETIRED=" + str(STALE))

if STALE.exists():
    raise SystemExit("STALE_SEEDDATA_SURVIVED")

print("CAUSE=000004_DEMO_SEEDDATA_TYPE_DRIFT_AFTER_000005_REAL_FILESYSTEM_MODEL")
print("RETIREMENT_POLICY=DELETE_UNUSED_DEMO_SOURCE")
print("RAY_LAYOUT_MUTATION=NO")
print("RAY_FILESYSTEM_LOGIC_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_PROJECT_SIGHT_000005H2_PATCH=PASS")

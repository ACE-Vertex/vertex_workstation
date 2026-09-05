from pathlib import Path
import re

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
RAY_DIR = ROOT / "src/features/ray"
STALE = RAY_DIR / "seedData.ts"

if not RAY_DIR.exists():
    raise SystemExit("RAY_DIR_MISSING=" + str(RAY_DIR))

# H2 false-positive explanation:
# ForgePage.tsx imports its own sibling ./seedData under src/features/forge.
# That must NOT be treated as a reference to src/features/ray/seedData.ts.
#
# Only references that resolve from files inside the RAY feature directory
# can own ./seedData. We therefore scope the retirement guard to RAY source.
patterns = [
    re.compile(r'from\s+["\']\./seedData["\']'),
    re.compile(r'import\s*\(\s*["\']\./seedData["\']\s*\)'),
    re.compile(r'require\s*\(\s*["\']\./seedData["\']\s*\)'),
]

ray_references = []
for path in RAY_DIR.rglob("*"):
    if not path.is_file() or path == STALE:
        continue
    if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx"}:
        continue

    text = path.read_text(encoding="utf-8", errors="replace")
    if any(pattern.search(text) for pattern in patterns):
        ray_references.append(str(path))

if ray_references:
    print("RAY_SEEDDATA_REFERENCED=FAIL")
    for ref in ray_references:
        print("RAY_REFERENCE=" + ref)
    raise SystemExit(1)

print("RAY_SEEDDATA_REFERENCED=NO")

if STALE.exists():
    STALE.unlink()
    print("RETIRED=" + str(STALE))
else:
    print("ALREADY_RETIRED=" + str(STALE))

if STALE.exists():
    raise SystemExit("STALE_RAY_SEEDDATA_SURVIVED")

print("CAUSE_H2=GUARD_MATCHED_FORGE_SIBLING_IMPORT_WITH_SAME_BASENAME")
print("REFERENCE_RESOLUTION=FEATURE_SCOPED")
print("RETIREMENT_POLICY=DELETE_UNUSED_RAY_DEMO_SOURCE")
print("RAY_LAYOUT_MUTATION=NO")
print("RAY_FILESYSTEM_LOGIC_MUTATION=NO")
print("FORGE_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_PROJECT_SIGHT_000005H3_PATCH=PASS")

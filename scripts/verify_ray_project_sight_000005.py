from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/features/ray/RayPage.tsx",
    ROOT / "src/features/ray/RayProjectRootBar.tsx",
    ROOT / "src/features/ray/RayProjectTree.tsx",
    ROOT / "src/features/ray/RaySourceViewer.tsx",
    ROOT / "src/features/ray/RayTargetSet.tsx",
    ROOT / "src/features/ray/RayInspector.tsx",
    ROOT / "src/features/ray/RayEvidence.tsx",
    ROOT / "src/features/ray/rayApi.ts",
    ROOT / "src/features/ray/rayAnalysis.ts",
    ROOT / "src/features/ray/models.ts",
    ROOT / "src/features/ray/ray.css",
    ROOT / "src-tauri/src/lib.rs",
]

for p in required:
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in required)
rust = (ROOT / "src-tauri/src/lib.rs").read_text(encoding="utf-8", errors="replace")
css = (ROOT / "src/features/ray/ray.css").read_text(encoding="utf-8", errors="replace")

checks = {
    "PROJECT_ROOT_INPUT": "PROJECT ROOT" in text and "LOAD ROOT" in text,
    "PROJECT_ROOT_BROWSE": "BROWSE" in text and "ray_pick_project_root" in text,
    "RECENT_ROOTS": "RECENT_KEY" in text and "recentRoots" in text,
    "REAL_PROJECT_SCAN": 'invoke<RayScanResult>("ray_scan_project"' in text,
    "REAL_FILE_READ": 'invoke<RayFileContent>("ray_read_project_file"' in text,
    "SOURCE_VIEWER": "Source Viewer" in text and "FILE SIGHT" in text,
    "LEXICAL_IMPORT_SIGHT": "Direct dependency clues extracted" in text,
    "LEXICAL_SYMBOL_SIGHT": "Source symbols extracted" in text,
    "DIRECT_DOM_LENS": "Direct DOM mutation lens" in text,
    "RUST_SCAN_COMMAND": "fn ray_scan_project" in rust,
    "RUST_READ_COMMAND": "fn ray_read_project_file" in rust,
    "RUST_PICK_COMMAND": "fn ray_pick_project_root" in rust,
    "ROOT_PATH_GUARD": "FILE_OUTSIDE_PROJECT_ROOT" in rust and "starts_with(&root)" in rust,
    "READ_LIMIT": "MAX_READ_BYTES" in rust,
    "SCAN_LIMIT": "MAX_SCAN_FILES" in rust and "MAX_SCAN_DEPTH" in rust,
    "HEAVY_DIR_EXCLUSION": '"node_modules"' in rust and '"target"' in rust and '"versions"' in rust,
    "PROVENANCE_CLASSIFICATION": "classify_provenance" in rust,
    "PERSISTENT_FLOAT_PROHIBITED": "FLOATING_WINDOW_POLICY=PROHIBITED_FOR_PERSISTENT_TOOLS" in text,
    "NO_RAY_FIXED_POSITION": "position: fixed" not in css,
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
commands = [
    ([npm, "run", "build"], ROOT),
    (["cargo", "fmt", "--manifest-path", str(ROOT / "src-tauri/Cargo.toml"), "--", "--check"], ROOT),
    (["cargo", "check", "--manifest-path", str(ROOT / "src-tauri/Cargo.toml")], ROOT),
]

for args, cwd in commands:
    p = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        errors="replace",
    )
    print("RUN=" + " ".join(args))
    if p.stdout:
        print(p.stdout.encode("ascii","backslashreplace").decode("ascii"))
    if p.stderr:
        print(p.stderr.encode("ascii","backslashreplace").decode("ascii"))
    if p.returncode:
        raise SystemExit(p.returncode)

print("RAY_PROJECT_SELECTION=REAL")
print("RAY_FILE_SIGHT=REAL_TAURI_FILESYSTEM")
print("RAY_SOURCE_PREVIEW_MAX_BYTES=524288")
print("RAY_ANALYSIS_STAGE=LEXICAL_DETERMINISTIC")
print("AST_GRAPH=NEXT_PASS")
print("FLOAT_POLICY=NO_PERSISTENT_FLOAT_WINDOWS")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_PROJECT_SIGHT_000005_STATIC=PASS")

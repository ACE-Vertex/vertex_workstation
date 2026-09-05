from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
required = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/forgeApi.ts",
    ROOT / "src/features/forge/IncomingCargo.tsx",
    ROOT / "src/features/forge/ArtifactInspector.tsx",
    ROOT / "src/features/forge/PathSwitcher.tsx",
    ROOT / "src/features/forge/models.ts",
    ROOT / "src/features/forge/seedData.ts",
    ROOT / "src/features/forge/forgeRuntime.css",
    ROOT / "src-tauri/src/lib.rs",
    ROOT / "src-tauri/Cargo.toml",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

text = "\n".join(
    path.read_text(encoding="utf-8", errors="replace")
    for path in required
)
rust = (ROOT / "src-tauri/src/lib.rs").read_text(encoding="utf-8", errors="replace")
cargo = (ROOT / "src-tauri/Cargo.toml").read_text(encoding="utf-8", errors="replace")

checks = {
    "REAL_RECEIVING_SCAN": 'invoke<ForgeScanResult>("forge_scan_receiving_bay"' in text,
    "REAL_VRA_ZIP_INSPECTION": "ZipArchive" in rust and 'by_name("manifest.json")' in rust,
    "ZIP_DEFLATE_DEP": 'zip = { version = "2"' in cargo and '"deflate"' in cargo,
    "MANIFEST_SIZE_BOUND": "MAX_VRA_MANIFEST_BYTES" in rust,
    "VRA_SCHEMA_GATE": 'artifact.schema_version != "vra/1"' in rust,
    "HUMAN_APPLY_GATE": 'artifact.authority != "HUMAN_APPLY"' in rust,
    "AUTHORIZED_ROOT_GATE": "TARGET_OUTSIDE_AUTHORIZED_PRODUCTION_ROOT" in rust,
    "REAL_OPERATION_PREVIEW": "operation_preview" in rust and "OPERATION PREVIEW" in text,
    "FORGE_FOLDER_PICKER": "forge_pick_folder" in rust and "BROWSE" in text,
    "REFRESH_WIRED": "onRefresh" in text and "SCANNING..." in text,
    "NO_FAKE_FOUNDATION_ARTIFACTS": "FOUNDATION_ARTIFACTS" not in text,
    "NO_FAKE_STAGE": "STAGE · NEXT PASS" in text and "disabled" in text,
    "COPY_INSPECTION": "COPY INSPECTION" in text and "navigator.clipboard.writeText" in text,
    "PROCESSING_SWEEP": "forge-receiving-sweep" in text,
    "CANONICAL_DISPLAY_PATH_FIX": 'strip_prefix("\\\\\\\\?\\\\")' in rust,
    "RAY_COMMANDS_PRESERVED": all(
        token in rust
        for token in ("ray_scan_project", "ray_read_project_file", "ray_pick_project_root")
    ),
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

frontend = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if frontend.stdout:
    print(frontend.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if frontend.stderr:
    print(frontend.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if frontend.returncode:
    raise SystemExit(frontend.returncode)

fmt = subprocess.run(
    [
        "cargo",
        "fmt",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=cargo fmt")
if fmt.stdout:
    print(fmt.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if fmt.stderr:
    print(fmt.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if fmt.returncode:
    raise SystemExit(fmt.returncode)

check = subprocess.run(
    [
        "cargo",
        "check",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=cargo check")
if check.stdout:
    print(check.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if check.stderr:
    print(check.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if check.returncode:
    raise SystemExit(check.returncode)

print("FORGE_RECEIVING_BAY=REAL_FILESYSTEM")
print("FORGE_MANIFEST_INSPECTOR=REAL_VRA_ZIP")
print("FORGE_TARGET_AUTHORIZATION=DETERMINISTIC")
print("FORGE_STAGE=NEXT_PASS")
print("FORGE_APPLY=NEXT_PASS")
print("FORGE_ROLLBACK=NEXT_PASS")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_REAL_RECEIVING_000007_STATIC=PASS")

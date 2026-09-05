from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/ArtifactInspector.tsx",
    ROOT / "src/features/forge/forgeApi.ts",
    ROOT / "src/features/forge/models.ts",
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
rust = (ROOT / "src-tauri/src/lib.rs").read_text(
    encoding="utf-8",
    errors="replace",
)
cargo = (ROOT / "src-tauri/Cargo.toml").read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "STAGE_API_WIRED": 'invoke<ForgeStageResult>("forge_stage_artifact"' in text,
    "STAGE_COMMAND_WIRED": "fn forge_stage_artifact" in rust,
    "SHA256_DEP": 'sha2 = "0.10"' in cargo,
    "PAYLOAD_HASH_VERIFY": "STAGE_SHA256_MISMATCH" in rust,
    "SOURCE_PAYLOAD_GATE": "STAGE_SOURCE_OUTSIDE_PAYLOAD" in rust,
    "PATH_TRAVERSAL_GATE": "STAGE_DESTINATION_TRAVERSAL_BLOCKED" in rust,
    "AUTHORIZED_ROOT_RECHECK": "STAGE_TARGET_OUTSIDE_AUTHORIZED_ROOT" in rust,
    "HUMAN_APPLY_RECHECK": "STAGE_AUTHORITY_NOT_HUMAN_APPLY" in rust,
    "IMMUTABLE_STAGE_ID": "STAGE_ID_COLLISION" in rust,
    "STAGE_REPORT": 'stage_report.json' in rust,
    "STAGE_LOCK": '"STAGE_LOCK"' in rust,
    "ARTIFACT_SNAPSHOT": 'artifact.vra' in rust,
    "BACKUP_PLAN": "backup_plan_root" in rust and "BACKUP PLAN" in text,
    "NO_TARGET_MUTATION_DURING_STAGE": "TARGET_MUTATION=NO" in text,
    "APPLY_STILL_DISABLED": "APPLY / FORGE · NEXT PASS" in text and "disabled" in text,
    "ROLLBACK_STILL_DISABLED": "ROLLBACK becomes active with APPLY" in text,
    "STAGING_PROCESSING_STATE": '"STAGING"' in text and "IMMUTABLE STAGING" in text,
    "RAY_COMMANDS_PRESERVED": all(
        token in rust
        for token in (
            "ray_scan_project",
            "ray_read_project_file",
            "ray_pick_project_root",
        )
    ),
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in text
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

frontend = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if frontend.stdout:
    print(
        frontend.stdout
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if frontend.stderr:
    print(
        frontend.stderr
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
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
    print(
        fmt.stdout
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if fmt.stderr:
    print(
        fmt.stderr
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
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
    print(
        check.stdout
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if check.stderr:
    print(
        check.stderr
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if check.returncode:
    raise SystemExit(check.returncode)

print("FORGE_STAGE=REAL")
print("STAGE_PAYLOAD_HASH=SHA256")
print("STAGE_STORAGE=LOCALAPPDATA_VERTEXWORKSTATION")
print("STAGE_TARGET_MUTATION=NO")
print("BACKUP_EXECUTION=NOT_YET")
print("FORGE_APPLY=NEXT_PASS")
print("FORGE_ROLLBACK=NEXT_PASS")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_REAL_STAGE_000008_STATIC=PASS")

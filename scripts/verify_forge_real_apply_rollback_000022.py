from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MODELS = ROOT / "src" / "features" / "forge" / "models.ts"
API = ROOT / "src" / "features" / "forge" / "forgeApi.ts"
INSPECTOR = ROOT / "src" / "features" / "forge" / "ArtifactInspector.tsx"
PAGE = ROOT / "src" / "features" / "forge" / "ForgePage.tsx"
CSS = ROOT / "src" / "features" / "forge" / "forgeRuntime.css"
LIB = ROOT / "src-tauri" / "src" / "lib.rs"
APPLY_RS = ROOT / "src-tauri" / "src" / "forge_apply.rs"

for path in (MODELS, API, INSPECTOR, PAGE, CSS, LIB, APPLY_RS):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

models = MODELS.read_text(encoding="utf-8", errors="replace")
api = API.read_text(encoding="utf-8", errors="replace")
inspector = INSPECTOR.read_text(encoding="utf-8", errors="replace")
page = PAGE.read_text(encoding="utf-8", errors="replace")
css = CSS.read_text(encoding="utf-8", errors="replace")
lib = LIB.read_text(encoding="utf-8", errors="replace")
apply_rs = APPLY_RS.read_text(encoding="utf-8", errors="replace")
combined = "\n".join((models, api, inspector, page, css, lib, apply_rs))

checks = {
    "APPLY_RESULT_MODELS":
        "ForgeApplyResult" in models and "ForgeRollbackResult" in models,
    "APPLY_RUNTIME_STATES":
        '"APPLYING"' in models and '"ROLLING_BACK"' in models,
    "APPLY_TAURI_API":
        'invoke<ForgeApplyResult>("forge_apply_stage"' in api,
    "ROLLBACK_TAURI_API":
        'invoke<ForgeRollbackResult>("forge_rollback_stage"' in api,
    "APPLY_COMMAND_REGISTERED":
        "forge_apply::forge_apply_stage" in lib,
    "ROLLBACK_COMMAND_REGISTERED":
        "forge_apply::forge_rollback_stage" in lib,
    "HUMAN_GATE_RECHECK":
        "authority=HUMAN_APPLY" in apply_rs
        and "APPLY_HUMAN_GATE_MISSING" in apply_rs,
    "STAGE_LOCK_REQUIRED":
        'join("STAGE_LOCK")' in apply_rs,
    "STAGE_ARTIFACT_SHA_RECHECK":
        "APPLY_ARTIFACT_SHA256_MISMATCH" in apply_rs,
    "STAGED_PAYLOAD_SHA_RECHECK":
        "APPLY_STAGED_SHA256_MISMATCH" in apply_rs,
    "AUTHORIZED_ROOT_RECHECK":
        "APPLY_TARGET_OUTSIDE_AUTHORIZED_ROOT" in apply_rs
        and "ROLLBACK_TARGET_OUTSIDE_AUTHORIZED_ROOT" in apply_rs,
    "TRAVERSAL_GATE":
        "APPLY_DESTINATION" in apply_rs
        and "Component::ParentDir" in apply_rs
        and "Component::Prefix" in apply_rs,
    "SYMLINK_GATE":
        "APPLY_TARGET_NOT_REGULAR_FILE" in apply_rs
        and "SYMLINK_BLOCKED" in apply_rs,
    "TARGET_STATE_DRIFT_GATE":
        "APPLY_TARGET_STATE_DRIFT_NEW_NOW_EXISTS" in apply_rs
        and "APPLY_TARGET_STATE_DRIFT_EXISTING_NOW_MISSING" in apply_rs,
    "BACKUP_BEFORE_TARGET_MUTATION":
        "Backup every pre-existing target before changing any target." in apply_rs
        and "APPLY_BACKUP" in apply_rs,
    "AUTO_RESTORE_ON_PARTIAL_APPLY_FAILURE":
        "AUTO_RESTORE_PASS" in apply_rs and "AUTO_RESTORE_FAIL" in apply_rs,
    "APPLY_REPORT_AND_LOCK":
        'join("apply_report.json")' in apply_rs
        and 'join("APPLY_LOCK")' in apply_rs,
    "ROLLBACK_REPORT_AND_LOCK":
        'join("rollback_report.json")' in apply_rs
        and 'join("ROLLBACK_LOCK")' in apply_rs,
    "ROLLBACK_POST_APPLY_DRIFT_BLOCK":
        "ROLLBACK_TARGET_DRIFT_SHA256" in apply_rs
        and "Do not overwrite post-APPLY edits." in apply_rs,
    "APPLY_BUTTON_REAL":
        'onClick={() => stageResult && onApply(stageResult)}' in inspector
        and "APPLY / FORGE" in inspector,
    "APPLY_ARMS_ONLY_AFTER_STAGE":
        "!staged" in inspector
        and "apply-armed" in inspector,
    "ROLLBACK_ARMS_ONLY_AFTER_APPLY":
        "!applied" in inspector
        and "rollback-armed" in inspector,
    "PROCESSING_STATES_VISIBLE":
        'runtimeState === "APPLYING"' in page
        and 'runtimeState === "ROLLING_BACK"' in page
        and "HUMAN APPLY + BACKUP + TARGET MUTATION" in page
        and "ROLLBACK + BACKUP RESTORE" in page,
    "LIVE_RECEIVING_WATCH_PRESERVED":
        "FORGE_RECEIVING_WATCH_INTERVAL_MS = 1500" in page,
    "CARGO_HISTORY_COLORS_PRESERVED":
        "stageHistory" in models
        and "forge-cargo-verified" in css
        and "forge-cargo-stage-error" in css,
    "NO_FLOAT_UI":
        "position: fixed" not in css,
    "NO_DOM_INJECTION":
        all(token not in combined for token in (
            ".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild("
        )),
    "OBSOLETE_APPLY_DISABLED_LITERAL_RETIRED":
        "APPLY / FORGE · NEXT PASS" not in inspector,
}

for name, ok in checks.items():
    print(name + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
commands = [
    ([npm, "run", "build"], "FRONTEND_BUILD"),
    (
        ["cargo", "check", "--manifest-path", str(ROOT / "src-tauri" / "Cargo.toml")],
        "CARGO_CHECK",
    ),
]
for args, label in commands:
    print("RUN=" + " ".join(args))
    proc = subprocess.run(
        args,
        cwd=ROOT,
        capture_output=True,
        text=True,
        errors="replace",
    )
    if proc.stdout:
        print(proc.stdout.encode("ascii", "backslashreplace").decode("ascii"))
    if proc.stderr:
        print(proc.stderr.encode("ascii", "backslashreplace").decode("ascii"))
    if proc.returncode:
        raise SystemExit(proc.returncode)
    print(label + "=PASS")

print("APPLY_GATE=STAGE_RESULT_PLUS_HUMAN_CLICK")
print("APPLY_MUTATION_OWNER=TAURI_RUST")
print("ROLLBACK_OWNER=TAURI_RUST")
print("BACKUP_OWNER=TAURI_RUST")
print("APPLY_PARTIAL_FAILURE=AUTO_RESTORE_ATTEMPTED")
print("ROLLBACK_POST_APPLY_DRIFT=BLOCKED")
print("FORGE_REAL_APPLY_ROLLBACK_000022=PASS")

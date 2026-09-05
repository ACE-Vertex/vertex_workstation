from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PAGE = ROOT / "src" / "features" / "forge" / "ForgePage.tsx"
APPLY_RS = ROOT / "src-tauri" / "src" / "forge_apply.rs"

page = PAGE.read_text(encoding="utf-8", errors="replace")
apply_rs = APPLY_RS.read_text(encoding="utf-8", errors="replace")

browse_start = page.index("async function browsePath(")
stage_start = page.index("async function stageArtifact(")
apply_start = page.index("async function applyStage(")
rollback_start = page.index("async function rollbackStage(")

browse_block = page[browse_start:stage_start]
stage_block = page[stage_start:apply_start]
apply_block = page[apply_start:rollback_start]

checks = {
    "BROWSE_PATH_HAS_NO_ARTIFACT_REFERENCE":
        "artifact.stageHistory" not in browse_block
        and "artifact.id" not in browse_block,
    "STAGE_CATCH_OWNS_ERROR_HISTORY":
        'artifact.stageHistory !== "VERIFIED"' in stage_block
        and 'stageHistory: "ERROR" as const' in stage_block,
    "STAGE_SUCCESS_OWNS_VERIFIED_HISTORY":
        'stageHistory: "VERIFIED" as const' in stage_block,
    "APPLY_FLOW_PRESENT":
        "applyForgeStage(" in apply_block
        and 'setRuntimeState("APPLYING")' in apply_block,
    "ROLLBACK_FLOW_PRESENT":
        "rollbackForgeStage(" in page
        and 'setRuntimeState("ROLLING_BACK")' in page,
    "UNUSED_WRITE_IMPORT_REMOVED":
        "io::{Read, Write}" not in apply_rs,
}

for name, ok in checks.items():
    print(name + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

commands = [
    ["python", str(ROOT / "scripts" / "verify_forge_real_apply_rollback_000022.py")],
    ["python", str(ROOT / "scripts" / "verify_forge_receiving_live_watch_000020.py")],
    ["python", str(ROOT / "scripts" / "verify_forge_incoming_history_colors_000021.py")],
    ["python", str(ROOT / "scripts" / "verify_openai_api_adapter_000019.py")],
    ["python", str(ROOT / "scripts" / "build_workstation_foundation_000001.py")],
]

for args in commands:
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

print("CAUSE=000022H1_VERIFIER_EXPECTED_NONEXISTENT_CHOOSEFOLDER_FUNCTION")
print("ACTUAL_FUNCTION=browsePath")
print("RUNTIME_SOURCE_MUTATION=NO")
print("FORGE_REAL_APPLY_ROLLBACK_000022H2=PASS")

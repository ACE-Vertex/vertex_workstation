from pathlib import Path
import subprocess
import sys

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MODELS = ROOT / "src" / "features" / "forge" / "models.ts"
CARGO = ROOT / "src" / "features" / "forge" / "IncomingCargo.tsx"
PAGE = ROOT / "src" / "features" / "forge" / "ForgePage.tsx"
CSS = ROOT / "src" / "features" / "forge" / "forgeRuntime.css"
RUST = ROOT / "src-tauri" / "src" / "lib.rs"

for path in (MODELS, CARGO, PAGE, CSS, RUST):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

models = MODELS.read_text(encoding="utf-8", errors="replace")
cargo = CARGO.read_text(encoding="utf-8", errors="replace")
page = PAGE.read_text(encoding="utf-8", errors="replace")
css = CSS.read_text(encoding="utf-8", errors="replace")
rust = RUST.read_text(encoding="utf-8", errors="replace")
combined = "\n".join((models, cargo, page, css, rust))

checks = {
    "HISTORY_TYPE_SEPARATE_FROM_VALIDITY":
        'ArtifactStageHistory = "NONE" | "ERROR" | "VERIFIED"' in models,
    "ARTIFACT_SHA_EXPOSED":
        "artifactSha256: string" in models and "artifact_sha256: String" in rust,
    "HISTORY_LEDGER_LOCALAPPDATA":
        'join("VertexWorkstation")' in rust
        and 'join("forge_history")' in rust
        and 'join("events.jsonl")' in rust,
    "HISTORY_APPEND_ONLY":
        "OpenOptions::new()" in rust
        and ".append(true)" in rust
        and 'schema: "forge-history/1"' in rust,
    "SUCCESS_HISTORY_RECORDED":
        '"STAGE_VERIFIED"' in rust and '"STAGE PASS"' in rust,
    "ERROR_HISTORY_RECORDED":
        '"STAGE_ERROR"' in rust,
    "SUCCESS_BACKFILL_FROM_STAGE_REPORTS":
        'join("stage_report.json")' in rust
        and '.get("artifactSha256")' in rust,
    "HISTORY_KEYED_BY_ARTIFACT_SHA":
        "HashMap<String, String>" in rust
        and "artifact_sha256" in rust,
    "VERIFIED_PRECEDENCE_OVER_ERROR":
        'if outcome == "STAGE_VERIFIED"' in rust
        and 'outcome == "STAGE_ERROR" && current != "VERIFIED"' in rust,
    "RED_UNUSABLE":
        'return "unusable"' in cargo
        and ".forge-cargo-unusable" in css
        and "#e84f4f" in css,
    "NEUTRAL_UNSTAGED":
        'return "unstaged"' in cargo
        and ".forge-cargo-unstaged" in css
        and 'READY · UNSTAGED' in cargo,
    "ORANGE_STAGE_ERROR":
        'return "stage-error"' in cargo
        and ".forge-cargo-stage-error" in css
        and "#ff8e2e" in css,
    "GREEN_VERIFIED":
        'return "verified"' in cargo
        and ".forge-cargo-verified" in css
        and "#55d99f" in css,
    "SELECTION_DOES_NOT_RECOLOR_LIFECYCLE":
        ".forge-cargo-verified.selected" in css
        and ".forge-cargo-stage-error.selected" in css
        and ".forge-cargo-unusable.selected" in css
        and ".forge-cargo-unstaged.selected" in css,
    "TOP_VERIFIED_USES_PERSISTED_ARTIFACT_STATE":
        'artifact.stageHistory === "VERIFIED"' in page
        and "verified={verified}" in page,
    "STAGE_SUCCESS_UPDATES_CARD_IMMEDIATELY":
        'stageHistory: "VERIFIED" as const' in page,
    "STAGE_ERROR_UPDATES_CARD_IMMEDIATELY":
        'stageHistory: "ERROR" as const' in page,
    "COPY_INSPECTION_INCLUDES_HISTORY":
        "stageHistory: artifact.stageHistory" in page
        and "artifactSha256: artifact.artifactSha256" in page,
    "LIVE_RECEIVING_WATCH_PRESERVED":
        "FORGE_RECEIVING_WATCH_INTERVAL_MS = 1500" in page
        and "forge_receiving_bay_fingerprint" in rust,
    "NO_FLOAT_UI":
        "position: fixed" not in css,
    "NO_DOM_INJECTION":
        all(token not in combined for token in (
            ".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild("
        )),
}

for name, ok in checks.items():
    print(name + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
for args, label in (
    ([npm, "run", "build"], "FRONTEND_BUILD"),
    (["cargo", "check", "--manifest-path", str(ROOT / "src-tauri" / "Cargo.toml")], "CARGO_CHECK"),
):
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

print("FORGE_CARGO_RED=UNUSABLE_CURRENT_ARTIFACT")
print("FORGE_CARGO_NEUTRAL=READY_NEVER_STAGED")
print("FORGE_CARGO_ORANGE=STAGE_ERROR_NO_SUCCESS")
print("FORGE_CARGO_GREEN=STAGE_VERIFIED_AT_LEAST_ONCE")
print("FORGE_INCOMING_CARGO_HISTORY_COLORS_000021=PASS")

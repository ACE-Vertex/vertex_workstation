from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PAGE = ROOT / "src" / "features" / "ray" / "RayPage.tsx"
HANDOFF = ROOT / "src" / "features" / "ray" / "rayHandoff.ts"
CSS = ROOT / "src" / "features" / "ray" / "ray.css"

for path in (PAGE, HANDOFF, CSS):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

page = PAGE.read_text(encoding="utf-8", errors="replace")
handoff = HANDOFF.read_text(encoding="utf-8", errors="replace")
css = CSS.read_text(encoding="utf-8", errors="replace")
combined = page + "\n" + handoff + "\n" + css

checks = {
    "DEEP_RAY_AUTO_CLIP":
        "function runDeepRay()" in page
        and 'setMode("DEEP")' in page
        and 'void copyRayToClipboard("DEEP")' in page,
    "MANUAL_RECOPY":
        "COPY RAY → VERA" in page
        and "function copyCurrentRay()" in page,
    "CLIPBOARD_HUMAN_RELAY":
        "navigator.clipboard.writeText(capsule)" in page,
    "CLIP_PROCESSING_STATE":
        '"CLIPPING"' in page
        and "CLIPPING..." in page
        and ".ray-clip-state.clipping" in css
        and "@keyframes ray-clip-pulse" in css,
    "CLIP_SUCCESS_STATE":
        'setClipState("COPIED")' in page
        and ".ray-clip-state.copied" in css,
    "CLIP_FAILURE_STATE":
        'setClipState("FAILED")' in page
        and "RAY CLIPBOARD FAILED" in page,
    "HANDOFF_SCHEMA":
        'RAY_HANDOFF_SCHEMA = "ray-vera-handoff/1"' in handoff,
    "HANDOFF_READ_ONLY_AUTHORITY":
        '"AUTHORITY: RAY_READ_ONLY_EVIDENCE"' in handoff
        and '"MUTATION: NONE"' in handoff,
    "HANDOFF_PROJECT_SCOPE":
        '"=== PROJECT SCOPE ==="' in handoff
        and "SCANNED_FILES" in handoff
        and "SKIPPED_FILES" in handoff,
    "HANDOFF_ACTIVE_TARGET":
        '"=== ACTIVE TARGET ==="' in handoff
        and "RELATIVE_PATH" in handoff
        and "PROVENANCE" in handoff,
    "HANDOFF_TARGET_SET":
        '"=== TARGET SET ==="' in handoff
        and "targetLines(targets)" in handoff,
    "HANDOFF_LINE_FACTS":
        "IMPORT_USE_MOD_FACTS" in handoff
        and "SYMBOL_FACTS" in handoff
        and "L${fact.line}:C${fact.column}" in handoff,
    "HANDOFF_FINDINGS":
        '"=== EVIDENCE / FINDINGS ==="' in handoff
        and "CONFIDENCE" in handoff
        and "EVIDENCE:" in handoff,
    "HANDOFF_SOURCE_SNAPSHOT":
        '"=== SOURCE SNAPSHOT BEGIN ==="' in handoff
        and "source.content" in handoff
        and '"=== SOURCE SNAPSHOT END ==="' in handoff,
    "HANDOFF_RUNTIME_TRUTH_BOUNDARY":
        "Do not infer unobserved runtime behavior from source evidence alone." in handoff,
    "RAY_000023_EXPLORER_PRESERVED":
        "symbolFacts={facts.symbolFacts}" in page
        and "onRevealLine=" in page,
    "NO_BROWSER_INJECTION":
        all(token not in combined for token in (
            ".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild(",
            "document.execCommand(", "dispatchEvent(new ClipboardEvent"
        )),
    "NO_FLOAT_UI":
        "position: fixed" not in css,
}

for name, ok in checks.items():
    print(name + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

commands = [
    (
        [r"C:\Program Files\nodejs\npm.cmd", "run", "build"],
        "FRONTEND_BUILD",
    ),
    (
        ["cargo", "check", "--manifest-path", str(ROOT / "src-tauri" / "Cargo.toml")],
        "CARGO_CHECK",
    ),
    (
        ["python", str(ROOT / "scripts" / "verify_ray_explorer_arborist_line_evidence_000023.py")],
        "RAY_000023_REGRESSION",
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

print("RAY_DEEP_ACTION=ANALYZE_PLUS_CLIP")
print("RAY_HANDOFF_TRANSPORT=CLIPBOARD_HUMAN_PASTE")
print("RAY_HANDOFF_DESTINATION=VERA")
print("RAY_HANDOFF_SOURCE=ACTIVE_FILE_PLUS_TARGET_SET_PLUS_LINE_EVIDENCE")
print("RAY_DIRECT_CHAT_INJECTION=NO")
print("RAY_DEEP_CLIPBOARD_VERA_HANDOFF_000024=PASS")

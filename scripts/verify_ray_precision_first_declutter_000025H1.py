from pathlib import Path
import re
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PAGE = ROOT / "src" / "features" / "ray" / "RayPage.tsx"
CSS = ROOT / "src" / "features" / "ray" / "ray.css"
ANALYSIS = ROOT / "src" / "features" / "ray" / "rayAnalysis.ts"

for path in (PAGE, CSS, ANALYSIS):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

page = PAGE.read_text(encoding="utf-8", errors="replace")
css = CSS.read_text(encoding="utf-8", errors="replace")
analysis = ANALYSIS.read_text(encoding="utf-8", errors="replace")

operation_indicator_guard = re.search(
    r"\{operation\s*\?\s*\(\s*<OperationIndicator\b.*?/>\s*\)\s*:\s*null\s*\}",
    page,
    flags=re.S,
)

checks = {
    "IDLE_FILE_SIGHT_BANNER_REMOVED":
        "FILE SIGHT READY" not in page,
    "DECORATIVE_RAY_ENGINE_READY_REMOVED":
        'system="RAY ENGINE"' not in page,
    "TARGET_POLICY_PROSE_REMOVED":
        "TARGET POLICY" not in page
        and "HUMAN PRIORITY → FILE SIGHT → DEPENDENCY CLUES → MACHINE RELEVANCE" not in page,
    "PROCESSING_INDICATOR_PRESERVED":
        operation_indicator_guard is not None
        and 'system="RAY"' in operation_indicator_guard.group(0)
        and "phase={operation.phase}" in operation_indicator_guard.group(0)
        and "startedAt={operation.startedAt}" in operation_indicator_guard.group(0),
    "NO_IDLE_OPERATION_INDICATOR":
        operation_indicator_guard is not None
        and 'active={Boolean(operation)}' not in operation_indicator_guard.group(0),
    "PROCESSING_GRID_DISTORTION_ALLOWED":
        "ProcessingGridDistortion" in page,
    "COMMAND_BAR_COMPACT":
        "grid-template-columns: 1fr auto auto auto auto;" in css,
    "DEEP_RAY_CLIP_PRESERVED":
        'void copyRayToClipboard("DEEP")' in page
        and "COPY RAY → VERA" in page,

    # Inline 000025 language-aware precision checks.
    # H1 superseded plain 000025, so this verifier must not depend on
    # a script that may never have been installed.
    "LANGUAGE_SWITCH":
        "type RayLanguage =" in analysis
        and "languageFor(source)" in analysis,
    "PYTHON_FROM_IMPORT":
        "python-from-import" in analysis
        and "fromImport" in analysis,
    "PYTHON_DIRECT_IMPORT":
        "python-import" in analysis
        and "directImport" in analysis,
    "PYTHON_ASYNC_DEF":
        "python-async-function" in analysis,
    "PYTHON_DEF":
        "python-function" in analysis,
    "PYTHON_CLASS":
        "python-class" in analysis,
    "PYTHON_DECORATOR":
        "python-decorator" in analysis,
    "PYTHON_MODULE_BINDING":
        "python-module-binding" in analysis
        and "zero-indentation assignments" in analysis,
    "TS_ESM_IMPORT":
        "esm-import" in analysis
        and "esm-side-effect-import" in analysis,
    "TS_COMMONJS_REQUIRE":
        "commonjs-require" in analysis,
    "TS_INTERFACE_TYPE_ENUM":
        "interfaceMatch" in analysis
        and "typeMatch" in analysis
        and "enumMatch" in analysis,
    "TS_ARROW_FUNCTION":
        "arrow-function" in analysis,
    "TS_REACT_HOOK_CANDIDATE":
        "react-hook-candidate" in analysis,
    "TS_REACT_COMPONENT_CANDIDATE":
        "react-component-candidate" in analysis,
    "TS_EVENT_HANDLER_CANDIDATE":
        "event-handler-candidate" in analysis,
    "RUST_FACTS_PRESERVED":
        "rust-use" in analysis
        and "rust-mod" in analysis
        and "rust-function" in analysis,
    "LINE_COLUMN_PRESERVED":
        "line: lineNumber" in analysis
        and "column: firstColumn" in analysis,
    "NO_FLOAT_UI":
        "position: fixed" not in css,
}

for name, ok in checks.items():
    print(name + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

commands = [
    (
        ["python", str(ROOT / "scripts" / "verify_ray_deep_clipboard_vera_handoff_000024.py")],
        "RAY_000024_CLIPBOARD",
    ),
    (
        [r"C:\Program Files\nodejs\npm.cmd", "run", "build"],
        "FRONTEND_BUILD",
    ),
    (
        ["cargo", "check", "--manifest-path", str(ROOT / "src-tauri" / "Cargo.toml")],
        "CARGO_CHECK",
    ),
    (
        ["python", str(ROOT / "scripts" / "verify_forge_real_apply_rollback_000022.py")],
        "FORGE_000022_REGRESSION",
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

print("HOTFIX=000025H3_VERIFIER_SELF_CONTAINED")
print("CAUSE=H2_REFERENCED_NONINSTALLED_PLAIN_000025_VERIFIER")
print("RUNTIME_MUTATION=NO")
print("RAY_LANGUAGE_PRECISION_CHECK=INLINE_SELF_CONTAINED")
print("RAY_IDLE_DECORATION=REMOVED")
print("RAY_PROCESSING_VISIBILITY=PRESERVED_WHEN_ACTIVE")
print("RAY_TARGET_POLICY_PROSE=REMOVED")
print("RAY_PRECISION_FIRST_DECLUTTER_000025H3=PASS")

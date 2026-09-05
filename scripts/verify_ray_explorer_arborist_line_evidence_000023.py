from pathlib import Path
import json
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

FILES = {
    "models": ROOT / "src" / "features" / "ray" / "models.ts",
    "analysis": ROOT / "src" / "features" / "ray" / "rayAnalysis.ts",
    "tree_model": ROOT / "src" / "features" / "ray" / "rayTree.ts",
    "tree": ROOT / "src" / "features" / "ray" / "RayProjectTree.tsx",
    "source": ROOT / "src" / "features" / "ray" / "RaySourceViewer.tsx",
    "evidence": ROOT / "src" / "features" / "ray" / "RayEvidence.tsx",
    "page": ROOT / "src" / "features" / "ray" / "RayPage.tsx",
    "css": ROOT / "src" / "features" / "ray" / "ray.css",
}

for path in FILES.values():
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

text = {name: path.read_text(encoding="utf-8", errors="replace") for name, path in FILES.items()}
combined = "\n".join(text.values())

package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
declared = (package.get("dependencies") or {}).get("react-arborist")

checks = {
    "REACT_ARBORIST_PINNED_3_16_0":
        declared == "3.16.0",
    "ARBORIST_PRESENTATION_PORT":
        'from "react-arborist"' in text["tree"]
        and "<Tree<RayTreeNode>" in text["tree"],
    "ARBORIST_VIRTUALIZED":
        "rowHeight={30}" in text["tree"]
        and "overscanCount={8}" in text["tree"],
    "ARBORIST_KEYBOARD_SELECTION_SYNC":
        "selection={activeId ?? undefined}" in text["tree"]
        and "node.handleClick(event)" in text["tree"],
    "ARBORIST_FILTERING":
        "searchTerm={searchTerm}" in text["tree"]
        and "searchMatch=" in text["tree"],
    "RAY_READ_ONLY_TREE":
        "disableEdit" in text["tree"]
        and "disableDrag" in text["tree"]
        and "disableDrop" in text["tree"],
    "TREE_FOLDER_FILE_SYMBOL":
        'RayTreeNodeKind = "folder" | "file" | "symbol"' in text["tree_model"]
        and "buildRayProjectTree" in text["tree_model"],
    "TREE_STABLE_FOLDER_IDS":
        'return `dir:${relativePath.replaceAll' in text["tree_model"],
    "SYMBOLS_HAVE_LINE_COLUMN":
        "readonly line: number" in text["models"]
        and "readonly column: number" in text["models"]
        and "symbolFacts" in text["analysis"],
    "IMPORTS_HAVE_LINE_COORDINATES":
        "importFacts" in text["analysis"]
        and "line: lineNumber" in text["analysis"],
    "EVIDENCE_HAS_LINE_COORDINATES":
        "lineStart?: number" in text["models"]
        and "REVEAL L" in text["evidence"],
    "SOURCE_REVEAL_HIGHLIGHT":
        'data-ray-line={lineNumber}' in text["source"]
        and "ray-line-focused" in text["source"],
    "ACTIVE_SYMBOLS_IN_TREE":
        "symbolFacts={facts.symbolFacts}" in text["page"]
        and "onRevealLine=" in text["page"],
    "REAL_FILESYSTEM_API_PRESERVED":
        'invoke<RayScanResult>("ray_scan_project"' in (
            ROOT / "src" / "features" / "ray" / "rayApi.ts"
        ).read_text(encoding="utf-8", errors="replace"),
    "QUICK_DEEP_ANALYSIS_PRESERVED":
        'mode === "QUICK"' in text["page"]
        and 'mode === "DEEP"' in text["page"],
    "PROCESSING_INDICATOR_PRESERVED":
        "OperationIndicator" in text["page"]
        and "ProcessingGridDistortion" in text["page"],
    "NO_FLOAT_UI":
        "position: fixed" not in text["css"],
    "NO_IMPERATIVE_DOM_MUTATION":
        all(token not in combined for token in (
            ".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild("
        )),
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

print("RAY_TREE_ENGINE=REACT_ARBORIST_3_16_0")
print("RAY_TREE_OWNERSHIP=PRESENTATION_ONLY")
print("RAY_FILESYSTEM_OWNER=TAURI_RUST")
print("RAY_MUTATION=NO")
print("RAY_SYMBOL_EVIDENCE=LINE_COLUMN_AWARE")
print("RAY_EVIDENCE_REVEAL=SOURCE_LINE")
print("RAY_EXPLORER_ARBORIST_LINE_EVIDENCE_000023=PASS")

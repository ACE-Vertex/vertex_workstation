from pathlib import Path
import json, re, subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

if ROOT.name.lower() != "vertex_workstation":
    raise SystemExit("WRONG_PROJECT_ROOT=" + str(ROOT))

required = [
    "package.json",
    "index.html",
    "tsconfig.json",
    "vite.config.ts",
    "src/main.tsx",
    "src/App.tsx",
    "src/core/contracts.ts",
    "src/core/componentRegistry.ts",
    "src/layout/layoutModel.ts",
    "src/presentation/PresentationPort.tsx",
    "src/components/ForgeSeed.tsx",
    "src/styles.css",
    "src-tauri/Cargo.toml",
    "src-tauri/src/main.rs",
    "src-tauri/src/lib.rs",
    "src-tauri/tauri.conf.json",
]
for rel in required:
    if not (ROOT/rel).exists():
        raise SystemExit("MISSING=" + rel)

pkg = json.loads((ROOT/"package.json").read_text(encoding="utf-8"))
deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

checks = {
    "REACT": "react" in deps and "react-dom" in deps,
    "TYPESCRIPT": "typescript" in deps,
    "VITE": "vite" in deps and "@vitejs/plugin-react" in deps,
    "TAURI_JS": "@tauri-apps/api" in deps and "@tauri-apps/cli" in deps,
    "NEXT_ABSENT": "next" not in deps,
}

src_files = list((ROOT/"src").rglob("*.ts")) + list((ROOT/"src").rglob("*.tsx"))
src_text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in src_files)

forbidden_imperative_dom = [
    ".appendChild(",
    ".insertBefore(",
    ".replaceChild(",
    ".removeChild(",
    "document.body.append",
    "document.body.prepend",
]
checks["NO_IMPERATIVE_DOM_REPARENT"] = not any(x in src_text for x in forbidden_imperative_dom)
checks["COMPONENT_REGISTRY"] = "componentId: \"forge.seed\"" in src_text
checks["OWNERSHIP_CONTRACT"] = all(
    x in src_text for x in (
        "logicalOwner",
        "stateOwner",
        "serviceOwner",
        "styleOwner",
        "deletePolicy",
    )
)
checks["PRESENTATION_PORT"] = "function PresentationPort" in src_text
checks["LAYOUT_SLOTS"] = all(x in src_text for x in ('"A1"', '"B1"', '"C1"'))

for key, value in checks.items():
    print(key + "=" + ("PASS" if value else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace")
    print("RUN=" + " ".join(map(str, cmd)))
    if p.stdout:
        print(p.stdout.encode("ascii", "backslashreplace").decode("ascii"))
    if p.stderr:
        print(p.stderr.encode("ascii", "backslashreplace").decode("ascii"))
    if p.returncode:
        raise SystemExit(p.returncode)

run(["cargo", "fmt", "--manifest-path", str(ROOT/"src-tauri/Cargo.toml"), "--", "--check"])

print("PROJECT_ROOT=" + str(ROOT))
print("FOUNDATION_STACK=REACT_TYPESCRIPT_VITE_TAURI_RUST")
print("DOM_OWNERSHIP_POLICY=RENDER_OUTPUT_ONLY")
print("VERTEX_WORKS_MUTATION=NO")
print("WORKSTATION_FOUNDATION_000001_STATIC=PASS")

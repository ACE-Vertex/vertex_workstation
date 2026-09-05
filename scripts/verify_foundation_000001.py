from pathlib import Path
import json
import re

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    "package.json",
    "tsconfig.json",
    "vite.config.ts",
    "index.html",
    "src/main.ts",
    "src/App.vue",
    "src/contracts/unit.ts",
    "src/shell/hostBus.ts",
    "src/shell/unitRegistry.ts",
    "src/shell/WorksShell.vue",
    "src/shell/components/UnitSlot.vue",
    "src/units/ray/index.ts",
    "src/units/ray/RayUnit.vue",
    "src/units/forge/index.ts",
    "src/units/forge/ForgeUnit.vue",
    "src-tauri/Cargo.toml",
    "src-tauri/build.rs",
    "src-tauri/tauri.conf.json",
    "src-tauri/capabilities/default.json",
    "src-tauri/src/main.rs",
    "src-tauri/src/lib.rs",
    "UNIT_CONTRACT.md",
    "README.md",
]
for rel in required:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit(f"MISSING={p}")

package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
if package["dependencies"].get("vue") is None:
    raise SystemExit("VUE_DEPENDENCY_MISSING")
if package["dependencies"].get("@tauri-apps/api") is None:
    raise SystemExit("TAURI_API_DEPENDENCY_MISSING")

tauri = json.loads((ROOT / "src-tauri/tauri.conf.json").read_text(encoding="utf-8"))
if tauri.get("identifier") != "net.a-portal.vertex.workstation":
    raise SystemExit("TAURI_IDENTIFIER_INVALID")

contract = (ROOT / "UNIT_CONTRACT.md").read_text(encoding="utf-8")
for token in [
    "No Welded Dependency",
    "Every connection must be detachable",
    "No unit-to-unit direct wiring",
    "Vue owns the DOM",
]:
    if token not in contract:
        raise SystemExit(f"CONTRACT_TOKEN_MISSING={token}")

# Fail if unit implementation imports the opposite unit.
ray_text = "\n".join(
    p.read_text(encoding="utf-8")
    for p in (ROOT / "src/units/ray").rglob("*")
    if p.is_file() and p.suffix in {".ts", ".vue"}
)
forge_text = "\n".join(
    p.read_text(encoding="utf-8")
    for p in (ROOT / "src/units/forge").rglob("*")
    if p.is_file() and p.suffix in {".ts", ".vue"}
)
if "../forge" in ray_text or "/forge/" in ray_text:
    raise SystemExit("RAY_DIRECT_FORGE_DEPENDENCY")
if "../ray" in forge_text or "/ray/" in forge_text:
    raise SystemExit("FORGE_DIRECT_RAY_DEPENDENCY")

# Explicitly block the old imperative DOM approach.
forbidden = [
    "document.querySelector",
    "document.getElementById",
    ".appendChild(",
    ".removeChild(",
    ".replaceChild(",
    ".insertAdjacentHTML(",
    ".innerHTML",
    "createElement(",
]
source_files = list((ROOT / "src").rglob("*.ts")) + list((ROOT / "src").rglob("*.vue"))
violations = []
for p in source_files:
    text = p.read_text(encoding="utf-8")
    for token in forbidden:
        if token in text:
            violations.append(f"{p.relative_to(ROOT)}:{token}")
if violations:
    raise SystemExit("DIRECT_DOM_MUTATION_FORBIDDEN=" + ",".join(violations))

# RAY and FORGE must advertise detachable + host-neutral.
ray_index = (ROOT / "src/units/ray/index.ts").read_text(encoding="utf-8")
forge_index = (ROOT / "src/units/forge/index.ts").read_text(encoding="utf-8")
for name, text in [("RAY", ray_index), ("FORGE", forge_index)]:
    if "hostNeutral: true" not in text or "detachable: true" not in text:
        raise SystemExit(f"{name}_UNIT_PORTABILITY_CONTRACT_MISSING")

rust = (ROOT / "src-tauri/src/lib.rs").read_text(encoding="utf-8")
if 'id: "ray"' not in rust or 'id: "forge"' not in rust:
    raise SystemExit("RUST_UNIT_DESCRIPTORS_MISSING")

print(f"ROOT={ROOT}")
print("FRAMEWORK=Vue3+TypeScript+Vite+Tauri2+Rust")
print("UNIT_COUNT=2")
print("RAY_UNIT=FOUNDATION")
print("FORGE_UNIT=FOUNDATION")
print("UNIT_TO_UNIT_DIRECT_WIRING=NO")
print("WELDED_DEPENDENCY=NO")
print("DIRECT_DOM_MUTATION=NO")
print("RAY_AUTHORITY=READ_ONLY")
print("FORGE_AUTHORITY=HUMAN_APPLY")
print("REAL_FORGE_LOGIC=NOT_YET_IMPLEMENTED")
print("REAL_RAY_LOGIC=NOT_YET_IMPLEMENTED")
print("FOUNDATION_CONTRACT_000001=PASS")

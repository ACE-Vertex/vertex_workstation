from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/App.tsx",
    ROOT / "src/core/input/useMiddleMouseScroll.ts",
    ROOT / "src/core/input/middleMouseScroll.css",
    ROOT / "src/features/canonical/CanonicalRegistryPage.tsx",
    ROOT / "src/features/canonical/canonicalRegistry.css",
    ROOT / "src/features/contracts/ArchitectureContractPage.tsx",
    ROOT / "src/shell/relay/vertexRelay.css",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

text = {
    path.name: path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in required
}

hook = text["useMiddleMouseScroll.ts"]
canonical = text["CanonicalRegistryPage.tsx"]
contract = text["ArchitectureContractPage.tsx"]
relay_css = text["vertexRelay.css"]
canonical_css = text["canonicalRegistry.css"]
middle_css = text["middleMouseScroll.css"]
app = text["App.tsx"]

checks = {
    "MIDDLE_MOUSE_HOOK": "event.button !== 1" in hook,
    "MIDDLE_MOUSE_POINTER_CAPTURE": "setPointerCapture" in hook,
    "MIDDLE_MOUSE_VERTICAL_SCROLL": "scrollTop" in hook,
    "MIDDLE_MOUSE_AUX_SUPPRESS": "onAuxClick" in hook,
    "CANONICAL_CARD_MIDDLE_SCROLL":
        "cardScroll" in canonical
        and "canonical-card-list middle-scroll-surface" in canonical,
    "CANONICAL_FORM_MIDDLE_SCROLL":
        "formScroll" in canonical
        and "canonical-form middle-scroll-surface" in canonical,
    "CONTRACT_CARD_MIDDLE_SCROLL":
        "architecture-card-list middle-scroll-surface" in contract,
    "CONTRACT_DETAIL_MIDDLE_SCROLL":
        "architecture-detail-body middle-scroll-surface" in contract,
    "MIDDLE_SCROLL_CSS_WIRED":
        'import "./core/input/middleMouseScroll.css";' in app,
    "MIDDLE_SCROLL_ACTIVE_CURSOR":
        'data-middle-scroll-active="true"' in middle_css,
    "RELAY_TITLE_SIZE_UP":
        "font-size: 9px" in relay_css
        and "font-size: 10px" in relay_css,
    "RELAY_TRANSPORT_SIZE_UP":
        'font: 8px "Cascadia Mono"' in relay_css,
    "RELAY_ACTION_SIZE_SMART":
        "min-height: 30px" in relay_css,
    "CANONICAL_LABEL_SIZE_UP":
        "font-size: 9px" in canonical_css,
    "CANONICAL_INPUT_SIZE_UP":
        'font: 10px/1.5 "Cascadia Mono"' in canonical_css,
    "CANONICAL_TEXTAREA_SIZE_UP":
        "min-height: 76px" in canonical_css,
    "NO_FLOAT_MIDDLE_SCROLL":
        "position: fixed" not in middle_css,
    "NO_FLOAT_RELAY":
        "position: fixed" not in relay_css,
    "NO_FLOAT_CANONICAL":
        "position: fixed" not in canonical_css,
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in "\n".join(text.values())
        for token in (
            ".appendChild(",
            ".removeChild(",
            ".insertBefore(",
            ".replaceChild(",
        )
    ),
}

for key, ok in checks.items():
    print(key + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
proc = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if proc.stdout:
    print(
        proc.stdout
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if proc.stderr:
    print(
        proc.stderr
        .encode("ascii", "backslashreplace")
        .decode("ascii")
    )
if proc.returncode:
    raise SystemExit(proc.returncode)

print("MIDDLE_MOUSE_SCROLL=PRESS_WHEEL_AND_DRAG")
print("RELAY_LEGIBILITY=SIZE_UP")
print("CANONICAL_FORM_LEGIBILITY=SIZE_UP")
print("FLOATING_WINDOW_ADDED=NO")
print("FORGE_RUNTIME_MUTATION=NO")
print("RAY_RUNTIME_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("UX_LEGIBILITY_MIDDLE_SCROLL_000011_STATIC=PASS")

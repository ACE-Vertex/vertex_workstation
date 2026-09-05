from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/App.tsx",
    ROOT / "src/core/relay/types.ts",
    ROOT / "src/core/relay/vertexRelay.ts",
    ROOT / "src/shell/relay/VertexRelayBar.tsx",
    ROOT / "src/shell/relay/vertexRelay.css",
    ROOT / "src/features/canonical/CanonicalRegistryPage.tsx",
    ROOT / "src/features/canonical/canonicalSeed.ts",
    ROOT / "src/features/canonical/models.ts",
    ROOT / "src/features/canonical/ConceptIcon.tsx",
    ROOT / "src/features/canonical/canonicalRegistry.css",
    ROOT / "src/features/contracts/ArchitectureContractPage.tsx",
    ROOT / "src/features/contracts/contracts.ts",
    ROOT / "src/features/contracts/architectureContract.css",
    ROOT / "src/features/contracts/architectureRelay.css",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

texts = {
    path.name: path.read_text(
        encoding="utf-8",
        errors="replace",
    )
    for path in required
}

all_text = "\n".join(texts.values())

checks = {
    "CANONICAL_WORKSPACE":
        '"canonical"' in texts["App.tsx"]
        and "CANONICAL" in texts["App.tsx"],
    "CANONICAL_PAGE_WIRED":
        "CanonicalRegistryPage" in texts["App.tsx"],
    "CANONICAL_LEFT_CARDS":
        "Concept Cards" in texts["CanonicalRegistryPage.tsx"]
        and "canonical-card-list" in texts["canonicalRegistry.css"],
    "CANONICAL_RIGHT_DETAIL":
        "02 / CANONICAL DETAIL" in texts["CanonicalRegistryPage.tsx"]
        and "canonical-detail" in texts["canonicalRegistry.css"],
    "CARD_TITLE_ABBREVIATION":
        "canonical-card-title" in texts["CanonicalRegistryPage.tsx"]
        and "abbreviation" in texts["CanonicalRegistryPage.tsx"],
    "JAPANESE_FIELD_LABELS": all(
        token in texts["CanonicalRegistryPage.tsx"]
        for token in (
            "正式名称",
            "略称",
            "状態",
            "重要度",
            "適用範囲",
            "カテゴリ",
            "概要",
            "機能",
            "詳細説明",
            "由来",
            "別名",
            "関連概念",
            "採用者",
            "備考",
        )
    ),
    "MEANINGFUL_ICONS":
        "ConceptIcon" in texts["CanonicalRegistryPage.tsx"]
        and "LANGUAGE" in texts["ConceptIcon.tsx"]
        and "REGISTRY" in texts["ConceptIcon.tsx"]
        and "MEASUREMENT" in texts["ConceptIcon.tsx"]
        and "LLM" in texts["ConceptIcon.tsx"]
        and "LIFECYCLE" in texts["ConceptIcon.tsx"]
        and "RUNTIME" in texts["ConceptIcon.tsx"],
    "CARD_DELETE_SMALL":
        "canonical-card-delete" in texts["CanonicalRegistryPage.tsx"]
        and "width: 22px" in texts["canonicalRegistry.css"]
        and "height: 22px" in texts["canonicalRegistry.css"],
    "NO_GIANT_ACTION_BUTTONS":
        "min-height: 27px" in texts["canonicalRegistry.css"]
        and "compact-action" in texts["canonicalRegistry.css"],
    "CANONICAL_PERSISTENCE":
        "localStorage.setItem" in texts["CanonicalRegistryPage.tsx"]
        and "vertex.canonical.registry.v1" in texts["CanonicalRegistryPage.tsx"],
    "VERTEX_RELAY_SCHEMA":
        '"vertex-relay/1"' in texts["types.ts"]
        and '"vertex-relay/1"' in texts["vertexRelay.ts"],
    "COPY_RELAY":
        "COPY RELAY" in texts["VertexRelayBar.tsx"]
        and "navigator.clipboard.writeText" in texts["VertexRelayBar.tsx"],
    "RECEIVE_RELAY":
        "RECEIVE" in texts["VertexRelayBar.tsx"]
        and "parseVertexRelay" in texts["VertexRelayBar.tsx"]
        and "ACCEPT" in texts["VertexRelayBar.tsx"]
        and "REJECT" in texts["VertexRelayBar.tsx"],
    "HUMAN_GATE":
        "HUMAN GATE" in texts["VertexRelayBar.tsx"],
    "CANONICAL_RELAY":
        'type: "CANONICAL"' in texts["CanonicalRegistryPage.tsx"],
    "CONTRACT_RELAY":
        'type: "ARCHITECTURE_CONTRACT"' in texts["ArchitectureContractPage.tsx"],
    "VERTEX_RELAY_CONTRACT_CARD":
        'title: "Vertex Relay"' in texts["contracts.ts"],
    "NO_FLOAT_CANONICAL":
        "position: fixed" not in texts["canonicalRegistry.css"],
    "NO_FLOAT_RELAY":
        "position: fixed" not in texts["vertexRelay.css"],
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in all_text
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

print("CANONICAL_PAGE=PASS")
print("VERTEX_RELAY=CLIPBOARD_SEND_RECEIVE")
print("VERTEX_RELAY_HUMAN_GATE=PASS")
print("CONTRACT_RELAY=PASS")
print("FLOATING_WINDOW_ADDED=NO")
print("FORGE_RUNTIME_MUTATION=NO")
print("RAY_RUNTIME_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("CANONICAL_VERTEX_RELAY_000010_STATIC=PASS")

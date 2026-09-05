from pathlib import Path

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/IncomingCargo.tsx",
    ROOT / "src/features/forge/ArtifactInspector.tsx",
    ROOT / "src/features/forge/PathSwitcher.tsx",
    ROOT / "src/features/forge/forgeApi.ts",
    ROOT / "src/features/forge/forgeRuntime.css",
    ROOT / "src-tauri/src/lib.rs",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

page = (ROOT / "src/features/forge/ForgePage.tsx").read_text(
    encoding="utf-8",
    errors="replace",
)
incoming = (ROOT / "src/features/forge/IncomingCargo.tsx").read_text(
    encoding="utf-8",
    errors="replace",
)
inspector = (ROOT / "src/features/forge/ArtifactInspector.tsx").read_text(
    encoding="utf-8",
    errors="replace",
)
switcher = (ROOT / "src/features/forge/PathSwitcher.tsx").read_text(
    encoding="utf-8",
    errors="replace",
)
api = (ROOT / "src/features/forge/forgeApi.ts").read_text(
    encoding="utf-8",
    errors="replace",
)
runtime_css = (ROOT / "src/features/forge/forgeRuntime.css").read_text(
    encoding="utf-8",
    errors="replace",
)
rust = (ROOT / "src-tauri/src/lib.rs").read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "REAL_RECEIVING_SCAN":
        'invoke<ForgeScanResult>("forge_scan_receiving_bay"' in api,
    "REAL_VRA_ZIP_INSPECTION":
        "ZipArchive" in rust and 'by_name("manifest.json")' in rust,
    "MANIFEST_SIZE_BOUND":
        "MAX_VRA_MANIFEST_BYTES" in rust,
    "VRA_SCHEMA_GATE":
        'artifact.schema_version != "vra/1"' in rust,
    "HUMAN_APPLY_GATE":
        'artifact.authority != "HUMAN_APPLY"' in rust,
    "AUTHORIZED_ROOT_GATE":
        "TARGET_OUTSIDE_AUTHORIZED_PRODUCTION_ROOT" in rust,
    "REAL_OPERATION_PREVIEW":
        "operation_preview" in rust and "OPERATION PREVIEW" in inspector,
    "FORGE_FOLDER_PICKER":
        "forge_pick_folder" in rust
        and "pickForgeFolder" in api
        and "onBrowse" in switcher
        and "BROWSE" in switcher
        and 'onBrowse={() => void browsePath("receivingBay")}' in page
        and 'onBrowse={() => void browsePath("productionRoot")}' in page,
    "REFRESH_WIRED":
        "onRefresh" in incoming
        and "SCANNING..." in incoming
        and "onRefresh={() => void refresh()}" in page,
    "NO_FAKE_FOUNDATION_ARTIFACTS":
        "FOUNDATION_ARTIFACTS" not in page
        and "FOUNDATION_ARTIFACTS" not in incoming,
    "REAL_STAGE_COEXISTS":
        "forge_stage_artifact" in rust
        and "stageForgeArtifact" in api
        and "onStage" in inspector,
    "COPY_INSPECTION":
        "COPY INSPECTION" in inspector
        and "navigator.clipboard.writeText" in page,
    "PROCESSING_SWEEP":
        "forge-receiving-sweep" in runtime_css
        and ".forge-activity.busy::after" in runtime_css,
    "CANONICAL_DISPLAY_PATH_FIX":
        'strip_prefix("\\\\\\\\?\\\\")' in rust,
    "RAY_COMMANDS_PRESERVED": all(
        token in rust
        for token in (
            "ray_scan_project",
            "ray_read_project_file",
            "ray_pick_project_root",
        )
    ),
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in (
            page
            + incoming
            + inspector
            + switcher
            + api
        )
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

print("FORGE_RECEIVING_REGRESSION=PASS")
print("FORGE_FOLDER_PICKER_EVIDENCE=PATHSWITCHER+FORGEPAGE+TAURI_COMMAND")
print("PROCESSING_SWEEP_EVIDENCE=FORGERUNTIME_CSS")
print("REAL_STAGE_COEXISTS=PASS")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_RECEIVING_REGRESSION_000008H2=PASS")

from pathlib import Path

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/IncomingCargo.tsx",
    ROOT / "src/features/forge/ArtifactInspector.tsx",
    ROOT / "src/features/forge/forgeApi.ts",
    ROOT / "src-tauri/src/lib.rs",
]

for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

text = "\n".join(
    path.read_text(encoding="utf-8", errors="replace")
    for path in required
)
rust = (ROOT / "src-tauri/src/lib.rs").read_text(
    encoding="utf-8",
    errors="replace",
)

checks = {
    "REAL_RECEIVING_SCAN": 'invoke<ForgeScanResult>("forge_scan_receiving_bay"' in text,
    "REAL_VRA_ZIP_INSPECTION": "ZipArchive" in rust and 'by_name("manifest.json")' in rust,
    "MANIFEST_SIZE_BOUND": "MAX_VRA_MANIFEST_BYTES" in rust,
    "VRA_SCHEMA_GATE": 'artifact.schema_version != "vra/1"' in rust,
    "HUMAN_APPLY_GATE": 'artifact.authority != "HUMAN_APPLY"' in rust,
    "AUTHORIZED_ROOT_GATE": "TARGET_OUTSIDE_AUTHORIZED_PRODUCTION_ROOT" in rust,
    "REAL_OPERATION_PREVIEW": "operation_preview" in rust and "OPERATION PREVIEW" in text,
    "FORGE_FOLDER_PICKER": "forge_pick_folder" in rust and "BROWSE" in text,
    "REFRESH_WIRED": "onRefresh" in text and "SCANNING..." in text,
    "NO_FAKE_FOUNDATION_ARTIFACTS": "FOUNDATION_ARTIFACTS" not in text,
    # 000007 asserted STAGE had to remain fake/disabled. That invariant is
    # intentionally retired by 000008. The receiving regression gate now checks
    # only receiving/inspection behavior and requires real Stage to coexist.
    "REAL_STAGE_COEXISTS": "forge_stage_artifact" in rust and 'stageForgeArtifact' in text,
    "COPY_INSPECTION": "COPY INSPECTION" in text and "navigator.clipboard.writeText" in text,
    "PROCESSING_SWEEP": "forge-receiving-sweep" in text,
    "CANONICAL_DISPLAY_PATH_FIX": 'strip_prefix("\\\\\\\\?\\\\")' in rust,
    "RAY_COMMANDS_PRESERVED": all(
        token in rust
        for token in (
            "ray_scan_project",
            "ray_read_project_file",
            "ray_pick_project_root",
        )
    ),
    "NO_IMPERATIVE_DOM_REPARENT": all(
        token not in text
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
print("OBSOLETE_000007_NO_FAKE_STAGE_ASSERTION=RETIRED")
print("VERTEX_WORKS_MUTATION=NO")

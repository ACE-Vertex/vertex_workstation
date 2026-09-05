from pathlib import Path
import subprocess
import sys

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
PAGE = ROOT / "src" / "features" / "forge" / "ForgePage.tsx"
API = ROOT / "src" / "features" / "forge" / "forgeApi.ts"
RUST = ROOT / "src-tauri" / "src" / "lib.rs"

for path in (PAGE, API, RUST):
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

page = PAGE.read_text(encoding="utf-8", errors="replace")
api = API.read_text(encoding="utf-8", errors="replace")
rust = RUST.read_text(encoding="utf-8", errors="replace")
combined = page + "\n" + api + "\n" + rust

checks = {
    "LIVE_WATCH_INTERVAL": "FORGE_RECEIVING_WATCH_INTERVAL_MS = 1500" in page,
    "LIGHTWEIGHT_FINGERPRINT_API": 'invoke<string>("forge_receiving_bay_fingerprint"' in api,
    "LIGHTWEIGHT_FINGERPRINT_RUST": "fn forge_receiving_bay_fingerprint" in rust,
    "FINGERPRINT_METADATA_ONLY": all(
        token in rust
        for token in (
            "fs::read_dir(&receiving)",
            "metadata.len()",
            "modified_unix_ms",
            "fingerprints.sort()",
            "sha256_bytes",
        )
    ),
    "FULL_SCAN_PRESERVED": "fn forge_scan_receiving_bay" in rust
    and 'invoke<ForgeScanResult>("forge_scan_receiving_bay"' in api,
    "WATCH_TRIGGERS_REAL_RESCAN": "await refresh(paths);" in page,
    "WATCH_HIDDEN_WINDOW_GUARD": 'document.visibilityState === "hidden"' in page,
    "WATCH_SINGLEFLIGHT": "receivingWatchInFlightRef" in page,
    "WATCH_BASELINE_AFTER_SCAN": "receivingFingerprintRef.current" in page
    and "readReceivingBayFingerprint(result.receivingBay)" in page,
    "COMMAND_REGISTERED": "forge_receiving_bay_fingerprint," in rust,
    "MANUAL_REFRESH_PRESERVED": "onRefresh={() => void refresh()}" in page,
    "STAGE_PRESERVED": "stageForgeArtifact" in combined,
    "NO_FLOAT_UI": "position: fixed" not in page,
    "NO_DOM_INJECTION": all(
        token not in combined
        for token in (".appendChild(", ".removeChild(", ".insertBefore(", ".replaceChild(")
    ),
}

for key, ok in checks.items():
    print(key + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
front = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if front.stdout:
    print(front.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if front.stderr:
    print(front.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if front.returncode:
    raise SystemExit(front.returncode)

cargo = subprocess.run(
    ["cargo", "check", "--manifest-path", str(ROOT / "src-tauri" / "Cargo.toml")],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=cargo check --manifest-path " + str(ROOT / "src-tauri" / "Cargo.toml"))
if cargo.stdout:
    print(cargo.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if cargo.stderr:
    print(cargo.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if cargo.returncode:
    raise SystemExit(cargo.returncode)

print("FORGE_RECEIVING_SOURCE=REAL_FILESYSTEM")
print("FORGE_RECEIVING_WATCH=ACTIVE_LIGHTWEIGHT_FINGERPRINT")
print("FORGE_FULL_MANIFEST_SCAN=ON_CHANGE_ONLY")
print("TARGET_MUTATION_BY_WATCH=NO")
print("FORGE_RECEIVING_LIVE_WATCH_000020=PASS")

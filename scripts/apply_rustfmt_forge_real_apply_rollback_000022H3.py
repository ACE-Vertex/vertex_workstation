from pathlib import Path
import subprocess
import hashlib

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MANIFEST = ROOT / "src-tauri" / "Cargo.toml"
TARGET = ROOT / "src-tauri" / "src" / "forge_apply.rs"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

if not TARGET.exists():
    raise SystemExit("MISSING=" + str(TARGET))

before = sha(TARGET)
print("FORGE_APPLY_RS_SHA256_BEFORE=" + before)

cmd = ["cargo", "fmt", "--manifest-path", str(MANIFEST)]
print("RUN=" + " ".join(cmd))
proc = subprocess.run(
    cmd,
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

after = sha(TARGET)
print("FORGE_APPLY_RS_SHA256_AFTER=" + after)
print("RUSTFMT_CHANGED=" + ("YES" if before != after else "NO"))

check = ["cargo", "fmt", "--manifest-path", str(MANIFEST), "--", "--check"]
print("RUN=" + " ".join(check))
proc = subprocess.run(
    check,
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

print("FORGE_REAL_APPLY_ROLLBACK_RUSTFMT_000022H3=PASS")

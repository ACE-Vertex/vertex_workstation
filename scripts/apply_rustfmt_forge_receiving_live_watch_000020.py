from pathlib import Path
import subprocess
import sys

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MANIFEST = ROOT / "src-tauri" / "Cargo.toml"

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

print("FORGE_RECEIVING_LIVE_WATCH_RUSTFMT=PASS")

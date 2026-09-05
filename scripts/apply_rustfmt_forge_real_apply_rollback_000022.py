from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MANIFEST = ROOT / "src-tauri" / "Cargo.toml"

for args in (
    ["cargo", "fmt", "--manifest-path", str(MANIFEST)],
    ["cargo", "fmt", "--manifest-path", str(MANIFEST), "--", "--check"],
):
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

print("FORGE_REAL_APPLY_ROLLBACK_RUSTFMT=PASS")

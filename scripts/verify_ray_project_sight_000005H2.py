from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
STALE = ROOT / "src/features/ray/seedData.ts"

if STALE.exists():
    raise SystemExit("STALE_SEEDDATA_PRESENT=" + str(STALE))

print("STALE_SEEDDATA_RETIRED=PASS")

commands = [
    ([r"C:\Program Files\nodejs\npm.cmd", "run", "build"], ROOT),
    ([
        "cargo",
        "fmt",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
        "--",
        "--check",
    ], ROOT),
    ([
        "cargo",
        "check",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
    ], ROOT),
]

for args, cwd in commands:
    print("RUN=" + " ".join(args))
    proc = subprocess.run(
        args,
        cwd=cwd,
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

print("TYPESCRIPT_VITE_BUILD=PASS")
print("RUSTFMT_CHECK=PASS")
print("CARGO_CHECK=PASS")
print("RAY_PROJECT_SIGHT_000005H2_VERIFY=PASS")

from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
TS_TARGETS = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/seedData.ts",
]

for path in TS_TARGETS:
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]

    if data.startswith(b"\\"):
        raise SystemExit("LEADING_BACKSLASH_PRESENT=" + str(path))

    text = data.decode("utf-8")

    if path.name == "ForgePage.tsx" and not text.lstrip().startswith("import "):
        raise SystemExit("FORGEPAGE_PREFIX_FAIL=" + str(path))

    if path.name == "seedData.ts" and not text.lstrip().startswith("export "):
        raise SystemExit("SEEDDATA_PREFIX_FAIL=" + str(path))

    print("SOURCE_PREFIX_OK=" + str(path))

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
print("FORGE_REAL_RECEIVING_000007H1_VERIFY=PASS")

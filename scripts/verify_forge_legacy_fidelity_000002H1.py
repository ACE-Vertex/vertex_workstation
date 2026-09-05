from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
FILES = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/seedData.ts",
]

for p in FILES:
    data = p.read_bytes()
    logical = data[3:] if data.startswith(b"\xef\xbb\xbf") else data
    if logical.startswith(b"\\"):
        raise SystemExit("LEADING_BACKSLASH_PRESENT=" + str(p))
    text = data.decode("utf-8-sig")
    if not text.lstrip().startswith("import "):
        raise SystemExit("IMPORT_START_FAIL=" + str(p))
    print("SOURCE_PREFIX_OK=" + str(p))

npm = r"C:\Program Files\nodejs\npm.cmd"
p = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if p.stdout:
    print(p.stdout.encode("ascii","backslashreplace").decode("ascii"))
if p.stderr:
    print(p.stderr.encode("ascii","backslashreplace").decode("ascii"))
if p.returncode:
    raise SystemExit(p.returncode)

print("TYPESCRIPT_VITE_BUILD=PASS")
print("FORGE_LEGACY_FIDELITY_000002H1_VERIFY=PASS")

from pathlib import Path
import subprocess
import hashlib

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

TS_TARGETS = [
    ROOT / "src/features/ray/rayAnalysis.ts",
    ROOT / "src/features/ray/RayPage.tsx",
]
RUST_TARGET = ROOT / "src-tauri/src/lib.rs"

def strip_one_leading_backslash(path: Path) -> None:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

    data = path.read_bytes()

    # Accept optional UTF-8 BOM, then remove exactly one stray leading backslash.
    bom = b"\xef\xbb\xbf"
    if data.startswith(bom):
        body = data[len(bom):]
        if body.startswith(b"\\"):
            body = body[1:]
            path.write_bytes(bom + body)
            print("REMOVED_LEADING_BACKSLASH_AFTER_BOM=" + str(path))
        else:
            print("NO_LEADING_BACKSLASH_AFTER_BOM=" + str(path))
    else:
        if data.startswith(b"\\"):
            path.write_bytes(data[1:])
            print("REMOVED_LEADING_BACKSLASH=" + str(path))
        else:
            print("NO_LEADING_BACKSLASH=" + str(path))

    fixed = path.read_bytes()
    logical = fixed[len(bom):] if fixed.startswith(bom) else fixed
    if logical.startswith(b"\\"):
        raise SystemExit("LEADING_BACKSLASH_SURVIVED=" + str(path))

    text = fixed.decode("utf-8-sig")
    if not text.lstrip().startswith("import "):
        raise SystemExit("EXPECTED_IMPORT_AT_START=" + str(path))

    print("SHA256=" + hashlib.sha256(fixed).hexdigest())

for target in TS_TARGETS:
    strip_one_leading_backslash(target)

if not RUST_TARGET.exists():
    raise SystemExit("MISSING=" + str(RUST_TARGET))

cargo = "cargo"
cmd = [
    cargo,
    "fmt",
    "--manifest-path",
    str(ROOT / "src-tauri/Cargo.toml"),
]
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

print("RUSTFMT_APPLIED=" + str(RUST_TARGET))
print("CAUSE_TS=RAW_TRIPLE_QUOTED_GENERATOR_PRESERVED_LEADING_BACKSLASH")
print("CAUSE_RUST=LIB_RS_NOT_RUSTFMT_NORMALIZED_BEFORE_VERIFY")
print("PATCH_SCOPE=RAY_TS_PREFIXES+RUSTFMT_ONLY")
print("RAY_LAYOUT_MUTATION=NO")
print("RAY_FILESYSTEM_LOGIC_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("RAY_PROJECT_SIGHT_000005H1_PATCH=PASS")

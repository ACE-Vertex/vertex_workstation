from pathlib import Path
import hashlib
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

TS_TARGETS = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/seedData.ts",
]

def strip_one_leading_backslash(path: Path) -> None:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

    data = path.read_bytes()
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
    if path.name == "ForgePage.tsx":
        if not text.lstrip().startswith("import "):
            raise SystemExit("FORGEPAGE_IMPORT_START_FAIL=" + str(path))
    elif path.name == "seedData.ts":
        if not text.lstrip().startswith("export "):
            raise SystemExit("SEEDDATA_EXPORT_START_FAIL=" + str(path))

    print("SHA256=" + hashlib.sha256(fixed).hexdigest())

for target in TS_TARGETS:
    strip_one_leading_backslash(target)

fmt = subprocess.run(
    [
        "cargo",
        "fmt",
        "--manifest-path",
        str(ROOT / "src-tauri/Cargo.toml"),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=cargo fmt --manifest-path " + str(ROOT / "src-tauri/Cargo.toml"))
if fmt.stdout:
    print(fmt.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if fmt.stderr:
    print(fmt.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if fmt.returncode:
    raise SystemExit(fmt.returncode)

print("CAUSE_TS=GENERATED_SOURCE_PRESERVED_STRAY_LEADING_BACKSLASH")
print("CAUSE_RUST=000007_LIB_RS_NOT_RUSTFMT_NORMALIZED_BEFORE_FOUNDATION_GATE")
print("PATCH_SCOPE=2_TS_PREFIXES+RUSTFMT_ONLY")
print("FORGE_FEATURE_LOGIC_MUTATION=NO")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_REAL_RECEIVING_000007H1_PATCH=PASS")

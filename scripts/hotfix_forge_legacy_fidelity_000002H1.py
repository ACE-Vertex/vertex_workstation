from pathlib import Path
import hashlib

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
TARGETS = [
    ROOT / "src/features/forge/ForgePage.tsx",
    ROOT / "src/features/forge/seedData.ts",
]

for p in TARGETS:
    if not p.exists():
        raise SystemExit("MISSING=" + str(p))

    data = p.read_bytes()

    # 000002H1 exact failure:
    # Both files were generated from Python raw triple-quoted strings with
    # an initial backslash that was preserved as a literal byte.
    # TypeScript then sees '\' at line 1 column 1 and emits TS1127.
    if data.startswith(b"\\"):
        data = data[1:]
        p.write_bytes(data)
        print("REMOVED_LEADING_BACKSLASH=" + str(p))
    elif data.startswith(b"\xef\xbb\xbf\\"):
        data = b"\xef\xbb\xbf" + data[4:]
        p.write_bytes(data)
        print("REMOVED_LEADING_BACKSLASH_AFTER_BOM=" + str(p))
    else:
        print("NO_LEADING_BACKSLASH=" + str(p))

    check = p.read_bytes()
    logical = check[3:] if check.startswith(b"\xef\xbb\xbf") else check

    if logical.startswith(b"\\"):
        raise SystemExit("LEADING_BACKSLASH_SURVIVED=" + str(p))

    text = check.decode("utf-8-sig")
    if not text.lstrip().startswith("import "):
        raise SystemExit("EXPECTED_IMPORT_NOT_AT_FILE_START=" + str(p))

    print("SHA256=" + hashlib.sha256(check).hexdigest())

print("CAUSE=RAW_TRIPLE_QUOTED_GENERATOR_PRESERVED_LEADING_BACKSLASH")
print("PATCH_SCOPE=ForgePage.tsx+seedData.ts_FIRST_BYTE_ONLY")
print("CSS_MUTATION=NO")
print("OWNERSHIP_CONTRACT_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_LEGACY_FIDELITY_000002H1_PATCH=PASS")

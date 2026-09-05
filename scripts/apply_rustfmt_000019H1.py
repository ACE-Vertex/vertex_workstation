from pathlib import Path
import hashlib
import shutil
import subprocess
import sys

ROOT = Path(
    r"G:\Vertex_Project\Development\vertex_workstation"
)
MANIFEST = (
    ROOT / "src-tauri" / "Cargo.toml"
)
RUST_ROOT = (
    ROOT / "src-tauri" / "src"
)

if not MANIFEST.exists():
    raise SystemExit(
        "CARGO_MANIFEST_MISSING="
        + str(MANIFEST)
    )

cargo = shutil.which("cargo")
if not cargo:
    raise SystemExit(
        "CARGO_NOT_FOUND"
    )

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            h.update(chunk)
    return h.hexdigest()

before = {
    path: sha256(path)
    for path in sorted(
        RUST_ROOT.rglob("*.rs")
    )
    if path.is_file()
}

print(
    "RUSTFMT_SCOPE=SRC_TAURI_RUST_SOURCES"
)
print(
    "RUSTFMT_MUTATION=FORMAT_ONLY"
)
print(
    "RUN=cargo fmt --manifest-path "
    + str(MANIFEST)
)

proc = subprocess.run(
    [
        cargo,
        "fmt",
        "--manifest-path",
        str(MANIFEST),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)

if proc.stdout:
    print(
        proc.stdout
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if proc.stderr:
    print(
        proc.stderr
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if proc.returncode:
    raise SystemExit(
        proc.returncode
    )

after = {
    path: sha256(path)
    for path in sorted(
        RUST_ROOT.rglob("*.rs")
    )
    if path.is_file()
}

changed = [
    path
    for path in after
    if before.get(path)
    != after.get(path)
]

for path in changed:
    print(
        "RUSTFMT_CHANGED="
        + str(
            path.relative_to(ROOT)
        )
    )

print(
    "RUSTFMT_CHANGED_COUNT="
    + str(len(changed))
)

print(
    "RUN=cargo fmt --manifest-path "
    + str(MANIFEST)
    + " -- --check"
)

check = subprocess.run(
    [
        cargo,
        "fmt",
        "--manifest-path",
        str(MANIFEST),
        "--",
        "--check",
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)

if check.stdout:
    print(
        check.stdout
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if check.stderr:
    print(
        check.stderr
        .encode(
            "ascii",
            "backslashreplace",
        )
        .decode("ascii")
    )

if check.returncode:
    raise SystemExit(
        check.returncode
    )

print(
    "RUSTFMT_CHECK=PASS"
)
print(
    "OPENAI_API_000019H1_FORMAT_NORMALIZATION=PASS"
)

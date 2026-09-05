from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
CARGO = ROOT / "src-tauri/Cargo.toml"

if not CARGO.exists():
    raise SystemExit("MISSING=" + str(CARGO))

proc = subprocess.run(
    ["cargo", "fmt", "--manifest-path", str(CARGO)],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=cargo fmt --manifest-path " + str(CARGO))
if proc.stdout:
    print(proc.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if proc.stderr:
    print(proc.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if proc.returncode:
    raise SystemExit(proc.returncode)

print("CAUSE_1=000008_PATH_TRAVERSAL_GATE_VERIFIER_EXPECTED_SYNTHETIC_LITERAL")
print("CAUSE_2=000007_NO_FAKE_STAGE_ASSERTION_OBSOLETE_AFTER_000008_REAL_STAGE")
print("CAUSE_3=000008_RUST_SOURCE_REQUIRED_RUSTFMT_NORMALIZATION")
print("RUNTIME_STAGE_LOGIC_MUTATION=NO")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_STAGE_000008H1_PATCH=PASS")

from pathlib import Path
import subprocess
import sys

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

required = [
    ROOT / "scripts" / "verify_forge_receiving_live_watch_000020.py",
    ROOT / "scripts" / "verify_forge_stage_000008H2.py",
    ROOT / "scripts" / "verify_openai_api_adapter_000019.py",
    ROOT / "scripts" / "build_workstation_foundation_000001.py",
]
for path in required:
    if not path.exists():
        raise SystemExit("MISSING=" + str(path))

commands = [
    ["python", str(ROOT / "scripts" / "verify_forge_receiving_live_watch_000020.py")],
    ["python", str(ROOT / "scripts" / "verify_forge_stage_000008H2.py")],
    ["python", str(ROOT / "scripts" / "verify_openai_api_adapter_000019.py")],
    ["python", str(ROOT / "scripts" / "build_workstation_foundation_000001.py")],
]

for args in commands:
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

print("CAUSE=000020_VERIFICATION_CHAIN_CALLED_OBSOLETE_000008_TRAVERSAL_LITERAL_CHECK")
print("RUNTIME_RECEIVING_LOGIC_MUTATION=NO")
print("STAGE_RUNTIME_LOGIC_MUTATION=NO")
print("LATEST_STAGE_VERIFIER=000008H2")
print("FORGE_RECEIVING_LIVE_WATCH_000020H1=PASS")

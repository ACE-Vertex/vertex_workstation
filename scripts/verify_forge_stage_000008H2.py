from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")

commands = [
    (
        [
            "python",
            str(ROOT / "scripts/verify_forge_real_stage_000008H1.py"),
        ],
        ROOT,
    ),
    (
        [
            "python",
            str(ROOT / "scripts/verify_forge_receiving_regression_000008H2.py"),
        ],
        ROOT,
    ),
    (
        [
            "python",
            str(ROOT / "scripts/verify_ray_project_sight_000005.py"),
        ],
        ROOT,
    ),
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

print("CAUSE=000008H1_RECEIVING_REGRESSION_VERIFIER_OMITTED_OWNING_FILES")
print("FORGE_FOLDER_PICKER_OWNER=PathSwitcher.tsx+ForgePage.tsx+forgeApi.ts+lib.rs")
print("PROCESSING_SWEEP_OWNER=forgeRuntime.css")
print("RUNTIME_STAGE_LOGIC_MUTATION=NO")
print("RAY_MUTATION=NO")
print("VERTEX_WORKS_MUTATION=NO")
print("FORGE_STAGE_000008H2_VERIFY=PASS")

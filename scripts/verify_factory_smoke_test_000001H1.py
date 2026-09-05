from pathlib import Path
import hashlib
import sys

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
MARKER = ROOT / "docs" / "factory_smoke_test" / "SMOKE_TEST_000001H1.txt"
EXPECTED_SHA256 = "6b7a167b2ba3ae2fccbc8510732f98064b10bac81844b3d264a8e28416388dd0"

checks = []

def check(name, ok, detail=""):
    print(f"{name}={'PASS' if ok else 'FAIL'}" + (f" {detail}" if detail else ""))
    checks.append(bool(ok))

check("MARKER_EXISTS", MARKER.is_file(), str(MARKER))

if MARKER.is_file():
    data = MARKER.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    check("MARKER_SHA256", actual == EXPECTED_SHA256, actual)
    text = data.decode("utf-8")
    check("HUMAN_APPLY_MARKER", "Authority: HUMAN_APPLY" in text)
    check("HARMLESS_MARKER_ONLY", "harmless marker only" in text)
else:
    check("MARKER_SHA256", False)
    check("HUMAN_APPLY_MARKER", False)
    check("HARMLESS_MARKER_ONLY", False)

if all(checks):
    print("FACTORY_SMOKE_TEST_000001H1=PASS")
    raise SystemExit(0)

print("FACTORY_SMOKE_TEST_000001H1=FAIL")
raise SystemExit(1)

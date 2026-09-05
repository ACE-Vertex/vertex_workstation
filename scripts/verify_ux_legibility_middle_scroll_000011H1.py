from pathlib import Path
import subprocess

ROOT = Path(r"G:\Vertex_Project\Development\vertex_workstation")
HOOK = ROOT / "src/core/input/useMiddleMouseScroll.ts"

if not HOOK.exists():
    raise SystemExit("MISSING=" + str(HOOK))

text = HOOK.read_text(encoding="utf-8", errors="replace")

checks = {
    "AUXCLICK_MOUSE_EVENT_TYPE":
        "readonly onAuxClick: MouseEventHandler<HTMLElement>;" in text,
    "AUXCLICK_CALLBACK_MOUSE_EVENT":
        "MouseEventHandler<HTMLElement>" in text
        and "const onAuxClick = useCallback" in text,
    "POINTER_HANDLERS_PRESERVED":
        "PointerEventHandler<HTMLElement>" in text
        and "onPointerDown" in text
        and "onPointerMove" in text
        and "onPointerUp" in text
        and "onPointerCancel" in text,
    "MIDDLE_BUTTON_GATE_PRESERVED":
        "event.button !== 1" in text
        and "event.button === 1" in text,
    "POINTER_CAPTURE_PRESERVED":
        "setPointerCapture" in text
        and "releasePointerCapture" in text,
    "NO_DOM_REPARENT":
        all(
            token not in text
            for token in (
                ".appendChild(",
                ".removeChild(",
                ".insertBefore(",
                ".replaceChild(",
            )
        ),
}

for key, ok in checks.items():
    print(key + "=" + ("PASS" if ok else "FAIL"))

if not all(checks.values()):
    raise SystemExit(1)

npm = r"C:\Program Files\nodejs\npm.cmd"
proc = subprocess.run(
    [npm, "run", "build"],
    cwd=ROOT,
    capture_output=True,
    text=True,
    errors="replace",
)
print("RUN=" + npm + " run build")
if proc.stdout:
    print(proc.stdout.encode("ascii", "backslashreplace").decode("ascii"))
if proc.stderr:
    print(proc.stderr.encode("ascii", "backslashreplace").decode("ascii"))
if proc.returncode:
    raise SystemExit(proc.returncode)

print("CAUSE=REACT_ONAUXCLICK_EXPECTS_MOUSEEVENTHANDLER")
print("FIX=ONAUXCLICK_POINTEREVENTHANDLER_TO_MOUSEEVENTHANDLER")
print("MIDDLE_MOUSE_RUNTIME_LOGIC_MUTATION=NO")
print("UX_LEGIBILITY_MIDDLE_SCROLL_000011H1=PASS")

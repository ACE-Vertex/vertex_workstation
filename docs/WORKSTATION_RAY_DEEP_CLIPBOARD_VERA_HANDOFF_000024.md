# Vertex Workstation — DEEP RAY Clipboard → Vera Handoff 000024

## User intent

Pressing DEEP RAY should immediately prepare the RAY result for Vera.

The human should only need to switch to Vera/ChatGPT and paste.

## Flow

`DEEP RAY click`
→ `mode=DEEP`
→ deterministic findings rebuilt for DEEP
→ `RAY / VERA HANDOFF CAPSULE`
→ `navigator.clipboard.writeText(...)`
→ `CLIP COPIED`
→ Human paste into Vera

No synthetic browser paste, DOM injection, or automatic chat submission is used.

This preserves the Human Relay boundary.

## Capsule contents

The clipboard capsule contains:

- schema / timestamp / DEEP mode
- read-only authority + mutation NONE
- project root and scan counts
- exact active file path and provenance
- target set
- source encoding / line count / truncation state
- import/use/mod facts with line + column
- symbol facts with line + column
- TODO/event/DOM/CSS clue lines
- Evidence / Findings with source line and confidence
- Vera truth-boundary instruction
- the loaded Source Snapshot itself

This means Vera can diagnose from the exact RAY-observed source rather than from
a detached summary.

## UI

DEEP RAY now clips automatically.

A separate `COPY RAY → VERA` button allows re-copying without re-running RAY.

Clip state is visible:
- READY
- CLIPPING...
- COPIED
- FAILED

CLIPPING has an explicit pulse animation.

## Runtime acceptance

1. Launch the immutable candidate.
2. Open RAY and select a source file.
3. Press DEEP RAY once.
4. `CLIP COPIED` must appear.
5. Paste into Vera/ChatGPT.
6. The pasted text must begin with:
   `=== VERTEX WORKSTATION — RAY / VERA HANDOFF CAPSULE ===`
7. It must contain the exact active path, line-aware facts/findings, and source snapshot.
8. Press `COPY RAY → VERA` and verify the capsule can be copied again.
9. Clipboard failure must surface as `CLIP FAILED` / RAY runtime error.
10. No automatic browser/chat paste or submission may occur.

Do not call clipboard Runtime GREEN until the actual paste is observed.

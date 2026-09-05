# Vertex Workstation — 000015H1

## Cause

Vertex Works rejected 000015 during **VALIDATE** before staging:

`verification program not allowed: cmd`

The runtime/bootstrap implementation itself was not executed.

## Fix

The VRA verification chain now uses only an allowed top-level verifier:

`python`

That Python verifier launches the existing PowerShell bootstrap as a child
process.

This follows the existing Works verification pattern where Python owns the
verification step and may invoke platform tools internally.

## Important consequence

Because 000015 failed before Stage and Apply, 000015H1 is **self-contained**.
It includes the entire 000015 payload plus this hotfix verifier.

No assumption is made that any 000015 file already exists on the target.

## Scope

No MCP protocol logic change.
No Relay schema/storage change.
No FORGE/RAY/UI change.
No legacy `vertex_works` mutation.

000015H1 remains NOT GREEN until Works completes validation, apply and the real
MCP runtime verification chain on the target machine.

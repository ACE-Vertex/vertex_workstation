# Vertex Workstation — FORGE Real Stage 000008H1

## Evidence diagnosis

000008 did not expose a Stage runtime-logic failure.

Three verification-layer issues stopped acceptance:

1. `PATH_TRAVERSAL_GATE=FAIL`
   - The runtime guard is generic:
     `safe_relative_path(destination, "STAGE_DESTINATION")`
     rejects `ParentDir`, `RootDir`, and `Prefix`.
   - The verifier incorrectly expected the synthetic contiguous literal
     `STAGE_DESTINATION_TRAVERSAL_BLOCKED`, which is constructed only at runtime.

2. `NO_FAKE_STAGE=FAIL`
   - This came from the historical 000007 verifier.
   - 000007 intentionally required Stage to remain disabled.
   - 000008 intentionally implements real Stage, so that historical assertion is
     obsolete and must not gate 000008.

3. `cargo fmt -- --check`
   - `src-tauri/src/lib.rs` required rustfmt normalization before the downstream
     RAY and foundation gates.

## H1 repair

- Run `cargo fmt`.
- Replace the 000008 traversal check with a check for the actual generic guard
  structure and the actual destination call.
- Add a receiving-side regression verifier that preserves all 000007 Receiving
  Bay / VRA inspection guarantees while explicitly accepting real Stage.
- Do not call the obsolete 000007 `NO_FAKE_STAGE` invariant as an 000008 gate.

## Runtime scope

No Stage runtime logic changed.
No target project mutation added.
No APPLY or ROLLBACK implementation added.
No RAY mutation.
No legacy `vertex_works` mutation.

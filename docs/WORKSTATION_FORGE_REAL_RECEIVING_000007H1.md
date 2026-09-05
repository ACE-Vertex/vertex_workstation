# Vertex Workstation — FORGE Real Receiving Bay 000007H1

## Exact failure

000007 feature-contract checks all passed before the build gate.

The actual failures were:

1. `src/features/forge/ForgePage.tsx(1,1): TS1127 Invalid character`
2. `src/features/forge/seedData.ts(1,1): TS1127 Invalid character`
3. `cargo fmt -- --check` reported formatting-only diffs in `src-tauri/src/lib.rs`

The two TypeScript files contain the same stray leading backslash-byte pattern
already seen in earlier generated payloads.

The Rust failure is formatting-only; the evidence does not show a Rust semantic
or compile error at this point.

## H1 repair

- Remove exactly one stray leading backslash from `ForgePage.tsx`
- Remove exactly one stray leading backslash from `seedData.ts`
- Run `cargo fmt` on the Workstation Tauri crate
- Re-run:
  - frontend build
  - rustfmt check
  - cargo check
  - original 000007 verifier
  - RAY preservation verifier
  - production Tauri builder

## Scope

No FORGE Receiving Bay logic change.
No VRA manifest inspection change.
No Authorized Production Root gate change.
No RAY change.
No legacy `vertex_works` mutation.

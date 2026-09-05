# Vertex Workstation — FORGE Stage Verification Scope Hotfix 000008H2

## Exact H1 outcome

The real Stage verifier passed completely:

- Stage API / command
- SHA256 payload gate
- payload source gate
- traversal gate
- Authorized Production Root re-check
- HUMAN_APPLY re-check
- immutable stage identity
- stage report / STAGE_LOCK / artifact snapshot
- backup plan
- target mutation = NO
- APPLY / ROLLBACK still disabled
- TypeScript/Vite build
- rustfmt
- cargo check

RAY regression and the production Tauri build also passed.

The only failing command was the new Receiving Bay regression verifier.

## Root cause

The H1 Receiving Bay verifier built its searchable source text from:

- ForgePage.tsx
- IncomingCargo.tsx
- ArtifactInspector.tsx
- forgeApi.ts
- lib.rs

but then attempted to prove two features owned by files it never loaded:

1. `FORGE_FOLDER_PICKER`
   - visual BROWSE control owner: `PathSwitcher.tsx`

2. `PROCESSING_SWEEP`
   - animation owner: `forgeRuntime.css`

The verifier therefore produced two false negatives even though the runtime
feature owners still exist.

## H2 repair

The regression verifier now follows ownership explicitly:

- folder picker proof:
  `PathSwitcher.tsx + ForgePage.tsx + forgeApi.ts + lib.rs`
- processing sweep proof:
  `forgeRuntime.css`

No runtime implementation is changed.

## Scope

No Stage logic change.
No Receiving Bay logic change.
No APPLY / ROLLBACK implementation.
No RAY mutation.
No legacy `vertex_works` mutation.

After H2 verification, the existing Tauri production builder is run again to
produce a fresh immutable candidate.

Runtime Stage acceptance is still required.

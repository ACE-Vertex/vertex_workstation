# Vertex Workstation — FORGE Real APPLY / ROLLBACK 000022H3

## Evidence diagnosis

000022H2 successfully passed:

- H2 scope checks
- complete 000022 APPLY / ROLLBACK static verifier
- frontend TypeScript/Vite build
- cargo check
- 000020 Receiving Bay live-watch regression
- 000021 Incoming Cargo history-color regression
- OpenAI adapter regression

The only remaining failure occurred inside the immutable production build gate:

`cargo fmt --manifest-path ... -- --check`

`src-tauri/src/forge_apply.rs` was semantically valid and compiled, but was not
fully rustfmt-normalized after the H1 source edit that removed the unused Write
import.

## H3

This is formatting-only.

1. Run target-side `cargo fmt` using the project's actual Rust toolchain.
2. Print forge_apply.rs SHA256 before/after.
3. Run `cargo fmt -- --check`.
4. Rerun the complete 000022H2 verifier chain.

No APPLY, ROLLBACK, Stage, Receiving, Relay, provider, or UI behavior changes.

Runtime acceptance still remains after a successful immutable build:
STAGE -> STAGED -> APPLY armed -> APPLYING -> APPLIED -> ROLLBACK armed.

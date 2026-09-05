# Vertex Workstation — OpenAI API Adapter 000019H1

## Evidence diagnosis

000019 itself passed its OpenAI API verifier and Rust unit tests.

The only failing verification was the production foundation builder at:

`cargo fmt --manifest-path .../src-tauri/Cargo.toml -- --check`

The evidence showed rustfmt diffs in `src-tauri/src/lib.rs`.

This is a formatting normalization failure, not an OpenAI API transport,
Adapter Port, MCP, Human Gate, or unit-test failure.

## H1 action

The H1 verifier performs one explicit semantic-preserving Rust formatting pass:

`cargo fmt --manifest-path <Cargo.toml>`

It then immediately runs:

`cargo fmt --manifest-path <Cargo.toml> -- --check`

and reports every `.rs` file whose SHA256 changed.

After formatting is normalized, the original 000019 verifier and all
regression verifiers run again, followed by the normal Tauri production build.

## Scope

- Rust formatting only.
- No API credential.
- No OpenAI request is sent.
- No Adapter behavior change.
- No MCP behavior change.
- No UI redesign.
- No floating window.
- No FORGE/RAY behavior mutation.

This hotfix is intentionally small because the functional 000019 checks were
already GREEN before the rustfmt gate.

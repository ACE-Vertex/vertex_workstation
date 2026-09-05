# Vertex Workstation — Foundation 000001H3

## Runtime failure

Build `20260904-215828` launched a valid Tauri window, but the WebView attempted:

`http://127.0.0.1:1420`

and returned `ERR_CONNECTION_REFUSED`.

The window title and native shell were therefore working, but the candidate was
still behaving like a development build.

## Root cause

The previous build pipeline did:

1. `npm run build`
2. `cargo build --release`

That compiles Rust in release mode, but it bypasses the Tauri CLI build
orchestration that owns the `devUrl` vs `frontendDist` production switch.

For a desktop production candidate, raw Cargo release build is not the correct
top-level build owner.

## H3 fix

Production candidate build is now:

`npm run tauri:build`

which invokes `tauri build`.

Tauri CLI:
- runs the configured `beforeBuildCommand`
- builds the Vite frontend
- uses `frontendDist`
- compiles the Tauri release application in production mode

`devUrl` remains available only for `tauri dev`.

## Hard rule introduced

Development:
`npm run tauri:dev` -> `devUrl`

Production candidate:
`npm run tauri:build` -> `frontendDist`

Do not build Workstation production candidates with raw
`cargo build --release`.

No React architecture, CSS, Component Registry, Ownership Contract,
Presentation Port or Layout Grid changes are made by H3.

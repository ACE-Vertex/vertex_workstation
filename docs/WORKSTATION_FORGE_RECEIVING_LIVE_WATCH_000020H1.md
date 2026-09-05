# Vertex Workstation — FORGE Receiving Live Watch 000020H1

## Evidence diagnosis

000020 runtime implementation itself passed its dedicated verifier:

- lightweight fingerprint API/Rust path
- real filesystem source
- real rescan on change
- hidden-window guard
- single-flight watch
- manual refresh preserved
- Stage preserved
- no float / no DOM injection
- TypeScript/Vite build
- cargo check

The overall Works VERIFY failed only because 000020 called the obsolete
`scripts/verify_forge_real_stage_000008.py`.

That historical verifier expects the synthetic contiguous source literal
`STAGE_DESTINATION_TRAVERSAL_BLOCKED`.

The actual Stage guard is generic by design:
`safe_relative_path(destination, "STAGE_DESTINATION")`
plus rejection of `ParentDir`, `RootDir`, and `Prefix`, and constructs
`<LABEL>_TRAVERSAL_BLOCKED` only at runtime.

This exact verifier false-negative was already retired by 000008H1/H2.

## H1 repair

No FORGE runtime code is changed.

The verification chain is corrected to use the latest Stage verification owner:
`verify_forge_stage_000008H2.py`.

Then 000020, OpenAI adapter, and production Tauri build gates are rerun.

## Truth boundary

This hotfix can make STATIC / BUILD / REGRESSION GREEN only.

Receiving Bay live-watch Runtime GREEN still requires visual acceptance:
drop/remove a `.vra` while FORGE is open and confirm Incoming Cargo updates
without pressing REFRESH.

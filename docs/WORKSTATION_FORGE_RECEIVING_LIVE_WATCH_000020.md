# Vertex Workstation — FORGE Receiving Bay Live Watch 000020

Purpose: restore the missing "look at the Receiving Bay" behavior without turning the factory into a constant heavy manifest scanner.

Observed cause:
- FORGE frontend already had a real `forge_scan_receiving_bay` path.
- `ForgePage` intentionally performed only an initial scan plus explicit REFRESH/commit scans.
- Therefore a VRA dropped into `_incoming` after the initial scan was not automatically surfaced until a manual refresh.

Implementation:
- Add a lightweight Rust metadata fingerprint command for the Receiving Bay.
- Poll only that fingerprint while the Workstation window is visible and FORGE is READY.
- Do not open/parse every VRA on every tick.
- When the fingerprint changes, run the existing real Receiving Bay scan and normal manifest inspection.
- Keep the existing manual REFRESH, Stage, RAY, OpenAI adapter, and Human Gate behavior.
- No floating UI, no browser DOM injection, no target mutation from the watcher.

Runtime acceptance:
1. Launch the immutable build produced by verification.
2. Keep FORGE open.
3. Drop one new `.vra` into `G:\Vertex_Project\Development\_incoming`.
4. Without pressing REFRESH, Incoming Cargo should update within roughly 1.5–3 seconds.
5. Works Ledger should show `RECEIVING WATCH CHANGE DETECTED — rescanning`.
6. Remove the test VRA; the list/count should update again without pressing REFRESH.

Do not call runtime GREEN until this behavior is observed.

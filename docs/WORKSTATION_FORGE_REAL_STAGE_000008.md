# Vertex Workstation — FORGE Real Stage 000008

## Mission

Close the next major FORGE gap:

`Inspect → Stage`

without mutating the target project.

## Real Stage contract

A READY VRA can now be staged only after Rust independently re-checks:

- VRA extension and readability
- manifest validity
- `vra/1`
- `HUMAN_APPLY`
- target root inside Authorized Production Root
- supported operation type (`copy`)
- source path remains under `payload/`
- source/destination path traversal is blocked
- each payload SHA256 matches the manifest
- per-file and total payload bounds

## Immutable stage

Successful stages are written under:

`%LOCALAPPDATA%\VertexWorkstation\staging\<artifact-id>-<timestamp>`

Each stage contains:

- `artifact.vra` — immutable source snapshot
- `manifest.json` — manifest snapshot
- `files/...` — hash-verified staged payload
- `stage_report.json` — structured stage evidence
- `STAGE_LOCK` — stage identity / target / authority proof

A stage ID is never reused.

If staging fails, the partial stage directory is removed.

## Backup plan

Stage calculates whether each destination already exists and records a planned
backup root under:

`%LOCALAPPDATA%\VertexWorkstation\backups\<stage-id>`

No backup or target mutation occurs yet.

## UI truth

The FORGE Inspector now has a real STAGE button.

After success it shows:

- stage id
- artifact SHA256
- payload hash verification count
- staged destinations
- NEW FILE vs BACKUP PLANNED
- staging root
- target root
- backup plan root

`APPLY / FORGE` and `ROLLBACK` remain disabled.

## Processing visibility

During staging the fixed FORGE State Board shows:

`HASH VERIFY + IMMUTABLE STAGING...`

with the existing orange sweep animation.

No floating window is introduced.

## Next pass

000009 should implement:

`Stage → HUMAN APPLY → Backup → Atomic-ish Copy → Verification`

with rollback material generated before the first target mutation.

No legacy `vertex_works` mutation.

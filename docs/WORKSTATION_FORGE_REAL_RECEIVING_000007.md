# Vertex Workstation — FORGE Real Receiving Bay + VRA Manifest Inspector 000007

## Mission

Begin closing the remaining Workstation implementation gaps without jumping
straight into destructive APPLY / ROLLBACK logic.

000007 converts the FORGE read-side from seed/demo data to real filesystem and
real `.vra` inspection.

## Real capabilities

FORGE now:

- scans the selected Receiving Bay
- shows actual `.vra` files
- opens each VRA ZIP and reads root `manifest.json`
- validates `vra/1`
- validates `HUMAN_APPLY`
- validates target project root against Authorized Production Root
- counts copy operations and verification commands
- previews operation destinations
- reports manifest errors as ATTENTION
- supports real REFRESH
- supports folder BROWSE for Receiving Bay and Authorized Production Root
- copies inspection summary to clipboard

## Truthful controls

STAGE / APPLY / ROLLBACK remain visibly present because they are part of the
FORGE workflow, but are disabled and labelled as the next implementation pass.

No fake “staged” or “verified” state is emitted.

## Processing visibility

Receiving Bay scan drives the existing bottom state board with an orange sweep
animation so processing remains visually obvious without introducing a float.

## Path presentation

Windows canonical `\\?\` prefixes are stripped for display only. Filesystem
guards continue using canonical paths internally.

## Next gap

000008 should implement:

`Inspect → Stage`

with immutable staging directory, payload hash verification, target-root gate,
backup plan generation, and HUMAN_APPLY gate.

Only after Stage is GREEN should APPLY / FORGE be wired.

No legacy `vertex_works` mutation.

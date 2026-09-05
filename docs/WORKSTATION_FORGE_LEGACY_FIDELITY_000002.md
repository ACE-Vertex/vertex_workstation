# Vertex Workstation — FORGE Legacy Fidelity 000002

## Visual target

Rebuild the new Workstation FORGE page as close as practical to the last
well-liked Vertex Works FORGE layout, while preserving the new React /
TypeScript architecture.

Primary retained panels:

- Incoming Cargo
- Artifact Inspector
- Vertex Shell
- Works Ledger

Retained visual characteristics:

- deep black / blue-black surfaces
- orange engineering accents
- dense information layout
- Receiving / Inspector upper pair
- Shell / Ledger lower pair
- status cards above
- state-board footer

## Required new behavior

`RECEIVING BAY` is not a fixed string. It is an editable / switchable path field.

`AUTHORIZED PRODUCTION ROOT` is also editable / switchable.

Both use React state and do not own runtime services yet.

## Architectural boundary

This artifact does not copy legacy DOM ownership.

The old look is reproduced as React components:

- `ForgePage`
- `IncomingCargo`
- `ArtifactInspector`
- `ConsolePanel`
- `ForgeStatusCards`
- `PathSwitcher`

Cargo selection drives Inspector state through React state.

No imperative DOM re-parenting is introduced.

## Scope

This is a FORGE layout / interaction foundation.

Actual filesystem Receiving Bay service,
production-root authorization service,
VRA apply/rollback runtime wiring,
real Shell stream and real Ledger stream are deferred to later passes.

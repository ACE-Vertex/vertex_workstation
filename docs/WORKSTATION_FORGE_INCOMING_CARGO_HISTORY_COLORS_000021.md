# Vertex Workstation — FORGE Incoming Cargo History Colors 000021

## Restored intended distinction

Incoming Cargo must not paint every valid item green.

The card border has four meanings:

- RED — current VRA is unusable / cannot enter Stage (`ATTENTION`)
- NEUTRAL — current VRA is valid but has never been staged
- ORANGE — this exact VRA payload has produced a Stage error and has never later passed
- GREEN — this exact VRA payload has successfully passed immutable Stage/hash verification at least once

## Important ownership rule

Current validity and execution history are separate dimensions.

`status = READY | ATTENTION`
describes the VRA *now*.

`stageHistory = NONE | ERROR | VERIFIED`
describes historical Stage evidence for the exact artifact SHA256.

The UI only renders those facts.

## Persistence

Stage history is owned by Rust and persisted append-only at:

`%LOCALAPPDATA%\VertexWorkstation\forge_history\events.jsonl`

No history is stored in React state, localStorage, the VRA itself, or the production project.

Existing successful immutable Stage snapshots are backfilled from:

`%LOCALAPPDATA%\VertexWorkstation\staging\*\stage_report.json`

Historical Stage failures that occurred before 000021 cannot be reconstructed if no durable evidence remains; errors are persisted from 000021 onward.

## Precedence

Current unusable state is always RED.

For a currently valid exact artifact SHA:
- any successful Stage => GREEN
- otherwise any recorded Stage error => ORANGE
- otherwise => NEUTRAL

Thus a VRA that failed once and later passed resolves to GREEN.

## Runtime acceptance

Open FORGE and verify four representative artifacts:
1. invalid VRA => red
2. valid VRA never staged => neutral border
3. valid VRA that fails Stage => orange immediately and after restart
4. valid VRA that passes Stage => green immediately and after restart

Selecting a card must not overwrite its lifecycle/history border color.

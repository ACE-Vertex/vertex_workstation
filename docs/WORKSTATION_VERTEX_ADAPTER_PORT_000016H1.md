# Vertex Workstation — 000016H1

## Cause

000016 applied successfully, but the TypeScript build failed in:

`src/shell/relay/VertexRelayBar.tsx`

at the adapter selector cast.

The generated JSX split the TypeScript `as` assertion across lines as:

`event.target.value`
`  as VertexAdapterId`

The target TypeScript/TSX parser rejected that form with:

`TS1005: ',' expected`

## Fix

Keep the assertion as one TypeScript expression:

`event.target.value as VertexAdapterId`

No Adapter Port architecture changes.
No Relay transport changes.
No MCP changes.
No credential handling changes.
No FORGE/RAY changes.
No UI redesign.

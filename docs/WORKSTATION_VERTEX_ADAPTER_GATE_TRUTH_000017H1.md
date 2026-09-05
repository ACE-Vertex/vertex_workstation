# Vertex Workstation — 000017H1

## Evidence diagnosis

000017 source/build remained healthy, but verification reported three failures:

- `UI_DOES_NOT_OWN_PROVIDER_GATE=FAIL`
- `CONTRACT_ROUTE_TRUTH=FAIL`
- legacy `000016 NO_FAKE_PROVIDER_SEND=FAIL`

The production build itself passed.

## Exact causes

### 1. UI ownership verifier false positive

`VertexRelayBar` still reads:

`activeAdapter?.state === "READY"`

for visual styling/status display.

That is presentation, not route ownership.

The actual SEND decision already calls:

`evaluateVertexAdapterRoute(...)`

and does not branch directly on provider-specific
`EXTERNAL_GATE` / `UNCONFIGURED` values.

The verifier was therefore too broad.

### 2. Contract rule was not actually inserted

The new source ownership is correct, but the intended Architecture Contract
sentence:

`Presentation must ask Adapter Port for route truth...`

was absent from `contracts.ts`.

H1 adds it for real.

### 3. 000016 verifier became historical

000016 originally guarded fake delivery by looking for:

`ADAPTER_EXTERNAL_GATE`

000017 intentionally replaced that transport guard with the stronger:

`evaluateVertexAdapterRoute`
+
`ADAPTER_ROUTE_BLOCKED`

The old verifier is updated to recognize either the historical guard or the
000017 evolved route guard.

## Scope

- one Architecture Contract rule
- verifier precision / lifecycle evolution

No Adapter runtime logic change.
No MCP protocol change.
No Relay schema change.
No UI redesign.
No credentials.
No FORGE/RAY mutation.

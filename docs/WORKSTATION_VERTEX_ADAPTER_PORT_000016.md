# Vertex Workstation — Vertex Adapter Port 000016

## Mission

Stop treating an external provider gate as a reason for Vertex Core to stop.

The new rule is:

`External gate != Core failure`

`External gate = Adapter state`

## Architecture

`Vertex Relay / Workstation Core`
`-> Vertex Adapter Port`
`-> Adapter Registry`
`-> selected adapter`

Initial registry:

- `VERTEX_RELAY_HTTP` — real active outbound adapter
- `CHATGPT_MCP` — explicit `EXTERNAL_GATE`
- `OPENAI_API` — `UNCONFIGURED`
- `LOCAL_LLM` — `UNCONFIGURED`
- `HYPER_AGENT` — `UNCONFIGURED`

Only the HTTP adapter has a real send implementation in this pass.

The other entries are explicit architectural slots and must not pretend to be
connected.

## Why

Previously, provider-specific restrictions could leave an unfinished connector
and stall the surrounding architecture.

Now the stable ownership boundary is the Adapter Port.

A provider can be blocked, replaced, upgraded, or removed without moving
Relay/Core ownership.

## UI

The existing docked Vertex Relay bar gains a compact adapter selector.

No persistent floating window is added.

The active adapter state is visible as:

- `READY`
- `LINK_REQUIRED`
- `EXTERNAL_GATE`
- `UNCONFIGURED`

Selecting a blocked/unconfigured adapter does not fake delivery.

## Security

No provider credential is introduced in 000016.

No API key, password, bearer token, browser DOM injection, or synthetic paste.

## Verification evolution

The old 000012 verifier owned a historical invariant that the Relay Bar called
`sendVertexRelayDirect` directly.

000016 intentionally changes that ownership:

`Relay Bar -> Adapter Port -> Direct HTTP Adapter -> directRelayTransport`

Therefore the 000012 direct-call invariant is retired and replaced by the
000016 adapter-boundary verifier.

The real HTTP POST transport remains verified.

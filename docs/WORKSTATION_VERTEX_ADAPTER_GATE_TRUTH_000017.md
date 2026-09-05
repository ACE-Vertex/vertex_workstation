# Vertex Workstation — Adapter Gate Truth 000017

## Mission

Move provider-gate truth out of Presentation and into the Vertex Adapter Port.

The accepted 000016H1 UI already showed the correct states visually.
000017 makes that truth architectural rather than merely presentational.

## New invariant

`Presentation does not decide whether a provider route is available.`

Instead:

`Relay Bar -> evaluateVertexAdapterRoute() -> Adapter Port`

The Adapter Port returns one of:

- READY
- LINK_REQUIRED
- EXTERNAL_GATE
- UNCONFIGURED

The same route evaluation is enforced again inside the send path.

## Why this matters

A provider must never appear connected because the UI forgot a condition.

For ChatGPT MCP:

`CHATGPT_MCP -> EXTERNAL_GATE`

until an actual supported ChatGPT MCP app connection exists.

Pressing SEND cannot perform a fake delivery.

For Vertex Relay HTTP:

`VERTEX_RELAY_HTTP -> LINK_REQUIRED`

until a real endpoint is configured, then it becomes sendable through the
existing real HTTP POST transport.

## OpenAI external gate

The current OpenAI product boundary is outside this VRA.

OpenAI currently documents that ChatGPT does not connect directly to a local
MCP server. A private/on-prem/developer-machine MCP server requires Secure MCP
Tunnel or a supported remote MCP endpoint.

000017 does not invent tunnel commands, product entitlement, credentials, or a
ChatGPT connection.

It prepares the Vertex side so the external gate can later change without
rewriting Core or Presentation ownership.

## Scope

- Adapter route ownership
- Relay Bar gate delegation
- invariant verifier

No MCP protocol mutation.
No credentials.
No browser DOM injection.
No floating windows.
No FORGE/RAY mutation.

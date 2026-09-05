# Vertex Workstation — MCP Tool Capability Annotations 000018

## Mission

Prepare the Vertex Relay MCP tool surface for a real ChatGPT custom-app
connection without pretending the OpenAI external gate is open.

The local MCP runtime is already real and verified.

000018 adds explicit MCP ToolAnnotations so a compatible MCP host can
distinguish read-only Relay inspection from write-capable Relay mutations.

## Tool policy

Read-only / closed-world:

- `vertex_relay_status`
- `vertex_relay_latest`
- `vertex_relay_pending`
- `vertex_relay_get`
- `vertex_relay_latest_reply`

These advertise:

- `readOnlyHint = true`
- `openWorldHint = false`

Write-capable / additive / closed-world:

- `vertex_relay_acknowledge`
  - non-destructive
  - idempotent
- `vertex_relay_reply`
  - non-destructive
  - non-idempotent

## Why this matters

OpenAI currently distinguishes read/fetch MCP access from full write/modify
MCP access depending on product entitlement.

Vertex must not hard-code a user's ChatGPT plan into Core.

Instead the MCP server should accurately describe what each tool does.

That lets an authorized host expose only the tools it is allowed to use.

## Safety boundary

MCP ToolAnnotations are hints, not a security boundary.

They do not replace:

- Vertex Adapter Port route gating
- Human Gate
- server-side validation
- authorization
- provider permissions

000018 verifies the annotations through a real MCP `list_tools()` protocol
session, not only through source inspection.

## External gate

ChatGPT custom-app connectivity remains external and is not claimed by this
pass.

No Secure MCP Tunnel command is invented.
No ChatGPT plan is assumed.
No provider credential is embedded.

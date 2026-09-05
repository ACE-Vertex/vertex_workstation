# Vertex Workstation — MCP Runtime Bootstrap 000015

## Status entering this pass

000014H1 proved the static ChatGPT/MCP boundary:

- Streamable HTTP MCP server source
- `/mcp`
- `/vertex-relay`
- SQLite state owner
- pending / get / acknowledge / reply tools
- no fake current-chat push

The remaining local gate is the actual MCP Python runtime.

## 000015 mission

Create and verify the isolated MCP runtime for real protocol execution.

Run:

`VERTEX_RELAY_MCP_RUNTIME_VERIFY.cmd`

The bootstrap:

1. calls `VERTEX_RELAY_MCP_SETUP.cmd`
2. creates/updates the isolated venv under LOCALAPPDATA
3. installs the pinned MCP v1 dependency there
4. launches the real MCP server verifier
5. initializes an MCP client session
6. lists tools
7. calls `vertex_relay_status`

No global Python package install is used.

## Important network-path correction

The earlier assumption that the next step must be a public HTTPS deployment is
too narrow.

Current OpenAI product guidance states that local/private/on-prem MCP servers
cannot be connected to ChatGPT directly, but supported OpenAI products can use
**Secure MCP Tunnel** so the local MCP server does not need to be exposed to
the public internet.

Therefore the preferred summit path becomes:

`Workstation`
`-> Local Vertex Relay MCP`
`-> Secure MCP Tunnel`
`-> ChatGPT custom app / MCP`
`-> Vera tool call`

A remote public HTTPS MCP deployment remains an alternative, not the only path.

## Truth boundary

000015 can prove the local MCP protocol runtime.

It cannot prove the ChatGPT-side app connection by itself.

The external gates after 000015 are:

- account/workspace developer-mode eligibility
- Secure MCP Tunnel or supported remote MCP connection
- ChatGPT app registration/selection
- ChatGPT actually invoking the Vertex Relay MCP tool in a conversation turn

No browser text-box injection is required.

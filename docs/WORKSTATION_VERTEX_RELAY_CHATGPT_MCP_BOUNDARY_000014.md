# Vertex Workstation — ChatGPT MCP App Boundary 000014

## Summit mission

Create the official protocol boundary that can let ChatGPT use Vertex Relay
without browser DOM injection or clipboard paste.

The target architecture is:

`Vertex Workstation SEND`
`-> HTTPS /vertex-relay`
`-> Vertex Relay MCP Gateway`
`-> ChatGPT App / MCP tool call`
`-> Vera reads the Relay`

and the reverse path:

`Vera`
`-> vertex_relay_reply`
`-> Relay reply queue`
`-> Vertex Workstation RECEIVE`

## What 000014 builds

A single logical gateway with two surfaces:

### Ingest surface

`POST /vertex-relay`

Accepts `vertex-relay/1`.

This is compatible with the Workstation Direct SEND transport from 000012.

For localhost development, ingest may run without a token.

For any internet-facing deployment, set:

`VERTEX_RELAY_INGEST_TOKEN`

and configure the sender/reverse proxy accordingly.

### MCP surface

`/mcp`

Streamable HTTP MCP server.

Tools:

- `vertex_relay_status`
- `vertex_relay_latest`
- `vertex_relay_pending`
- `vertex_relay_get`
- `vertex_relay_acknowledge`
- `vertex_relay_reply`
- `vertex_relay_latest_reply`

## Storage

SQLite, WAL mode.

Default:

`%LOCALAPPDATA%\VertexWorkstation\relay_mcp\vertex_relay.db`

The database gives the MCP side and ingest side one deterministic state owner.

## Runtime isolation

MCP Python dependencies are not installed into the OS Python.

Run:

`VERTEX_RELAY_MCP_SETUP.cmd`

This creates an isolated runtime under:

`%LOCALAPPDATA%\VertexWorkstation\runtimes\relay_mcp_v1`

Then start local development server:

`VERTEX_RELAY_MCP.cmd`

Local endpoints:

- MCP: `http://127.0.0.1:8000/mcp`
- Ingest: `http://127.0.0.1:8000/vertex-relay`
- Health: `http://127.0.0.1:8000/health`

## The remaining gate

ChatGPT cloud cannot reach `127.0.0.1`.

Therefore the summit requires either OpenAI Secure MCP Tunnel for the local/private MCP server, or a supported remote HTTPS MCP deployment, plus a supported ChatGPT App / MCP connection.

000014 deliberately does not claim that a Relay can push itself into the
currently open ChatGPT conversation.

MCP is a tool boundary: ChatGPT must invoke the connected MCP tool during a
conversation turn.

That distinction is intentional.

## ChatGPT product boundary

OpenAI's current Apps SDK is based on MCP and supports apps that run in
ChatGPT conversations.

Private custom MCP Developer Mode is currently documented for Business and
Enterprise/Edu workspaces.

A published ChatGPT app is a separate distribution path.

Therefore there are two deployment tracks:

1. Internal/private MCP app in an eligible managed workspace.
2. Public/published ChatGPT app using the Apps SDK/plugin distribution path.

## Security boundary

000014 is not a production-public auth implementation.

Before exposing `/mcp` on the internet:

- use HTTPS
- put the MCP endpoint behind supported OAuth/auth
- keep ingest separately authenticated
- do not put tokens in URLs
- use least privilege
- preserve Human Gate for write actions

The local server is for protocol/runtime development only.

## Truth table

`Workstation -> local Bridge` = already proven by 000013 verifier.

`Workstation -> local MCP Gateway ingest` = core implemented in 000014.

`ChatGPT -> MCP Gateway tools` = runtime test after isolated MCP setup.

`Secure MCP Tunnel or remote HTTPS -> ChatGPT custom app` = next external deployment gate.

`Workstation push -> current ChatGPT text box` = not supported/claimed.

## Why this is the summit route

This stops fighting the browser input box.

Instead of trying to inject text into ChatGPT, Vertex becomes an official
tool/data source that ChatGPT can call through MCP.

That is the clean architectural door.

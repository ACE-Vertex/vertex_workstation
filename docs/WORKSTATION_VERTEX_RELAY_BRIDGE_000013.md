# Vertex Workstation — Vertex Relay Bridge 000013

## Mission

Create the first real local Relay Bridge behind Workstation `SEND`.

This pass establishes:

`Workstation SEND -> Local Relay Bridge`

It does **not** claim:

`Local Relay Bridge -> Vera`

until a real Vera-facing adapter exists.

## Endpoint

Default:

`http://127.0.0.1:47821/vertex-relay`

Health:

`http://127.0.0.1:47821/health`

Latest receipt:

`http://127.0.0.1:47821/vertex-relay/latest`

The bridge binds loopback only in this foundation pass.

## Start

From the Workstation project root:

`VERTEX_RELAY_BRIDGE.cmd`

Optional PowerShell parameters are forwarded to the launcher.

Example alternate port:

`VERTEX_RELAY_BRIDGE.cmd -Port 47831`

## Storage

Default root:

`%LOCALAPPDATA%\VertexWorkstation\relay_bridge`

Subdirectories:

- `inbox`
- `outbox`
- `meta`

Every accepted Relay is stored as an immutable JSON receipt under a dated inbox directory.

`meta/latest.json` tracks the latest accepted Relay.

## Validation

Accepted Relay must satisfy:

- schema = `vertex-relay/1`
- known type
- known action
- known source
- known target
- subject.id
- subject.name
- timestamp
- payload field present

Maximum body size:

2 MiB

## Browser / Tauri compatibility

The bridge provides CORS and OPTIONS support so the Tauri WebView can call the local HTTP endpoint through the existing Direct SEND transport.

## Truth boundary

On success the Bridge returns HTTP 202:

`RECEIVED`

and explicitly reports:

`VERA_ADAPTER_NOT_CONNECTED`

Therefore 000013 proves only:

`Workstation -> Relay Bridge`

The next pass is the Vera-facing adapter / authenticated transport.

## Security foundation

- loopback only
- no auth token storage
- no browser DOM injection
- no synthetic paste
- no public network bind
- no auto-forward to external services

## Verification

The verifier launches the actual bridge on an ephemeral loopback port and proves:

- health 200
- real Relay POST 202
- on-disk inbox persistence
- latest metadata
- invalid schema rejection

No FORGE / RAY source mutation.
No legacy `vertex_works` mutation.

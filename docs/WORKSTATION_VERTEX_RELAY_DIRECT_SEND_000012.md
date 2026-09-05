# Vertex Workstation — Vertex Relay Direct Send 000012

## Mission

Move Vertex Relay beyond manual clipboard paste without pretending that
Workstation can inject text into the ChatGPT browser DOM.

## Transport model

### COPY RELAY

Human/manual fallback.

- serializes `vertex-relay/1`
- writes to clipboard
- remains available permanently

### SEND

Real direct transport foundation.

- HTTP POST
- content type:
  `application/vnd.vertex-relay+json`
- 10 second timeout
- sends the exact `vertex-relay/1` envelope
- endpoint is configurable inside the docked Relay lane
- no automatic clipboard fallback if direct transport is unavailable

If no direct endpoint is configured:

`SEND -> LINK REQUIRED`

The endpoint editor then appears inline inside the Relay lane.

### Relay Bridge

The configured endpoint is expected to be a local or remote Relay Bridge,
for example one owned later by Hyper Agent or Vertex Core.

Example shape:

`http://127.0.0.1:<port>/vertex-relay`

This pass does not invent a Hyper Agent port or API credential.

No password, API token, or Authorization value is stored by Workstation.
Authentication remains the responsibility of the Relay Bridge layer.

## Browser boundary

000012 deliberately does NOT:

- inject into the ChatGPT text box
- synthesize mouse paste into another application
- automate external browser DOM
- claim current ChatGPT conversation delivery without a bridge

That boundary remains external to Workstation.

## UI

The Relay lane stays docked and compact.

Visible primary operations:

- COPY RELAY
- SEND
- RECEIVE

Status:

- DIRECT OFFLINE
- DIRECT LINKED
- LINK REQUIRED
- SENDING...
- SENT <HTTP status>
- SEND FAILED <HTTP status>
- SEND TIMEOUT

No floating windows.
No oversized action buttons.

## Architecture Contract

The Vertex Relay contract is amended:

- Clipboard = fallback
- DIRECT = configured Relay Bridge POST
- Hyper Agent / Vertex Core may own the Vera-facing bridge

## Scope

No FORGE runtime mutation.
No RAY runtime mutation.
No legacy `vertex_works` mutation.

Runtime acceptance requires a real Relay Bridge endpoint before SEND can be
declared end-to-end GREEN.

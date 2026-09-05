# Vertex Workstation — Middle Mouse Scroll + Legibility Pass 000011

## Mission

Improve dense Workstation content pages without changing their architecture.

### Middle mouse mechanism

Press the mouse wheel (middle button) and drag to scroll vertically.

Enabled on:

- CANONICAL card list
- CANONICAL detail form
- Architecture Contract card list
- Architecture Contract detail body

The mechanism uses React pointer handlers and pointer capture.
It does not reparent DOM and does not add floating UI.

Form controls are excluded from initiating middle-drag inside the CANONICAL
form so text fields retain normal editing behavior.

### Vertex Relay legibility

Increase the visual size of:

- VERTEX RELAY
- CANONICAL / SHARE or ARCHITECTURE_CONTRACT / SHARE
- TRANSPORT: CLIPBOARD · HUMAN GATE
- relay action labels
- relay receive textarea

No oversized action buttons.

### CANONICAL form legibility

Increase:

- Japanese field labels
- input/select/textarea text
- field padding
- textarea minimum height

Goal: reduce eye strain while preserving the current dense workstation layout.

## Scope

No floating windows.
No FORGE runtime behavior changes.
No RAY runtime behavior changes.
No legacy vertex_works mutation.
Runtime visual acceptance required.

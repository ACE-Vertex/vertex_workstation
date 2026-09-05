# Vertex Workstation — Architecture Contract Page 000009C

## Mission

Add a simple Architecture Contract content page to Vertex Workstation.

## UI

New top-level workspace tab:

`CONTRACT`

Page layout:

- left: card list, visually similar in density to Incoming Cargo
- right: selected Architecture Contract content

No floating windows.

## Initial contract cards

1. Folder Architecture
2. Component Ownership
3. Layout Ownership
4. Feature Boundary
5. Verification Ownership
6. Runtime Safety

Each card contains:

- title
- short summary
- status

Selecting a card updates the right-side detail with:

- principles
- rules
- notes

## Scope

This is intentionally a simple first content page.

No persistence.
No editor.
No version history.
No contract mutation workflow.
No FORGE behavior changes.
No RAY behavior changes.
No legacy `vertex_works` mutation.

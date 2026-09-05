# Vertex Workstation — RAY Layout / Runtime Lane Hotfix 000006H1

## Observed runtime failure

In browser LOCAL mode the page showed:

`RAY FILESYSTEM REQUIRES TAURI RUNTIME`

and the amber runtime notice expanded through almost the entire workspace while
the RAY cockpit collapsed into a thin strip at the bottom.

## Exact layout cause

000006 introduced `OperationIndicator` as a new page child but the RAY page grid
still relied on implicit sequential placement.

With a runtime error present, the children were effectively placed as:

1. Hero
2. Project Root
3. Operation Indicator
4. Command Bar
5. Runtime Error
6. Cockpit
7. Footer

The previous grid track contract did not explicitly own all seven children.

As a result, the conditional Runtime Error landed in the flexible
`minmax(0, 1fr)` track and consumed the workspace, while the cockpit was pushed
into the following fixed-height track.

## H1 repair

RAY now uses an explicit seven-lane contract:

1. Hero — 92px
2. Project Root — 52px
3. Operation Indicator — 40px
4. Command Bar — 52px
5. Runtime Notice — auto / compact
6. Cockpit — `minmax(0, 1fr)`
7. Status Board — 36px

Every major child receives an explicit `grid-row`.

Conditional notices can no longer steal the cockpit track.

## LOCAL browser behavior

The screenshot was taken in browser LOCAL mode, where the Tauri invoke bridge is
not present.

RAY real filesystem scan/read remains a Tauri capability.

H1 therefore makes LOCAL mode graceful:

- no automatic failing filesystem scan
- RAY header reports `LOCAL PREVIEW`
- Operation Indicator reports `LOCAL UI PREVIEW`
- filesystem controls are disabled
- the cockpit remains fully visible
- compact runtime notice explains that Tauri is required

This does not remove or weaken the real Tauri filesystem implementation.

## Scope

No RAY analysis redesign.
No filesystem protocol mutation.
No FORGE mutation.
No legacy `vertex_works` mutation.
No floating windows.

Runtime visual acceptance required.

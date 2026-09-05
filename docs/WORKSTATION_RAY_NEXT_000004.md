# Vertex Workstation — RAY NEXT Foundation 000004

## Mission

Establish the first RAY NEXT cockpit inside Vertex Workstation without copying
the legacy Works DOM ownership model.

RAY NEXT is treated as:

**targeting scope + microscope + software CT + evidence recorder**

## Persistent layout policy

Persistent tools MUST NOT use floating windows.

RAY NEXT uses:

- Grid
- Docked panels
- Split-oriented composition
- Responsive layout contracts
- Future tabs / collapse

Floating presentation is reserved only for transient OS dialogs or short-lived
confirmation/peek surfaces.

## 000004 cockpit

Primary panels:

1. Project Tree
2. Target Set
3. Ray Inspector
4. Evidence / Findings

Command bar:

- TARGET LOCK
- QUICK RAY
- DEEP RAY

Workstation-level tabs:

- FORGE
- RAY

## Target policy

Human target precedence is explicit:

`Human Priority → Dependency Expansion → Machine Relevance`

P1/P2 are human target rank concepts.

Rxx represents Ray machine relevance and is intentionally not merged with P rank.

## Ownership lenses

Inspector reserves separate fields for:

- Visual Parent
- Logical Owner
- State Owner
- Service Owner
- Style Owner
- Layout Slot
- Event Owner

DOM parentage is not ownership.

## Scope / limitation

000004 is the RAY cockpit and interaction foundation.

The analysis engine is deliberately still a stub. This pass does NOT yet wire:

- filesystem scanning
- AST extraction
- import graph
- call graph
- CSS selector influence graph
- event ownership graph
- dependency expansion
- actual Quick/Deep execution
- historical provenance discovery

Those become subsequent RAY precision passes after runtime visual acceptance.

No mutation of legacy `vertex_works`.

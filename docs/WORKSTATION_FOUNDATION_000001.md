# VERTEX WORKSTATION — FOUNDATION 000001

## Project

`G:\Vertex_Project\Development\vertex_workstation`

## Technology decision

- React
- TypeScript
- Vite
- Tauri
- Rust

Next.js is not part of the workstation runtime foundation.

## Architectural contract

1. Component Core is not the DOM.
2. DOM parentage never defines logical ownership.
3. Component identity is stable.
4. State owner, service owner, style owner and logical owner are explicit.
5. Presentation Port is the UI mounting boundary.
6. Layout changes mutate layout state, not DOM parent relationships.
7. Imperative DOM re-parenting is prohibited in application source.
8. Delete is denied while dependency references exist.
9. Runtime visual acceptance is mandatory after build.
10. Existing `vertex_works` is not modified by this artifact.

## Foundation proof

`forge.seed` is the first registered Component Core.

The screen exposes A1 / B1 / C1 layout slots. Changing slots updates the
Presentation Port layout only. The component's `pulse` counter must remain
unchanged while moving between slots.

Success proves:

`Core fixed / Presentation movable`

before FORGE NEXT or RAY NEXT construction begins.

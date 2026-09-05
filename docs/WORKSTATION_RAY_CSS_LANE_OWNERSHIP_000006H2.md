# Vertex Workstation — RAY CSS Lane Ownership Hotfix 000006H2

## Runtime evidence

Build `20260904-230018` proved that:

- Tauri filesystem sight is alive (`91 FILES VISIBLE`)
- the page no longer shows the giant runtime error
- but the RAY cockpit is still compressed to a thin strip at the bottom

This means the H1 logical seven-lane model existed in source, but did not win the
actual CSS cascade.

## Exact cause

`ray.css` still contains the older six-row `.ray-page` template.

H1 placed the seven-row replacement in `rayProcessing.css`.

Because the final bundle controls stylesheet order, the old `ray.css` rule could
win at runtime. With the new explicit child row assignments:

- empty/flexible old row consumed most of the viewport
- cockpit was assigned to row 6
- old row 6 was the fixed 36px track

That exactly matches the screenshot.

## H2 architecture repair

Stop using the processing stylesheet as a second layout owner.

New ownership:

- `ray.css` — RAY visual/cockpit base
- `rayLayoutContract.css` — ONLY page lane geometry
- `rayProcessing.css` — ONLY processing presentation / stacking

`App.tsx` imports `rayLayoutContract.css` explicitly after `ray.css`.

The layout contract also uses a scoped selector:

`.workstation-shell .workspace-stage .ray-page`

so the canonical seven-row contract cannot be casually overridden by the older
base selector.

## Hard rule reinforced

**1 Layout Layer = 1 Geometry Owner**

Processing animation may decorate the layout but must never own it.

## Scope

No RAY filesystem change.
No analysis change.
No FORGE change.
No floating windows.
No legacy `vertex_works` mutation.

Runtime visual acceptance is required.

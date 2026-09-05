# Vertex Workstation — 000011H1

## Cause

`onAuxClick` was typed as `PointerEventHandler<HTMLElement>`.

React DOM defines `onAuxClick` as a mouse event handler, so spreading the
middle-scroll bindings onto a `<div>` caused TS2322.

## Fix

Only the event type contract is corrected:

- `onAuxClick: PointerEventHandler<HTMLElement>`
- becomes
- `onAuxClick: MouseEventHandler<HTMLElement>`

The middle-button runtime behavior itself is unchanged.

The pointer-based handlers remain pointer handlers:

- onPointerDown
- onPointerMove
- onPointerUp
- onPointerCancel

No layout change.
No CANONICAL logic change.
No Architecture Contract logic change.
No FORGE/RAY runtime mutation.
No floating windows.

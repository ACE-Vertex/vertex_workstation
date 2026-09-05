# Vertex Workstation — RAY Processing Animation 000006

## Mission

Make RAY processing state unmistakable while preserving the fixed cockpit.

The visual direction is inspired by the **idea** of animated grid-distortion
backgrounds seen in modern React component galleries, but the implementation in
this artifact is original Workstation code and does not copy third-party source.

## Processing signal

During:

- PROJECT SCAN
- FILE READ

RAY displays a persistent docked operation indicator containing:

- concentric orbit / pulse
- moving scan bar
- operation phase
- current path/file detail
- elapsed timer

When processing ends, the indicator returns to FILE SIGHT READY.

## Ambient grid distortion

The existing Workstation grid becomes an active visual instrument.

During processing:

- grid lines bend around an analysis focus region
- wave + swirl displacement increases
- cyan energy field becomes slightly stronger

When idle:

- the grid becomes nearly static and faint

The effect is rendered on a dedicated canvas presentation layer.

## Hard layer contract

The distortion layer:

- `position: absolute`
- `z-index: 0`
- `pointer-events: none`

RAY content:

- `z-index: 1`
- isolated stacking context

Therefore the animation cannot own or intercept workspace interaction.

This explicitly preserves the lesson from the old Works/RAY atmosphere incident:
background effects must never cover or own active workspace behavior.

## Accessibility

`prefers-reduced-motion` disables the active CSS motion and keeps the visual cue
subtle.

## Scope

No floating window.
No filesystem behavior change.
No scan/read protocol change.
No legacy `vertex_works` mutation.

Runtime visual acceptance is required.

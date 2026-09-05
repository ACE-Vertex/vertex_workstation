# Vertex Workstation

Greenfield successor workspace built alongside the stable Vertex Works
`20260904-173222` lifeline.

## Foundation stack

- React
- TypeScript
- Vite
- Tauri
- Rust

## First architecture rule

DOM is render output, not ownership.

Component identity, state ownership, service ownership, style ownership and
layout position are separate contracts.

## Foundation 000001

The first component (`forge.seed`) is registered in the Component Registry and
rendered through a Presentation Port.

Moving A1 → B1 → C1 changes only layout state. The component stays in the same
React ownership tree and its local state must survive the move.

This is the first proof for the future Layout Drone model.

# Vertex Workstation Unit Contract 0.1

## Core construction rules

1. No Welded Dependency.
2. Every connection must be detachable.
3. Host must not own unit internals.
4. Unit must survive host migration.
5. No unit-to-unit direct wiring.
6. Host Bus is the only cross-unit mediation surface.
7. RAY authority is READ_ONLY.
8. FORGE mutation authority is HUMAN_APPLY.
9. Mounting a unit must not silently start watchers, mutate files, or spawn work.
10. Unmount must leave no process, lock, watcher, IPC endpoint, or temp residue.
11. View is a result of state; view must not become an execution trigger.
12. Vue owns the DOM. Direct imperative DOM mutation is forbidden.
13. A unit is not promoted until its complete contract is proven end-to-end.

## Workstation scope

Vertex Works contains only two operational units:

- RAY
- FORGE

Todo, adoption ledgers, project memory, Beacon, VPO and other organs belong outside the Works core.

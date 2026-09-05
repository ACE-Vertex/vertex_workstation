# Vertex Workstation — RAY Project Selection + File Sight 000005H2

## Exact failure

000005H1 successfully repaired:

- the stray leading backslash in `rayAnalysis.ts`
- the stray leading backslash in `RayPage.tsx`
- Rust formatting

After those repairs, TypeScript exposed the next exact failure:

`src/features/ray/seedData.ts` still contains the old 000004 demo `RayFile`
objects with fields such as:

- `humanPriority`
- `rayRelevance`
- `symbols`
- `relationHint`

The 000005 real-filesystem `RayFile` model intentionally replaced that shape
with actual filesystem metadata.

`seedData.ts` is no longer imported by RAY 000005, but TypeScript still compiles
the unused source file because it remains under `src/`.

## H2 repair

Physically retire the obsolete 000004 demo source:

`src/features/ray/seedData.ts`

The hotfix first scans current source files and refuses deletion if any active
TypeScript/JavaScript source still imports the module.

This follows the Workstation architecture rule:

**retired implementation must not survive as an active compilable source owner.**

## Scope

No RAY layout changes.
No Project Root behavior changes.
No filesystem scan/read changes.
No ownership changes.
No legacy `vertex_works` mutation.

After retirement, H2 re-runs:

1. TypeScript + Vite build
2. rustfmt check
3. cargo check
4. existing 000005 verifier
5. existing Tauri production builder

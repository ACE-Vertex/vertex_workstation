# Vertex Workstation — RAY Project Selection + File Sight 000005H3

## Exact H2 failure

H2 correctly refused to delete `src/features/ray/seedData.ts`, but its reference
guard was too broad.

It searched the entire `src/` tree for the literal sibling import string
`./seedData`.

`src/features/forge/ForgePage.tsx` legitimately imports:

`./seedData`

but that resolves to:

`src/features/forge/seedData.ts`

—not to the stale RAY module.

The H2 guard therefore produced a false positive and preserved the obsolete
`src/features/ray/seedData.ts`, so TypeScript continued compiling its obsolete
000004 `RayFile` object shape and emitted TS2353.

## H3 repair

Use feature-scoped module resolution for the retirement guard:

- only source files under `src/features/ray/` are allowed to block retirement
- only actual sibling `./seedData` import/require forms are matched
- `src/features/forge/seedData.ts` must remain present
- `src/features/ray/seedData.ts` is physically retired when unreferenced

This is a guard correction only.

## Scope

No FORGE mutation.
No RAY layout mutation.
No filesystem scan/read mutation.
No ownership-contract mutation.
No legacy `vertex_works` mutation.

After retirement:

1. TypeScript + Vite build
2. rustfmt check
3. cargo check
4. existing 000005 verifier
5. existing Tauri production builder

# Vertex Workstation — FORGE Legacy Fidelity 000002H1

## Exact failure

000002 structural checks all passed, then TypeScript failed with:

- `ForgePage.tsx(1,1): error TS1127: Invalid character`
- `seedData.ts(1,1): error TS1127: Invalid character`

The same two files failed again during the Tauri `beforeBuildCommand`.

## Root cause

Those two source payloads were generated from Python raw triple-quoted strings
whose opening form preserved a leading backslash byte.

Result:

`\import ...`

at byte 0 instead of:

`import ...`

TypeScript correctly rejected the first character.

## H1 fix

Remove exactly one leading backslash byte from:

- `src/features/forge/ForgePage.tsx`
- `src/features/forge/seedData.ts`

The hotfix is idempotent and validates that both files begin with an import after
the repair.

No layout redesign.
No CSS change.
No React ownership change.
No Component Registry change.
No Vertex Works mutation.

After source repair:
1. `npm run build`
2. existing 000002 structural verifier
3. existing Workstation Tauri production builder

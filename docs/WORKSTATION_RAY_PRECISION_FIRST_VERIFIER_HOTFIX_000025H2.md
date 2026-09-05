# Vertex Workstation — RAY 000025H2 Verifier Hotfix

## Exact failure

000025H1 runtime/source checks passed for:
- idle FILE SIGHT banner removal
- RAY ENGINE READY removal
- TARGET POLICY prose removal
- active processing indicator preservation
- command-bar compaction
- DEEP RAY clipboard preservation
- language-aware analysis
- no floating UI

Only `NO_IDLE_OPERATION_INDICATOR` failed.

## Root cause

The H1 verifier searched the entire `RayPage.tsx` for:

`active={Boolean(operation)}`

That expression is legitimately used by the existing
`ProcessingGridDistortion` processing animation.

It is not evidence that the removed idle `OperationIndicator` still exists.

The verifier therefore produced a false negative.

## H2

Verifier only. No runtime/source behavior is changed.

The corrected check scopes inspection specifically to the
`{operation ? (<OperationIndicator ... />) : null}` block.

`ProcessingGridDistortion` is explicitly allowed to keep using
`Boolean(operation)`.

Runtime intent remains:
- no idle status banner
- processing feedback only while real work is active
- precision/evidence first

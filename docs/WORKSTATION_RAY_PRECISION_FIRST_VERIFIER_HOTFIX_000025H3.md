# Vertex Workstation — RAY Precision First Verifier Hotfix 000025H3

## Exact failure

000025H2 passed every direct RAY UI / behavior assertion, including:

- idle FILE SIGHT banner removed
- RAY ENGINE ready banner removed
- TARGET POLICY prose removed
- active-only processing indicator preserved
- command bar compact
- DEEP RAY clipboard preserved
- language-aware analysis present
- no floating UI

It then failed because the H2 verifier attempted to execute:

`scripts\verify_ray_language_aware_fact_extractor_000025.py`

That file does not exist in this installation.

## Root cause

000025H1 explicitly superseded plain 000025 and carried the actual
`rayAnalysis.ts` language-aware implementation forward, but it did not install
the standalone plain-000025 verifier script.

H2 therefore depended on an artifact that the superseding path did not require
the user to apply.

## H3

Verifier-only hotfix.

No runtime/source behavior is changed.

The language-aware precision assertions are now checked directly against
`src/features/ray/rayAnalysis.ts`, making the verifier self-contained.

The verifier still runs:
- 000024 clipboard regression
- frontend build
- cargo check
- FORGE 000022 regression

After H3 GREEN and runtime visual acceptance, the next planned action is
GitHub Push.

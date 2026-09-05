# Vertex Workstation — FORGE Real APPLY / ROLLBACK 000022H2

Returned Evidence showed the 000022H1 runtime/source repair was applied, but
the H1 verifier itself failed before testing anything:

`ValueError: substring not found`

The verifier searched for:

`async function chooseFolder(`

The actual FORGE function is:

`async function browsePath(`

Therefore this is a verifier-only hotfix.

No React, Rust, APPLY, ROLLBACK, Stage, Receiving Bay, history-color, Relay,
or provider runtime source is changed.

H2 verifies the real `browsePath -> stageArtifact -> applyStage -> rollbackStage`
boundaries, then reruns the 000022 verifier, 000020 live Receiving verifier,
000021 cargo-history verifier, OpenAI adapter regression, and immutable
production build.

Runtime acceptance is still required after a successful build:
STAGE -> STAGED -> APPLY armed -> APPLYING -> APPLIED -> ROLLBACK armed.

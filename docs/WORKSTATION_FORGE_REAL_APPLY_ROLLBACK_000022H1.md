# Vertex Workstation — FORGE Real APPLY / ROLLBACK 000022H1

Evidence showed a precise TypeScript scope error:

- `ForgePage.tsx(296,11): Cannot find name 'artifact'`
- `ForgePage.tsx(302,31): Cannot find name 'artifact'`

Cause:
The 000021 Stage-error history update had been inserted into the
`chooseFolder()` catch block, where no `artifact` variable exists.

Fix:
- remove that block from `chooseFolder()`
- move it into the `stageArtifact(artifact)` catch block, which is its correct owner
- remove one unused Rust `Write` import warning
- do not change APPLY / ROLLBACK behavior

This is a scope/ownership hotfix only.

Runtime acceptance after build remains:
STAGE -> STAGED -> APPLY armed -> APPLYING -> APPLIED -> ROLLBACK armed.

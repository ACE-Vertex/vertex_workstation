import type {
  ForgeApplyResult,
  ForgeArtifact,
  ForgeRollbackResult,
  ForgeStageResult,
} from "./models";

interface ArtifactInspectorProps {
  readonly artifact?: ForgeArtifact;
  readonly stageResult: ForgeStageResult | null;
  readonly applyResult: ForgeApplyResult | null;
  readonly rollbackResult: ForgeRollbackResult | null;
  readonly staging: boolean;
  readonly applying: boolean;
  readonly rollingBack: boolean;
  readonly onStage: (artifact: ForgeArtifact) => void;
  readonly onApply: (stage: ForgeStageResult) => void;
  readonly onRollback: (stage: ForgeStageResult) => void;
  readonly onCopyInspection: (artifact: ForgeArtifact) => void;
}

export function ArtifactInspector({
  artifact,
  stageResult,
  applyResult,
  rollbackResult,
  staging,
  applying,
  rollingBack,
  onStage,
  onApply,
  onRollback,
  onCopyInspection,
}: ArtifactInspectorProps) {
  const staged = Boolean(
    artifact &&
    stageResult &&
    stageResult.artifactId === artifact.id,
  );
  const applied = Boolean(
    staged &&
    applyResult &&
    applyResult.stageId === stageResult?.stageId,
  );
  const rolledBack = Boolean(
    staged &&
    rollbackResult &&
    rollbackResult.stageId === stageResult?.stageId,
  );

  return (
    <section className="forge-panel inspector-panel">
      <header className="panel-header">
        <div>
          <span>02 / INSPECTION + HUMAN GATE</span>
          <h2>Artifact Inspector</h2>
        </div>
        <span
          className={`verified-chip ${
            artifact?.status === "ATTENTION" ? "attention" : ""
          }`}
        >
          {rolledBack
            ? "ROLLED BACK"
            : applied
              ? "APPLIED"
              : staged
                ? "STAGED"
                : artifact
                  ? artifact.status
                  : "INSPECT"}
        </span>
      </header>

      {!artifact ? (
        <div className="empty-state">SELECT INCOMING CARGO</div>
      ) : (
        <div className="inspector-body forge-real-inspector">
          <div className="inspector-grid">
            <div><span>ID</span><strong>{artifact.id}</strong></div>
            <div><span>TITLE</span><strong>{artifact.title}</strong></div>
            <div><span>SCHEMA</span><strong>{artifact.schemaVersion || "UNKNOWN"}</strong></div>
            <div><span>SOURCE</span><strong>{artifact.source || "UNKNOWN"}</strong></div>
            <div><span>TARGET</span><strong>{artifact.target || "UNRESOLVED"}</strong></div>
            <div><span>AUTHORITY</span><strong>{artifact.authority || "UNKNOWN"}</strong></div>
            <div><span>PAYLOAD</span><strong>{artifact.payloadCount} operation(s)</strong></div>
            <div><span>VERIFY</span><strong>{artifact.verificationCount} command(s)</strong></div>
            <div><span>TARGET GATE</span><strong>{artifact.targetAuthorized ? "AUTHORIZED" : "BLOCKED"}</strong></div>
            <div><span>SIZE</span><strong>{artifact.sizeBytes} bytes</strong></div>
          </div>

          <div
            className={`stage-banner ${
              artifact.status === "ATTENTION" ? "attention" : ""
            }`}
          >
            <strong>
              {staged
                ? `STAGED · ${stageResult?.verifiedCount ?? 0}/${stageResult?.payloadCount ?? 0} HASH VERIFIED`
                : artifact.manifestValid
                  ? "RECEIVED / MANIFEST INSPECTED"
                  : "RECEIVED / MANIFEST ATTENTION"}
            </strong>
            <code>
              {staged
                ? stageResult?.stagingRoot
                : artifact.filePath}
            </code>
          </div>

          <div className="forge-manifest-detail">
            <div>
              <span>{staged ? "STAGED PAYLOAD" : "OPERATION PREVIEW"}</span>
              {staged ? (
                stageResult?.operations.map((operation, index) => (
                  <code key={`${operation.destination}:${index}`}>
                    {String(index + 1).padStart(2, "0")} HASH OK → {operation.destination}
                    {operation.existedBefore ? " · BACKUP PLANNED" : " · NEW FILE"}
                  </code>
                ))
              ) : artifact.operationPreview.length ? (
                artifact.operationPreview.map((line) => (
                  <code key={line}>{line}</code>
                ))
              ) : (
                <small>NO COPY OPERATIONS RESOLVED</small>
              )}
            </div>

            {staged ? (
              <div className="stage-proof">
                <span>STAGE PROOF</span>
                <code>STAGE ID={stageResult?.stageId}</code>
                <code>ARTIFACT SHA256={stageResult?.artifactSha256}</code>
                <code>TARGET={stageResult?.targetRoot}</code>
                <code>BACKUP PLAN={stageResult?.backupPlanRoot}</code>
              </div>
            ) : artifact.errors.length ? (
              <div className="manifest-errors">
                <span>INSPECTION ERRORS</span>
                {artifact.errors.map((error) => (
                  <code key={error}>{error}</code>
                ))}
              </div>
            ) : (
              <div>
                <span>GATES</span>
                <code>SCHEMA=vra/1</code>
                <code>AUTHORITY=HUMAN_APPLY</code>
                <code>TARGET=AUTHORIZED</code>
                <code>PAYLOAD=READY FOR HASH STAGE</code>
              </div>
            )}
          </div>

          <div className="inspector-actions">
            <button
              type="button"
              disabled={
                staging ||
                applying ||
                rollingBack ||
                staged ||
                artifact.status !== "READY" ||
                !artifact.targetAuthorized
              }
              onClick={() => onStage(artifact)}
            >
              {staging
                ? "STAGING..."
                : staged
                  ? "STAGED"
                  : "STAGE"}
            </button>
            <button
              type="button"
              className={staged && !applied && !rolledBack ? "apply-armed" : ""}
              disabled={
                !staged ||
                staging ||
                applying ||
                rollingBack ||
                applied ||
                rolledBack ||
                !stageResult
              }
              onClick={() => stageResult && onApply(stageResult)}
              title={
                staged && !applied && !rolledBack
                  ? "HUMAN APPLY — mutate authorized production target using immutable staged payload"
                  : "APPLY arms only after the current artifact is STAGED"
              }
            >
              {applying
                ? "APPLYING..."
                : applied
                  ? "APPLIED"
                  : rolledBack
                    ? "APPLY CLOSED"
                    : "APPLY / FORGE"}
            </button>
            <button
              type="button"
              className={applied && !rolledBack ? "danger rollback-armed" : "danger"}
              disabled={
                !staged ||
                !applied ||
                rolledBack ||
                staging ||
                applying ||
                rollingBack ||
                !stageResult
              }
              onClick={() => stageResult && onRollback(stageResult)}
              title={
                applied && !rolledBack
                  ? "Restore backups and remove files created by this APPLY"
                  : "ROLLBACK arms only after APPLY"
              }
            >
              {rollingBack
                ? "ROLLING BACK..."
                : rolledBack
                  ? "ROLLED BACK"
                  : "ROLLBACK"}
            </button>
          </div>

          <div className="return-lane">
            <span className="return-dot" />
            <div>
              <small>INSPECTION / RETURN LANE</small>
              <strong>
                {rolledBack
                  ? "ROLLBACK COMPLETE"
                  : applied
                    ? "APPLY COMPLETE / ROLLBACK ARMED"
                    : staged
                      ? "STAGE VERIFIED / HUMAN APPLY ARMED"
                      : artifact.status === "READY"
                        ? "MANIFEST READY"
                        : "ATTENTION REQUIRED"}
              </strong>
            </div>
            <button
              type="button"
              onClick={() => onCopyInspection(artifact)}
            >
              COPY INSPECTION
            </button>
          </div>
        </div>
      )}
    </section>
  );
}

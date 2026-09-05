import type { RayFinding } from "./models";

interface RayEvidenceProps {
  readonly findings: readonly RayFinding[];
  readonly onRevealLine: (line: number) => void;
}

export function RayEvidence({
  findings,
  onRevealLine,
}: RayEvidenceProps) {
  return (
    <section className="ray-panel ray-evidence-panel">
      <header className="ray-panel-header">
        <div>
          <span>05 / EVIDENCE</span>
          <h2>Evidence / Findings</h2>
        </div>
        <strong>{findings.length} FINDINGS</strong>
      </header>

      <div className="evidence-list">
        {findings.length === 0 ? (
          <div className="ray-empty">RUN QUICK RAY OR DEEP RAY</div>
        ) : (
          findings.map((finding) => (
            <article className="finding-row" key={finding.id}>
              <span className={`finding-severity ${finding.severity.toLowerCase()}`}>
                {finding.severity}
              </span>
              <div className="finding-copy">
                <strong>{finding.title}</strong>
                <small>{finding.evidence}</small>
                <code>
                  {finding.source}
                  {finding.lineStart ? ` · L${finding.lineStart}` : ""}
                  {finding.lineEnd && finding.lineEnd !== finding.lineStart
                    ? `–L${finding.lineEnd}`
                    : ""}
                </code>
              </div>
              <div className="confidence">
                <span>{Math.round(finding.confidence * 100)}%</span>
                <small>CONF</small>
                {finding.lineStart ? (
                  <button
                    type="button"
                    className="ray-evidence-reveal"
                    onClick={() => onRevealLine(finding.lineStart!)}
                  >
                    REVEAL L{finding.lineStart}
                  </button>
                ) : null}
              </div>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

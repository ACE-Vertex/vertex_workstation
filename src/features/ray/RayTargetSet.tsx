import type { RayFile } from "./models";

interface RayTargetSetProps {
  readonly targets: readonly RayFile[];
  readonly locked: boolean;
  readonly onActivate: (id: string) => void;
}

export function RayTargetSet({
  targets,
  locked,
  onActivate,
}: RayTargetSetProps) {
  return (
    <section className="ray-panel ray-target-panel">
      <header className="ray-panel-header">
        <div>
          <span>03 / HUMAN TARGET</span>
          <h2>Target Set</h2>
        </div>
        <strong>{locked ? "LOCKED" : "OPEN"} · {targets.length}</strong>
      </header>

      <div className="target-set-list">
        {targets.length === 0 ? (
          <div className="ray-empty">ADD FILES FROM PROJECT TREE</div>
        ) : (
          targets.map((file, index) => (
            <button
              type="button"
              className="target-row"
              onClick={() => onActivate(file.id)}
              key={file.id}
            >
              <div className="priority-cell">
                <span>P{index + 1}</span>
                <small>HUMAN</small>
              </div>
              <div className="target-copy">
                <strong>{file.relativePath}</strong>
                <small>{file.provenance} · {file.sizeBytes} bytes</small>
              </div>
              <div className="ray-rank">
                <span>R—</span>
                <small>NEXT</small>
              </div>
            </button>
          ))
        )}
      </div>
    </section>
  );
}

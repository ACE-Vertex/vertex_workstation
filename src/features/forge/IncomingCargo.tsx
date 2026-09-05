import { useMemo, useState } from "react";
import type { ForgeArtifact } from "./models";

interface IncomingCargoProps {
  readonly artifacts: readonly ForgeArtifact[];
  readonly selectedId: string;
  readonly busy: boolean;
  readonly onSelect: (id: string) => void;
  readonly onRefresh: () => void;
}

type CargoVisualState =
  | "unusable"
  | "unstaged"
  | "stage-error"
  | "verified";

function cargoVisualState(artifact: ForgeArtifact): CargoVisualState {
  if (artifact.status !== "READY") return "unusable";
  if (artifact.stageHistory === "VERIFIED") return "verified";
  if (artifact.stageHistory === "ERROR") return "stage-error";
  return "unstaged";
}

function statusLabel(artifact: ForgeArtifact) {
  const state = cargoVisualState(artifact);
  if (state === "unusable") return "UNUSABLE";
  if (state === "verified") return "VERIFIED";
  if (state === "stage-error") return "STAGE ERROR";
  return "READY · UNSTAGED";
}

function statusSortKey(artifact: ForgeArtifact) {
  const state = cargoVisualState(artifact);
  const rank: Record<CargoVisualState, number> = {
    unusable: 0,
    "stage-error": 1,
    unstaged: 2,
    verified: 3,
  };
  return `${rank[state]}:${artifact.fileName}`;
}

export function IncomingCargo({
  artifacts,
  selectedId,
  busy,
  onSelect,
  onRefresh,
}: IncomingCargoProps) {
  const [sort, setSort] = useState<"name" | "status">("name");

  const sorted = useMemo(() => {
    const copy = [...artifacts];
    if (sort === "status") {
      return copy.sort((a, b) =>
        statusSortKey(a).localeCompare(statusSortKey(b)),
      );
    }
    return copy.sort((a, b) => a.fileName.localeCompare(b.fileName));
  }, [artifacts, sort]);

  return (
    <section className="forge-panel incoming-panel">
      <header className="panel-header">
        <div>
          <span>01 / RECEIVING BAY</span>
          <h2>Incoming Cargo</h2>
        </div>
        <div className="panel-tools">
          <button
            type="button"
            className={sort === "name" ? "active" : ""}
            onClick={() => setSort("name")}
          >
            NAME
          </button>
          <button
            type="button"
            className={sort === "status" ? "active" : ""}
            onClick={() => setSort("status")}
          >
            STATUS
          </button>
          <button type="button" onClick={onRefresh} disabled={busy}>
            {busy ? "SCANNING..." : "REFRESH"}
          </button>
        </div>
      </header>

      <div className="cargo-list" role="list">
        {sorted.length === 0 ? (
          <div className="empty-state forge-inline-empty">
            NO .VRA ARTIFACTS IN RECEIVING BAY
          </div>
        ) : (
          sorted.map((artifact) => {
            const visualState = cargoVisualState(artifact);
            return (
            <button
              type="button"
              className={`cargo-card forge-cargo-${visualState} ${artifact.id === selectedId ? "selected" : ""}`}
              onClick={() => onSelect(artifact.id)}
              key={`${artifact.filePath}:${artifact.id}`}
            >
              <div className="cargo-title-row">
                <strong>{artifact.title}</strong>
                <span className={`artifact-status forge-cargo-status-${visualState}`}>
                  {statusLabel(artifact)}
                </span>
              </div>
              <small>{artifact.schemaVersion || "UNKNOWN SCHEMA"}</small>
              <code>{artifact.fileName}</code>
              <code>{artifact.target || "TARGET UNRESOLVED"}</code>
            </button>
            );
          })
        )}
      </div>
    </section>
  );
}

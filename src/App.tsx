import { useState } from "react";
import { ForgePage } from "./features/forge/ForgePage";
import { RayPage } from "./features/ray/RayPage";
import { ArchitectureContractPage } from "./features/contracts/ArchitectureContractPage";
import { CanonicalRegistryPage } from "./features/canonical/CanonicalRegistryPage";
import "./styles.css";
import "./shell/workstationShell.css";
import "./features/ray/ray.css";
import "./features/ray/rayLayoutContract.css";
import "./core/input/middleMouseScroll.css";

type Workspace = "forge" | "ray" | "contract" | "canonical";

export default function App() {
  const [workspace, setWorkspace] = useState<Workspace>("forge");

  return (
    <div className="workstation-shell">
      <nav
        className="workspace-switcher"
        aria-label="Vertex Workstation workspace"
      >
        <div className="workspace-brand">
          <strong>VERTEX WORKSTATION</strong>
          <span>CORE / PRESENTATION SEPARATED</span>
        </div>

        <div
          className="workspace-tabs"
          role="tablist"
          aria-label="Workspaces"
        >
          <button
            type="button"
            role="tab"
            aria-selected={workspace === "forge"}
            className={workspace === "forge" ? "active" : ""}
            onClick={() => setWorkspace("forge")}
          >
            FORGE
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={workspace === "ray"}
            className={workspace === "ray" ? "active" : ""}
            onClick={() => setWorkspace("ray")}
          >
            RAY
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={workspace === "contract"}
            className={workspace === "contract" ? "active" : ""}
            onClick={() => setWorkspace("contract")}
          >
            CONTRACT
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={workspace === "canonical"}
            className={workspace === "canonical" ? "active" : ""}
            onClick={() => setWorkspace("canonical")}
          >
            CANONICAL
          </button>
        </div>

        <div className="workspace-contract">
          NO FLOAT / GRID + DOCK + SPLIT
        </div>
      </nav>

      <section className="workspace-stage">
        {workspace === "forge" ? (
          <ForgePage />
        ) : workspace === "ray" ? (
          <RayPage />
        ) : workspace === "contract" ? (
          <ArchitectureContractPage />
        ) : (
          <CanonicalRegistryPage />
        )}
      </section>
    </div>
  );
}

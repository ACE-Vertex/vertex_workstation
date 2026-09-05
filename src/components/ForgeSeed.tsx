import { useState } from "react";
import { getComponentContract } from "../core/componentRegistry";

export function ForgeSeed() {
  const [pulse, setPulse] = useState(0);
  const contract = getComponentContract("forge.seed");

  return (
    <article className="forge-seed">
      <header className="seed-header">
        <div>
          <span className="eyebrow">FIRST COMPONENT CORE</span>
          <h2>FORGE SEED</h2>
        </div>
        <span className="status-chip">CORE STABLE</span>
      </header>

      <div className="contract-grid">
        <div><span>Component</span><strong>{contract.componentId}</strong></div>
        <div><span>Logical Owner</span><strong>{contract.logicalOwner}</strong></div>
        <div><span>State Owner</span><strong>{contract.stateOwner}</strong></div>
        <div><span>Style Owner</span><strong>{contract.styleOwner}</strong></div>
      </div>

      <div className="seed-state">
        <span>State continuity test</span>
        <strong>{pulse}</strong>
        <button type="button" onClick={() => setPulse((value) => value + 1)}>
          PULSE +1
        </button>
      </div>
    </article>
  );
}

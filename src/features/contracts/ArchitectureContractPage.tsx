import { useMemo, useState } from "react";
import { useMiddleMouseScroll } from "../../core/input/useMiddleMouseScroll";
import {
  createVertexRelay,
} from "../../core/relay/vertexRelay";
import type { VertexRelayEnvelope } from "../../core/relay/types";
import { VertexRelayBar } from "../../shell/relay/VertexRelayBar";
import {
  ARCHITECTURE_CONTRACTS,
  type ArchitectureContractItem,
} from "./contracts";
import "./architectureContract.css";
import "./architectureRelay.css";

function ContractDetail({
  contract,
  relay,
  onReceive,
  detailScroll,
}: {
  readonly contract: ArchitectureContractItem;
  readonly relay: VertexRelayEnvelope;
  readonly onReceive: (envelope: VertexRelayEnvelope) => void;
  readonly detailScroll: ReturnType<typeof useMiddleMouseScroll>;
}) {
  return (
    <section className="architecture-detail">
      <header className="architecture-detail-header">
        <div>
          <span>
            {contract.index} / ARCHITECTURE CONTRACT
          </span>
          <h2>{contract.title}</h2>
          <p>{contract.summary}</p>
        </div>
        <strong className="architecture-status">
          {contract.status}
        </strong>
      </header>

      <div className="architecture-detail-body middle-scroll-surface" {...detailScroll}>
        <section>
          <span>PRINCIPLES</span>
          {contract.principles.map((item) => (
            <article key={item}>
              <b>◆</b>
              <p>{item}</p>
            </article>
          ))}
        </section>

        <section>
          <span>RULES</span>
          <ol>
            {contract.rules.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </section>

        <section>
          <span>NOTES</span>
          {contract.notes.map((item) => (
            <code key={item}>{item}</code>
          ))}
        </section>
      </div>

      <div className="architecture-relay-slot">
        <VertexRelayBar
          envelope={relay}
          onReceive={onReceive}
        />
      </div>
    </section>
  );
}

export function ArchitectureContractPage() {
  const [contracts, setContracts] =
    useState<ArchitectureContractItem[]>(
      [...ARCHITECTURE_CONTRACTS],
    );
  const [selectedId, setSelectedId] =
    useState(contracts[0].id);
  const cardScroll = useMiddleMouseScroll({ axis: "y" });
  const detailScroll = useMiddleMouseScroll({ axis: "y" });

  const selected = useMemo(
    () =>
      contracts.find(
        (item) => item.id === selectedId,
      ) ?? contracts[0],
    [contracts, selectedId],
  );

  const relay = createVertexRelay({
    type: "ARCHITECTURE_CONTRACT",
    action: "SHARE",
    subjectId: selected.id,
    subjectName: selected.title,
    payload: selected,
  });

  function receiveRelay(
    envelope: VertexRelayEnvelope,
  ) {
    if (
      envelope.type !==
      "ARCHITECTURE_CONTRACT"
    ) {
      return;
    }

    const payload =
      envelope.payload as Partial<ArchitectureContractItem>;

    if (!payload.title) return;

    const incoming: ArchitectureContractItem = {
      id:
        typeof payload.id === "string" &&
        payload.id
          ? payload.id
          : `contract-relay-${Date.now()}`,
      index:
        typeof payload.index === "string" &&
        payload.index
          ? payload.index
          : String(contracts.length + 1)
              .padStart(2, "0"),
      title: payload.title,
      summary:
        typeof payload.summary === "string"
          ? payload.summary
          : "",
      status:
        payload.status === "ACTIVE"
          ? "ACTIVE"
          : "DRAFT",
      principles: Array.isArray(
        payload.principles,
      )
        ? payload.principles.filter(
            (item): item is string =>
              typeof item === "string",
          )
        : [],
      rules: Array.isArray(payload.rules)
        ? payload.rules.filter(
            (item): item is string =>
              typeof item === "string",
          )
        : [],
      notes: Array.isArray(payload.notes)
        ? payload.notes.filter(
            (item): item is string =>
              typeof item === "string",
          )
        : [],
    };

    setContracts((current) => {
      const exists = current.some(
        (item) => item.id === incoming.id,
      );

      if (exists) {
        return current.map((item) =>
          item.id === incoming.id
            ? incoming
            : item,
        );
      }

      return [incoming, ...current];
    });

    setSelectedId(incoming.id);
  }

  return (
    <main className="architecture-page">
      <header className="architecture-hero">
        <div>
          <span>
            STRUCTURE · OWNERSHIP · VERIFICATION · RUNTIME
          </span>
          <h1>
            ARCHITECTURE <strong>CONTRACT</strong>
          </h1>
          <p>
            Vertex Workstation の設計原則・所有権・境界を明文化する。
          </p>
        </div>

        <div className="architecture-hero-meta">
          <span>CONTRACT SET</span>
          <strong>
            {contracts.length} ITEMS
          </strong>
          <code>
            WORKSTATION / ACTIVE ARCHITECTURE
          </code>
        </div>
      </header>

      <section className="architecture-grid">
        <aside className="architecture-list">
          <header>
            <div>
              <span>01 / CONTRACT INDEX</span>
              <h2>Architecture Cards</h2>
            </div>
            <strong>{contracts.length}</strong>
          </header>

          <div className="architecture-card-list middle-scroll-surface" {...cardScroll}>
            {contracts.map((contract) => (
              <button
                type="button"
                className={
                  selectedId === contract.id
                    ? "architecture-card active"
                    : "architecture-card"
                }
                onClick={() =>
                  setSelectedId(contract.id)
                }
                key={contract.id}
              >
                <div>
                  <span>{contract.index}</span>
                  <strong>{contract.title}</strong>
                </div>

                <p>{contract.summary}</p>
                <small>{contract.status}</small>
              </button>
            ))}
          </div>
        </aside>

        <ContractDetail
          contract={selected}
          relay={relay}
          onReceive={receiveRelay}
          detailScroll={detailScroll}
        />
      </section>

      <footer className="architecture-footer">
        <span>
          CONTRACT VIEW — READ / SELECT / REVIEW
        </span>
        <span>
          NO FLOAT · FEATURE FIRST · OWNERSHIP EXPLICIT · RELAY READY
        </span>
      </footer>
    </main>
  );
}

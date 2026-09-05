import { useMemo, useState } from "react";
import { useMiddleMouseScroll } from "../../core/input/useMiddleMouseScroll";
import {
  createVertexRelay,
} from "../../core/relay/vertexRelay";
import type { VertexRelayEnvelope } from "../../core/relay/types";
import { VertexRelayBar } from "../../shell/relay/VertexRelayBar";
import { CANONICAL_SEED } from "./canonicalSeed";
import { ConceptIcon } from "./ConceptIcon";
import type {
  CanonicalConcept,
  CanonicalImportance,
  CanonicalStatus,
} from "./models";
import "./canonicalRegistry.css";

const STORAGE_KEY = "vertex.canonical.registry.v1";

function loadConcepts(): CanonicalConcept[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [...CANONICAL_SEED];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed)
      ? (parsed as CanonicalConcept[])
      : [...CANONICAL_SEED];
  } catch {
    return [...CANONICAL_SEED];
  }
}

function makeDraftConcept(): CanonicalConcept {
  const stamp = Date.now();

  return {
    id: `canonical-draft-${stamp}`,
    formalName: "New Concept",
    abbreviation: "NEW",
    status: "DRAFT",
    importance: "NORMAL",
    scope: "ALL_VERTEX_PRODUCTS",
    category: "UNCLASSIFIED",
    summary: "",
    functionText: "",
    description: "",
    origin: "",
    aliases: "",
    related: "",
    flavorBadge: "",
    adoptedBy: "Human + Vera",
    notes: "",
  };
}

export function CanonicalRegistryPage() {
  const [concepts, setConcepts] =
    useState<CanonicalConcept[]>(loadConcepts);
  const [selectedId, setSelectedId] =
    useState(concepts[0]?.id ?? "");
  const [query, setQuery] = useState("");
  const [saveState, setSaveState] = useState("READY");
  const cardScroll = useMiddleMouseScroll({ axis: "y" });
  const formScroll = useMiddleMouseScroll({
    axis: "y",
    ignoreFormControls: true,
  });

  const selected =
    concepts.find((item) => item.id === selectedId) ??
    concepts[0];

  const filtered = useMemo(() => {
    const token = query.trim().toLowerCase();
    if (!token) return concepts;

    return concepts.filter((concept) =>
      [
        concept.formalName,
        concept.abbreviation,
        concept.summary,
        concept.aliases,
        concept.category,
      ]
        .join(" ")
        .toLowerCase()
        .includes(token),
    );
  }, [concepts, query]);

  function updateSelected(
    patch: Partial<CanonicalConcept>,
  ) {
    if (!selected) return;

    setConcepts((current) =>
      current.map((concept) =>
        concept.id === selected.id
          ? { ...concept, ...patch }
          : concept,
      ),
    );
    setSaveState("DIRTY");
  }

  function saveRegistry() {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(concepts),
      );
      setSaveState("SAVED");
    } catch {
      setSaveState("SAVE FAILED");
    }
  }

  function addConcept() {
    const draft = makeDraftConcept();
    setConcepts((current) => [draft, ...current]);
    setSelectedId(draft.id);
    setSaveState("DIRTY");
  }

  function removeConcept(id: string) {
    setConcepts((current) => {
      const next = current.filter(
        (concept) => concept.id !== id,
      );
      if (selectedId === id) {
        setSelectedId(next[0]?.id ?? "");
      }
      return next;
    });
    setSaveState("DIRTY");
  }

  function receiveRelay(
    envelope: VertexRelayEnvelope,
  ) {
    if (envelope.type !== "CANONICAL") {
      setSaveState("TYPE MISMATCH");
      return;
    }

    const payload = envelope.payload as Partial<CanonicalConcept>;

    if (!payload.formalName) {
      setSaveState("DRAFT INVALID");
      return;
    }

    const incomingId =
      typeof payload.id === "string" && payload.id
        ? payload.id
        : `canonical-relay-${Date.now()}`;

    const incoming: CanonicalConcept = {
      ...makeDraftConcept(),
      ...payload,
      id: incomingId,
      status:
        payload.status === "ADOPTED" ||
        payload.status === "STABLE" ||
        payload.status === "DRAFT"
          ? payload.status
          : "DRAFT",
    };

    setConcepts((current) => {
      const exists = current.some(
        (concept) => concept.id === incoming.id,
      );

      if (exists) {
        return current.map((concept) =>
          concept.id === incoming.id
            ? { ...concept, ...incoming }
            : concept,
        );
      }

      return [incoming, ...current];
    });

    setSelectedId(incoming.id);
    setSaveState("RELAY RECEIVED");
  }

  const relay = selected
    ? createVertexRelay({
        type: "CANONICAL",
        action: "SHARE",
        subjectId: selected.id,
        subjectName: selected.formalName,
        payload: selected,
      })
    : createVertexRelay({
        type: "CANONICAL",
        action: "SHARE",
        subjectId: "none",
        subjectName: "No Selection",
        payload: {},
      });

  return (
    <main className="canonical-page">
      <header className="canonical-hero">
        <div>
          <span>
            SHARED CONCEPT · LANGUAGE · SEMANTIC REGISTRY
          </span>
          <h1>
            CANONICAL <strong>REGISTRY</strong>
          </h1>
          <p>
            Vertex Worldの共通概念・用語・意味をHumanとAIで共有する。
          </p>
        </div>

        <div className="canonical-hero-meta">
          <span>REGISTRY</span>
          <strong>{concepts.length} ITEMS</strong>
          <code>
            {concepts.filter((item) => item.status === "ADOPTED").length}
            {" "}ADOPTED
          </code>
        </div>
      </header>

      <section className="canonical-grid">
        <aside className="canonical-list">
          <header>
            <div>
              <span>01 / CANONICAL INDEX</span>
              <h2>Concept Cards</h2>
            </div>

            <button
              type="button"
              className="compact-action"
              onClick={addConcept}
            >
              + NEW
            </button>
          </header>

          <div className="canonical-search">
            <input
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="名前・略称・意味で検索..."
            />
          </div>

          <div className="canonical-card-list middle-scroll-surface" {...cardScroll}>
            {filtered.map((concept) => (
              <article
                className={
                  concept.id === selectedId
                    ? "canonical-card active"
                    : "canonical-card"
                }
                key={concept.id}
              >
                <button
                  type="button"
                  className="canonical-card-main"
                  onClick={() =>
                    setSelectedId(concept.id)
                  }
                >
                  <ConceptIcon
                    category={concept.category}
                  />

                  <div>
                    <div className="canonical-card-title">
                      <strong>
                        {concept.formalName}
                      </strong>
                      <span>
                        {concept.abbreviation}
                      </span>
                    </div>

                    <p>{concept.summary}</p>

                    <div className="canonical-card-badges">
                      <span>{concept.status}</span>
                      <span>{concept.importance}</span>
                      {concept.flavorBadge ? (
                        <span>{concept.flavorBadge}</span>
                      ) : null}
                    </div>
                  </div>
                </button>

                <button
                  type="button"
                  className="canonical-card-delete"
                  aria-label={`Delete ${concept.formalName}`}
                  title="カードを削除"
                  onClick={() =>
                    removeConcept(concept.id)
                  }
                >
                  ×
                </button>
              </article>
            ))}
          </div>
        </aside>

        <section className="canonical-detail">
          {!selected ? (
            <div className="canonical-empty">
              NO CANONICAL CONCEPT
            </div>
          ) : (
            <>
              <header className="canonical-detail-header">
                <div>
                  <span>02 / CANONICAL DETAIL</span>
                  <h2>
                    {selected.formalName}
                    <em>{selected.abbreviation}</em>
                  </h2>
                  <p>{selected.summary}</p>
                </div>

                <span className="canonical-detail-status">
                  {selected.status}
                </span>
              </header>

              <div className="canonical-form middle-scroll-surface" {...formScroll}>
                <label>
                  <span>正式名称</span>
                  <input
                    value={selected.formalName}
                    onChange={(event) =>
                      updateSelected({
                        formalName: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>略称</span>
                  <input
                    value={selected.abbreviation}
                    onChange={(event) =>
                      updateSelected({
                        abbreviation: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>状態</span>
                  <select
                    value={selected.status}
                    onChange={(event) =>
                      updateSelected({
                        status:
                          event.target.value as CanonicalStatus,
                      })
                    }
                  >
                    <option>ADOPTED</option>
                    <option>STABLE</option>
                    <option>DRAFT</option>
                  </select>
                </label>

                <label>
                  <span>重要度</span>
                  <select
                    value={selected.importance}
                    onChange={(event) =>
                      updateSelected({
                        importance:
                          event.target.value as CanonicalImportance,
                      })
                    }
                  >
                    <option>CRITICAL</option>
                    <option>IMPORTANT</option>
                    <option>NORMAL</option>
                  </select>
                </label>

                <label>
                  <span>適用範囲</span>
                  <input
                    value={selected.scope}
                    onChange={(event) =>
                      updateSelected({
                        scope: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>カテゴリ</span>
                  <input
                    value={selected.category}
                    onChange={(event) =>
                      updateSelected({
                        category: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="span-2">
                  <span>概要</span>
                  <textarea
                    value={selected.summary}
                    onChange={(event) =>
                      updateSelected({
                        summary: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="span-2">
                  <span>機能</span>
                  <textarea
                    value={selected.functionText}
                    onChange={(event) =>
                      updateSelected({
                        functionText: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="span-2">
                  <span>詳細説明</span>
                  <textarea
                    value={selected.description}
                    onChange={(event) =>
                      updateSelected({
                        description: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="span-2">
                  <span>由来</span>
                  <textarea
                    value={selected.origin}
                    onChange={(event) =>
                      updateSelected({
                        origin: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>別名</span>
                  <input
                    value={selected.aliases}
                    onChange={(event) =>
                      updateSelected({
                        aliases: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>関連概念</span>
                  <input
                    value={selected.related}
                    onChange={(event) =>
                      updateSelected({
                        related: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>Flavor Badge</span>
                  <input
                    value={selected.flavorBadge}
                    onChange={(event) =>
                      updateSelected({
                        flavorBadge: event.target.value,
                      })
                    }
                  />
                </label>

                <label>
                  <span>採用者</span>
                  <input
                    value={selected.adoptedBy}
                    onChange={(event) =>
                      updateSelected({
                        adoptedBy: event.target.value,
                      })
                    }
                  />
                </label>

                <label className="span-2">
                  <span>備考</span>
                  <textarea
                    value={selected.notes}
                    onChange={(event) =>
                      updateSelected({
                        notes: event.target.value,
                      })
                    }
                  />
                </label>
              </div>

              <div className="canonical-bottom">
                <VertexRelayBar
                  envelope={relay}
                  onReceive={receiveRelay}
                />

                <div className="canonical-save">
                  <span>{saveState}</span>
                  <button
                    type="button"
                    onClick={saveRegistry}
                  >
                    SAVE
                  </button>
                </div>
              </div>
            </>
          )}
        </section>
      </section>

      <footer className="canonical-footer">
        <span>
          CANONICAL REGISTRY — HUMAN + VERA SHARED SEMANTICS
        </span>
        <span>
          NO FLOAT · SMART ACTIONS · RELAY READY
        </span>
      </footer>
    </main>
  );
}

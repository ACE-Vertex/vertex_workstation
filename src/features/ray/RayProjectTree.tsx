import { useEffect, useMemo, useRef, useState } from "react";
import { Tree, type NodeRendererProps } from "react-arborist";
import type { RayFile, RayLineFact } from "./models";
import {
  buildRayProjectTree,
  countRayTreeNodes,
  type RayTreeNode,
} from "./rayTree";

interface RayProjectTreeProps {
  readonly files: readonly RayFile[];
  readonly symbolFacts: readonly RayLineFact[];
  readonly targetIds: ReadonlySet<string>;
  readonly activeId: string | null;
  readonly locked: boolean;
  readonly onActivate: (id: string) => void;
  readonly onRevealLine: (fileId: string, line: number) => void;
  readonly onToggleTarget: (id: string) => void;
}

function useHostHeight() {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [height, setHeight] = useState(320);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    const update = () => {
      setHeight(Math.max(120, Math.floor(host.getBoundingClientRect().height)));
    };

    update();
    const observer = new ResizeObserver(update);
    observer.observe(host);
    return () => observer.disconnect();
  }, []);

  return { hostRef, height };
}

export function RayProjectTree({
  files,
  symbolFacts,
  targetIds,
  activeId,
  locked,
  onActivate,
  onRevealLine,
  onToggleTarget,
}: RayProjectTreeProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const { hostRef, height } = useHostHeight();

  const treeData = useMemo(
    () => buildRayProjectTree(files, activeId, symbolFacts),
    [files, activeId, symbolFacts],
  );

  const nodeCount = useMemo(() => countRayTreeNodes(treeData), [treeData]);

  function NodeRow({ node, style }: NodeRendererProps<RayTreeNode>) {
    const data = node.data;
    const targeted = data.fileId ? targetIds.has(data.fileId) : false;

    const activate = () => {
      if (data.kind === "folder") {
        node.toggle();
        return;
      }

      if (data.kind === "symbol" && data.fileId && data.line) {
        onRevealLine(data.fileId, data.line);
        return;
      }

      if (data.kind === "file" && data.fileId) {
        onActivate(data.fileId);
      }
    };

    return (
      <div
        style={style}
        className={`ray-arborist-row kind-${data.kind} ${
          node.isSelected ? "selected" : ""
        } ${targeted ? "targeted" : ""}`}
        onDoubleClick={activate}
      >
        <button
          type="button"
          className="ray-tree-expander"
          onClick={() => node.toggle()}
          disabled={node.isLeaf}
          aria-label={node.isOpen ? "Collapse node" : "Expand node"}
        >
          {node.isLeaf ? "·" : node.isOpen ? "▾" : "▸"}
        </button>

        {data.kind === "file" ? (
          <button
            type="button"
            className="ray-tree-target"
            onClick={(event) => {
              event.stopPropagation();
              if (data.fileId) onToggleTarget(data.fileId);
            }}
            disabled={locked}
            title={targeted ? "Remove from Target Set" : "Add to Target Set"}
          >
            {targeted ? "●" : "○"}
          </button>
        ) : (
          <span className="ray-tree-target-spacer" />
        )}

        <button
          type="button"
          className="ray-tree-node-main"
          onClick={(event) => {
            node.handleClick(event);
            if (data.kind === "folder") node.toggle();
          }}
          title={data.relativePath ?? data.name}
        >
          <span className="ray-tree-icon">
            {data.kind === "folder" ? "DIR" : data.kind === "symbol" ? "SYM" : "SRC"}
          </span>
          <span className="ray-tree-name">{data.name}</span>

          {data.kind === "symbol" ? (
            <span className="ray-tree-node-meta">
              {data.symbolKind} · L{data.line}
            </span>
          ) : data.kind === "file" ? (
            <span className="ray-tree-node-meta">
              {data.provenance} · {data.fileKind}
            </span>
          ) : null}
        </button>
      </div>
    );
  }

  return (
    <section className="ray-panel ray-tree-panel">
      <header className="ray-panel-header">
        <div>
          <span>01 / PROJECT RAY</span>
          <h2>RAY Explorer</h2>
        </div>
        <strong>{files.length} FILES · {nodeCount} NODES</strong>
      </header>

      <div className="ray-tree-toolbar">
        <label>
          <span>FILTER</span>
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="file / folder / symbol / provenance"
            spellCheck={false}
            aria-label="Filter RAY Explorer"
          />
        </label>
        <span className="ray-tree-engine">ARBORIST · VIRTUALIZED · READ ONLY</span>
      </div>

      <div className="ray-arborist-host" ref={hostRef}>
        {files.length === 0 ? (
          <div className="ray-empty">LOAD A PROJECT ROOT</div>
        ) : (
          <Tree<RayTreeNode>
            data={treeData}
            width="100%"
            height={height}
            rowHeight={30}
            indent={16}
            overscanCount={8}
            openByDefault={false}
            selection={activeId ?? undefined}
            searchTerm={searchTerm}
            searchMatch={(node, term) =>
              node.data.searchText.includes(term.trim().toLowerCase())
            }
            disableMultiSelection
            disableEdit
            disableDrag
            disableDrop
            onActivate={(node) => {
              const data = node.data;
              if (data.kind === "file" && data.fileId) {
                onActivate(data.fileId);
              } else if (data.kind === "symbol" && data.fileId && data.line) {
                onRevealLine(data.fileId, data.line);
              } else if (data.kind === "folder") {
                node.toggle();
              }
            }}
          >
            {NodeRow}
          </Tree>
        )}
      </div>
    </section>
  );
}

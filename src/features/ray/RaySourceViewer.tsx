import { useEffect, useRef } from "react";
import type { RayFile, RayFileContent } from "./models";

interface RaySourceViewerProps {
  readonly file?: RayFile;
  readonly source: RayFileContent | null;
  readonly reading: boolean;
  readonly error: string | null;
  readonly focusLine: number | null;
}

export function RaySourceViewer({
  file,
  source,
  reading,
  error,
  focusLine,
}: RaySourceViewerProps) {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const lines = source?.content.split(/\r?\n/).slice(0, 4000) ?? [];

  useEffect(() => {
    if (!focusLine || !viewportRef.current) return;
    const row = viewportRef.current.querySelector<HTMLElement>(
      `[data-ray-line="${focusLine}"]`,
    );
    row?.scrollIntoView({ block: "center", behavior: "smooth" });
  }, [focusLine, source]);

  return (
    <section className="ray-panel ray-source-panel">
      <header className="ray-panel-header">
        <div>
          <span>02 / FILE SIGHT</span>
          <h2>Source Viewer</h2>
        </div>
        <strong>
          {reading
            ? "READING"
            : source
              ? `${source.lineCount} LINES${focusLine ? ` · FOCUS L${focusLine}` : ""}`
              : "NO SOURCE"}
        </strong>
      </header>

      {!file ? (
        <div className="ray-empty">SELECT A FILE</div>
      ) : error ? (
        <div className="ray-source-message">
          <strong>FILE SIGHT ERROR</strong>
          <code>{error}</code>
        </div>
      ) : reading ? (
        <div className="ray-empty">READING {file.relativePath}</div>
      ) : !source ? (
        <div className="ray-empty">
          {file.textCandidate ? "SOURCE NOT LOADED" : "BINARY / NON-TEXT FILE"}
        </div>
      ) : (
        <div className="source-viewer" ref={viewportRef}>
          {source.truncated ? (
            <div className="source-truncated">
              PREVIEW TRUNCATED · {source.sizeBytes} BYTES TOTAL
            </div>
          ) : null}

          <ol className="source-lines">
            {lines.map((line, index) => {
              const lineNumber = index + 1;
              return (
                <li
                  key={`${lineNumber}-${line.slice(0, 16)}`}
                  data-ray-line={lineNumber}
                  className={focusLine === lineNumber ? "ray-line-focused" : ""}
                >
                  <code>{line || " "}</code>
                </li>
              );
            })}
          </ol>
        </div>
      )}
    </section>
  );
}

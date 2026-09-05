import type {
  RayFile,
  RayFileContent,
  RayLexicalFacts,
  RayMode,
} from "./models";

interface RayInspectorProps {
  readonly file?: RayFile;
  readonly source: RayFileContent | null;
  readonly facts: RayLexicalFacts;
  readonly mode: RayMode;
}

export function RayInspector({
  file,
  source,
  facts,
  mode,
}: RayInspectorProps) {
  return (
    <section className="ray-panel ray-inspector-panel">
      <header className="ray-panel-header">
        <div>
          <span>04 / RAY INSPECTOR</span>
          <h2>Inspector</h2>
        </div>
        <strong>{mode}</strong>
      </header>

      {!file ? (
        <div className="ray-empty">NO ACTIVE FILE</div>
      ) : (
        <div className="ray-inspector-body">
          <div className="inspector-fact">
            <span>PATH</span>
            <strong>{file.relativePath}</strong>
          </div>
          <div className="inspector-fact">
            <span>PROVENANCE</span>
            <strong>{file.provenance}</strong>
          </div>
          <div className="inspector-fact">
            <span>KIND</span>
            <strong>{file.kind}</strong>
          </div>
          <div className="inspector-fact">
            <span>SIZE</span>
            <strong>{file.sizeBytes} bytes</strong>
          </div>
          <div className="inspector-fact">
            <span>CONTENT</span>
            <strong>
              {source
                ? `${source.lineCount} lines / ${source.encoding}${source.truncated ? " / truncated" : ""}`
                : file.textCandidate
                  ? "not loaded"
                  : "binary / non-text"}
            </strong>
          </div>

          <div className="symbol-block">
            <span>SYMBOL SIGHT</span>
            <div>
              {facts.symbols.length
                ? facts.symbols.slice(0, 24).map((symbol) => (
                    <code key={symbol}>{symbol}</code>
                  ))
                : <small>NO SYMBOLS DETECTED</small>}
            </div>
          </div>

          <div className="import-block">
            <span>DEPENDENCY CLUES</span>
            <div>
              {facts.imports.length
                ? facts.imports.slice(0, 14).map((entry) => (
                    <code key={entry}>{entry}</code>
                  ))
                : <small>NO IMPORT / USE / MOD CLUES</small>}
            </div>
          </div>

          <div className="ownership-matrix">
            <span>OWNERSHIP LENSES</span>
            <div className="ownership-grid">
              <b>Visual Parent</b><em>presentation</em>
              <b>Logical Owner</b><em>deterministic pass pending</em>
              <b>State Owner</b><em>deterministic pass pending</em>
              <b>Service Owner</b><em>deterministic pass pending</em>
              <b>Style Owner</b><em>deterministic pass pending</em>
              <b>Layout Slot</b><em>presentation</em>
              <b>Event Owner</b><em>{facts.eventBindingCount} lexical clue(s)</em>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

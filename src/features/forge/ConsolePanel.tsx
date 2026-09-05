interface ConsolePanelProps {
  readonly eyebrow: string;
  readonly title: string;
  readonly badge?: string;
  readonly lines: readonly string[];
}

export function ConsolePanel({
  eyebrow,
  title,
  badge,
  lines,
}: ConsolePanelProps) {
  return (
    <section className="forge-panel console-panel">
      <header className="panel-header">
        <div>
          <span>{eyebrow}</span>
          <div className="console-title-line">
            <h2>{title}</h2>
            {badge ? <em>{badge}</em> : null}
          </div>
        </div>
        <button type="button">CLEAR</button>
      </header>

      <pre className="console-body">
        {lines.join("\n")}
      </pre>
    </section>
  );
}

import { useEffect, useMemo, useState } from "react";

export interface OperationIndicatorProps {
  readonly active: boolean;
  readonly system: string;
  readonly phase: string;
  readonly detail?: string;
  readonly startedAt?: number | null;
  readonly readyLabel?: string;
}

function formatElapsed(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const seconds = (totalSeconds % 60).toString().padStart(2, "0");
  return `${minutes}:${seconds}`;
}

export function OperationIndicator({
  active,
  system,
  phase,
  detail,
  startedAt,
  readyLabel = "READY",
}: OperationIndicatorProps) {
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (!active) return;
    setNow(Date.now());
    const timer = window.setInterval(() => setNow(Date.now()), 250);
    return () => window.clearInterval(timer);
  }, [active, startedAt]);

  const elapsed = useMemo(
    () => (active && startedAt ? formatElapsed(now - startedAt) : "00:00"),
    [active, now, startedAt],
  );

  return (
    <section
      className={`operation-indicator ${active ? "active" : "idle"}`}
      role="status"
      aria-live="polite"
      aria-label={`${system} ${active ? phase : readyLabel}`}
    >
      <div className="operation-orbit" aria-hidden="true">
        <span className="operation-orbit-ring outer" />
        <span className="operation-orbit-ring inner" />
        <span className="operation-orbit-core" />
      </div>

      <div className="operation-copy">
        <span>{system}</span>
        <strong>{active ? phase : readyLabel}</strong>
        {detail ? <small>{detail}</small> : null}
      </div>

      <div className="operation-motion" aria-hidden="true">
        <span />
      </div>

      <time className="operation-timer">{active ? elapsed : "READY"}</time>
    </section>
  );
}

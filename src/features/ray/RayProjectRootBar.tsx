interface RayProjectRootBarProps {
  readonly draft: string;
  readonly recentRoots: readonly string[];
  readonly busy: boolean;
  readonly onDraftChange: (value: string) => void;
  readonly onLoad: () => void;
  readonly onBrowse: () => void;
  readonly onRecent: (value: string) => void;
}

export function RayProjectRootBar({
  draft,
  recentRoots,
  busy,
  onDraftChange,
  onLoad,
  onBrowse,
  onRecent,
}: RayProjectRootBarProps) {
  return (
    <section className="ray-project-root-bar">
      <div className="root-input-block">
        <span>PROJECT ROOT</span>
        <input
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          spellCheck={false}
          disabled={busy}
          aria-label="RAY project root"
        />
      </div>

      <button type="button" onClick={onLoad} disabled={busy || draft.trim().length === 0}>
        LOAD ROOT
      </button>
      <button type="button" onClick={onBrowse} disabled={busy}>
        BROWSE
      </button>

      <label className="recent-root-select">
        <span>RECENT</span>
        <select
          value=""
          onChange={(event) => {
            if (event.target.value) onRecent(event.target.value);
          }}
          disabled={busy || recentRoots.length === 0}
        >
          <option value="">SELECT ROOT</option>
          {recentRoots.map((root) => (
            <option value={root} key={root}>
              {root}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}

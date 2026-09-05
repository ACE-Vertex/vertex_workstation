interface PathSwitcherProps {
  readonly label: string;
  readonly value: string;
  readonly options: readonly string[];
  readonly disabled?: boolean;
  readonly onChange: (next: string) => void;
  readonly onCommit?: () => void;
  readonly onBrowse?: () => void;
}

export function PathSwitcher({
  label,
  value,
  options,
  disabled = false,
  onChange,
  onCommit,
  onBrowse,
}: PathSwitcherProps) {
  const listId = `${label.replaceAll(" ", "-").toLowerCase()}-options`;

  return (
    <div className="path-switcher">
      <div className="path-switcher-heading">
        <span className="path-switcher-label">{label}</span>
        {onBrowse ? (
          <button type="button" onClick={onBrowse} disabled={disabled}>
            BROWSE
          </button>
        ) : null}
      </div>

      <input
        list={listId}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onBlur={onCommit}
        onKeyDown={(event) => {
          if (event.key === "Enter") onCommit?.();
        }}
        spellCheck={false}
        aria-label={label}
        disabled={disabled}
      />

      <datalist id={listId}>
        {options.map((option) => (
          <option value={option} key={option} />
        ))}
      </datalist>
    </div>
  );
}

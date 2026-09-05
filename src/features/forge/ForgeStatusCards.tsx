interface ForgeStatusCardsProps {
  readonly receiving: number;
  readonly ready: number;
  readonly verified: number;
  readonly attention: number;
}

const Card = ({
  label,
  value,
  hint,
}: {
  label: string;
  value: number;
  hint: string;
}) => (
  <div className="status-card">
    <span>{label}</span>
    <strong>{value}</strong>
    <small>{hint}</small>
  </div>
);

export function ForgeStatusCards({
  receiving,
  ready,
  verified,
  attention,
}: ForgeStatusCardsProps) {
  return (
    <div className="status-cards">
      <Card label="RECEIVING" value={receiving} hint="incoming artifacts" />
      <Card label="READY" value={ready} hint="validated / waiting" />
      <Card label="VERIFIED" value={verified} hint="completed artifacts" />
      <Card label="ATTENTION" value={attention} hint="invalid / verify failed" />
    </div>
  );
}

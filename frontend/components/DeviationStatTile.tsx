export function DeviationStatTile({ deviationMw }: { deviationMw: number }) {
  const isUp = deviationMw >= 0;
  const color = isUp ? "var(--diverging-up)" : "var(--diverging-down)";
  const arrow = isUp ? "▲" : "▼";

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <p className="text-xs" style={{ color: "var(--text-muted)" }}>
        vs. same hour last week
      </p>
      <p className="mt-1 flex items-center gap-1.5 text-2xl font-semibold">
        <span style={{ color }}>{arrow}</span>
        <span style={{ color: "var(--text-primary)" }}>
          {Math.round(Math.abs(deviationMw)).toLocaleString()} MW
        </span>
      </p>
      <p className="mt-1 text-xs" style={{ color: "var(--text-secondary)" }}>
        {isUp ? "Higher" : "Lower"} than the same hour one week prior
      </p>
    </div>
  );
}

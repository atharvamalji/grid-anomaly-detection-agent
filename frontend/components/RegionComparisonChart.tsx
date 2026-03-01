"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { AnomalyExplanation } from "@/lib/api";
import { useDarkMode } from "@/lib/useDarkMode";
import { categoricalColor } from "@/lib/colors";

interface RegionRow {
  region: string;
  count: number;
  avgSeverity: number;
}

function TooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: RegionRow }[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const row = payload[0].payload;

  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-sm"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
        {row.count} {row.count === 1 ? "anomaly" : "anomalies"}
      </p>
      <p style={{ color: "var(--text-secondary)" }}>{row.region}</p>
      <p style={{ color: "var(--text-secondary)" }}>
        avg severity {row.avgSeverity.toFixed(4)}
      </p>
    </div>
  );
}

export function RegionComparisonChart({ anomalies }: { anomalies: AnomalyExplanation[] }) {
  const isDark = useDarkMode();
  const byRegion = new Map<string, { count: number; severitySum: number }>();
  for (const a of anomalies) {
    const entry = byRegion.get(a.region) ?? { count: 0, severitySum: 0 };
    entry.count += 1;
    entry.severitySum += a.severity_score;
    byRegion.set(a.region, entry);
  }

  // Stable alphabetical order for color assignment — color follows the region
  // identity, never its rank in the (count-sorted) display order.
  const stableRegionOrder = Array.from(byRegion.keys()).sort();

  const data: RegionRow[] = Array.from(byRegion.entries())
    .map(([region, { count, severitySum }]) => ({
      region,
      count,
      avgSeverity: severitySum / count,
    }))
    .sort((a, b) => b.count - a.count);

  if (data.length <= 1) {
    return null;
  }

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <h2 className="mb-3 text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
        Anomalies by region
      </h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--gridline)" strokeDasharray="0" vertical={false} />
          <XAxis
            dataKey="region"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
            width={32}
          />
          <Tooltip content={<TooltipContent />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} maxBarSize={48}>
            {data.map((row) => (
              <Cell
                key={row.region}
                fill={categoricalColor(stableRegionOrder.indexOf(row.region), isDark)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnomalyExplanation } from "@/lib/api";

interface DayCount {
  date: string;
  count: number;
}

function toDayKey(timestamp: string): string {
  return timestamp.slice(0, 10);
}

function formatDayLabel(dayKey: string): string {
  const [, month, day] = dayKey.split("-");
  return `${month}/${day}`;
}

function TooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: DayCount }[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload;

  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-sm"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
        {point.count} {point.count === 1 ? "anomaly" : "anomalies"}
      </p>
      <p style={{ color: "var(--text-secondary)" }}>{point.date}</p>
    </div>
  );
}

export function AnomalyCountBarChart({ anomalies }: { anomalies: AnomalyExplanation[] }) {
  const counts = new Map<string, number>();
  for (const a of anomalies) {
    const key = toDayKey(a.timestamp);
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }

  const data: DayCount[] = Array.from(counts.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, count]) => ({ date, count }));

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <h2 className="mb-3 text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
        Anomalies per day
      </h2>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--gridline)" strokeDasharray="0" vertical={false} />
          <XAxis
            dataKey="date"
            tickFormatter={formatDayLabel}
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
          <Bar
            dataKey="count"
            fill="var(--series-accent)"
            radius={[4, 4, 0, 0]}
            maxBarSize={24}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Row {
  label: string;
  value: number;
  isActual: boolean;
}

function TooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: Row }[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const row = payload[0].payload;

  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-sm"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
        {Math.round(row.value).toLocaleString()} MW
      </p>
      <p style={{ color: "var(--text-secondary)" }}>{row.label}</p>
    </div>
  );
}

export function FeatureComparisonChart({
  actualValue,
  rollingMean,
}: {
  actualValue: number;
  rollingMean: number;
}) {
  const data: Row[] = [
    { label: "Actual demand", value: actualValue, isActual: true },
    { label: "Rolling 24h mean", value: rollingMean, isActual: false },
  ];

  return (
    <div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={data} layout="vertical" margin={{ top: 0, right: 24, bottom: 0, left: 8 }}>
          <CartesianGrid stroke="var(--gridline)" strokeDasharray="0" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: "var(--text-secondary)", fontSize: 12 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
            width={120}
          />
          <Tooltip content={<TooltipContent />} cursor={{ fill: "var(--gridline)", opacity: 0.4 }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
            {data.map((row) => (
              <Cell
                key={row.label}
                fill={row.isActual ? "var(--series-accent)" : "var(--series-context)"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

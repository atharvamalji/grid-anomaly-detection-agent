"use client";

import { useMemo } from "react";
import {
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnomalyExplanation } from "@/lib/api";
import { severityColor } from "@/lib/colors";
import { useDarkMode } from "@/lib/useDarkMode";

// Rendering every flagged anomaly as an SVG circle degrades badly past a few
// hundred points (each with its own hit-test + custom shape render). Cap to
// the highest-severity subset, which is also the most interesting to look at.
const MAX_POINTS = 200;

interface Point {
  x: number;
  y: number;
  region: string;
  timestampLabel: string;
  anomalyType: string | null;
  demandValue: number | null;
}

function formatDate(ms: number): string {
  return new Date(ms).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function TooltipContent({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: Point }[];
}) {
  if (!active || !payload || payload.length === 0) return null;
  const point = payload[0].payload;

  return (
    <div
      className="rounded-md border px-3 py-2 text-xs shadow-sm"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <p className="font-semibold" style={{ color: "var(--text-primary)" }}>
        severity {point.y.toFixed(4)}
      </p>
      <p style={{ color: "var(--text-secondary)" }}>{point.timestampLabel}</p>
      <p style={{ color: "var(--text-secondary)" }}>
        {point.region}
        {point.anomalyType ? ` · ${point.anomalyType}` : ""}
      </p>
      {point.demandValue != null && (
        <p style={{ color: "var(--text-secondary)" }}>
          demand {Math.round(point.demandValue).toLocaleString()} MW
        </p>
      )}
    </div>
  );
}

export function SeverityScatterChart({ anomalies }: { anomalies: AnomalyExplanation[] }) {
  const isDark = useDarkMode();

  const { points, maxSeverity, truncated } = useMemo(() => {
    const sorted = [...anomalies].sort((a, b) => b.severity_score - a.severity_score);
    const capped = sorted.slice(0, MAX_POINTS);
    const pts: Point[] = capped.map((a) => ({
      x: new Date(a.timestamp).getTime(),
      y: a.severity_score,
      region: a.region,
      timestampLabel: a.timestamp,
      anomalyType: a.anomaly_type,
      demandValue: a.contributing_features.value ?? null,
    }));
    return {
      points: pts,
      maxSeverity: Math.max(...pts.map((p) => p.y), 0.0001),
      truncated: anomalies.length > capped.length,
    };
  }, [anomalies]);

  const dotColors = useMemo(
    () => points.map((p) => severityColor(p.y, maxSeverity, isDark)),
    [points, maxSeverity, isDark],
  );

  return (
    <div
      className="rounded-lg border p-4"
      style={{ borderColor: "var(--gridline)", backgroundColor: "var(--chart-surface)" }}
    >
      <div className="mb-3 flex items-baseline justify-between">
        <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
          Severity over time
        </h2>
        {truncated && (
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            top {points.length} of {anomalies.length}
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
          <CartesianGrid stroke="var(--gridline)" strokeDasharray="0" vertical={false} />
          <XAxis
            dataKey="x"
            type="number"
            domain={["dataMin", "dataMax"]}
            tickFormatter={formatDate}
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
          />
          <YAxis
            dataKey="y"
            type="number"
            tick={{ fill: "var(--text-muted)", fontSize: 11 }}
            axisLine={{ stroke: "var(--baseline-axis)" }}
            tickLine={false}
            width={48}
          />
          <Tooltip content={<TooltipContent />} cursor={{ stroke: "var(--gridline)" }} />
          <Scatter
            data={points}
            shape={(props: unknown) => {
              const p = props as { cx: number; cy: number; index: number };
              return (
                <circle
                  cx={p.cx}
                  cy={p.cy}
                  r={5}
                  fill={dotColors[p.index]}
                  stroke="var(--chart-surface)"
                  strokeWidth={2}
                />
              );
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

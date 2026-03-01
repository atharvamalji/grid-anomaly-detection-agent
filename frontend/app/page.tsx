import { getRecentAnomalies } from "@/lib/api";
import { StatTile } from "@/components/StatTile";
import { SeverityScatterChart } from "@/components/SeverityScatterChart";
import { AnomalyCountBarChart } from "@/components/AnomalyCountBarChart";
import { RegionComparisonChart } from "@/components/RegionComparisonChart";
import { AnomalyTable } from "@/components/AnomalyTable";

export default async function Home() {
  let anomalies: Awaited<ReturnType<typeof getRecentAnomalies>> = [];
  let error: string | null = null;

  try {
    anomalies = await getRecentAnomalies(1000);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  return (
    <div
      className="min-h-screen px-6 py-10 sm:px-10"
      style={{ backgroundColor: "var(--background)" }}
    >
      <main className="mx-auto max-w-7xl">
        <header className="mb-8">
          <h1
            className="text-2xl font-semibold"
            style={{ color: "var(--text-primary)" }}
          >
            Grid Anomaly Detection Agent
          </h1>
          <p
            className="mt-1 text-sm"
            style={{ color: "var(--text-secondary)" }}
          >
            Recently flagged anomalies with agent-generated explanations. This
            is a portfolio/demo project — explanations are hypotheses for human
            review, not autonomous decisions.
          </p>
        </header>

        {error && (
          <div
            className="mb-6 rounded-lg border p-4 text-sm"
            style={{
              borderColor: "var(--diverging-up)",
              backgroundColor: "var(--diverging-mid)",
              color: "var(--text-primary)",
            }}
          >
            Could not load anomalies from the backend API: {error}
          </div>
        )}

        {!error && anomalies.length === 0 && (
          <div
            className="rounded-lg border p-6 text-sm"
            style={{
              borderColor: "var(--gridline)",
              backgroundColor: "var(--chart-surface)",
              color: "var(--text-secondary)",
            }}
          >
            No anomalies recorded yet. Run <code>POST /analyze</code> against
            the backend to detect and explain anomalies for a time window.
          </div>
        )}

        {!error && anomalies.length > 0 && (
          <>
            <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <StatTile
                label="Flagged anomalies"
                value={String(anomalies.length)}
              />
              <StatTile
                label="Peak severity"
                value={Math.max(
                  ...anomalies.map((a) => a.severity_score),
                ).toFixed(3)}
              />
              <StatTile
                label="Average severity"
                value={(
                  anomalies.reduce((sum, a) => sum + a.severity_score, 0) /
                  anomalies.length
                ).toFixed(3)}
              />
              <StatTile
                label="Regions monitored"
                value={String(new Set(anomalies.map((a) => a.region)).size)}
              />
            </div>

            <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
              <SeverityScatterChart anomalies={anomalies} />
              <AnomalyCountBarChart anomalies={anomalies} />
            </div>

            <div className="mb-6">
              <RegionComparisonChart anomalies={anomalies} />
            </div>
          </>
        )}

        {!error && anomalies.length > 0 && (
          <AnomalyTable anomalies={anomalies} />
        )}
      </main>
    </div>
  );
}

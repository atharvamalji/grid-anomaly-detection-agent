import Link from "next/link";
import { getRecentAnomalies } from "@/lib/api";

function severityBadgeClass(score: number): string {
  if (score >= 0.03) return "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300";
  if (score >= 0.015) return "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300";
  return "bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-300";
}

export default async function Home() {
  let anomalies: Awaited<ReturnType<typeof getRecentAnomalies>> = [];
  let error: string | null = null;

  try {
    anomalies = await getRecentAnomalies(50);
  } catch (e) {
    error = e instanceof Error ? e.message : String(e);
  }

  return (
    <div className="min-h-screen bg-zinc-50 px-6 py-10 dark:bg-black sm:px-10">
      <main className="mx-auto max-w-4xl">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-zinc-950 dark:text-zinc-50">
            Grid Anomaly Detection Agent
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Recently flagged anomalies with agent-generated explanations. This is a
            portfolio/demo project — explanations are hypotheses for human review, not
            autonomous decisions.
          </p>
        </header>

        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            Could not load anomalies from the backend API: {error}
          </div>
        )}

        {!error && anomalies.length === 0 && (
          <div className="rounded-lg border border-zinc-200 bg-white p-6 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
            No anomalies recorded yet. Run <code>POST /analyze</code> against the backend
            to detect and explain anomalies for a time window.
          </div>
        )}

        <ul className="space-y-3">
          {anomalies.map((anomaly) => (
            <li key={anomaly.id ?? `${anomaly.timestamp}-${anomaly.region}`}>
              <Link
                href={anomaly.id != null ? `/anomalies/${anomaly.id}` : "#"}
                className="block rounded-lg border border-zinc-200 bg-white p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-700"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium text-zinc-950 dark:text-zinc-50">
                      {anomaly.region} — {anomaly.timestamp}
                    </p>
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                      {anomaly.anomaly_type ?? "Anomaly"}
                      {anomaly.explanation ? `: ${anomaly.explanation.slice(0, 120)}${anomaly.explanation.length > 120 ? "…" : ""}` : ""}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${severityBadgeClass(anomaly.severity_score)}`}
                  >
                    {anomaly.severity_score.toFixed(3)}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

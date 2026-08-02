const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export interface AnomalyExplanation {
  id: number | null;
  timestamp: string;
  region: string;
  severity_score: number;
  anomaly_type: string | null;
  explanation: string | null;
  recommendation: string | null;
  citations: string[];
  contributing_features: Record<string, number>;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API request to ${path} failed (${res.status}): ${body}`);
  }
  return res.json() as Promise<T>;
}

export function getRecentAnomalies(limit = 20): Promise<AnomalyExplanation[]> {
  return apiFetch<AnomalyExplanation[]>(`/anomalies/recent?limit=${limit}`);
}

export function getAnomalyById(id: number): Promise<AnomalyExplanation> {
  return apiFetch<AnomalyExplanation>(`/anomalies/${id}`);
}

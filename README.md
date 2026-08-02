# Grid Anomaly Detection Agent

An agentic pipeline that ingests hourly electric grid load data (EIA-930,
MISO), detects anomalies with a classical ML model, and uses an LLM agent
to explain likely causes and recommend actions — citing grid reliability
documentation via RAG. Exposed as a REST API (gRPC as a stretch goal),
with a Next.js dashboard and read-only export for BI tools (Power BI /
Tableau).

## Safety framing (read before anything else)

- This is a **portfolio/demo project**, not a production grid-monitoring
  tool.
- The LLM's explanations are **hypotheses for human review**, not
  autonomous decisions — the agent never takes action, only recommends.
- **No real operational or non-public data is used.** All data is public
  (EIA-930 API, public NERC/MISO/FERC documents).

## Project structure

- `backend/` — Python pipeline: ingestion, feature engineering, anomaly
  detection (Isolation Forest / stretch LSTM autoencoder), RAG, LangGraph
  agent, FastAPI API.
- `frontend/` — Next.js dashboard for investigating flagged anomalies and
  agent explanations.
- `bi_export/` — notes on the read-only DB view used by Power BI / Tableau.
- `grpc/`, `k8s/` — stretch goals, currently deferred (see `spec.txt` §7).
- `spec.txt` — full project spec.

See `spec.txt` for architecture, milestones, and extension ideas.

## Development

See `Makefile` for common tasks (`make dev`, `make test`, `make lint`,
`make docker-up`). Setup instructions will be filled in as each component
is implemented.

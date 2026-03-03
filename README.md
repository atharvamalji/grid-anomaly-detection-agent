# Grid Anomaly Detection Agent

An agentic pipeline that ingests hourly electric grid load data (EIA-930,
MISO/PJM/SPP), detects anomalies with a classical ML model, and uses an LLM
agent — enriched with real historical weather data — to explain likely
causes and recommend actions, citing real MISO/NERC reliability
documentation via RAG. Exposed as a REST API with a Next.js dashboard.

## Safety framing (read before anything else)

- This is a **portfolio/demo project**, not a production grid-monitoring
  tool.
- The LLM's explanations are **hypotheses for human review**, not
  autonomous decisions — the agent never takes action, only recommends.
- **No real operational or non-public data is used.** All data is public
  (EIA-930 API, public NERC/MISO/FERC documents).

## Project structure

- `backend/` — Python pipeline: ingestion, feature engineering, anomaly
  detection (Isolation Forest / stretch LSTM autoencoder), RAG, weather
  enrichment, LangGraph agent, FastAPI API.
- `frontend/` — Next.js dashboard for investigating flagged anomalies and
  agent explanations.
- `spec.txt` — full project spec.

gRPC, Kubernetes, and BI-tool export were considered as stretch goals (see
`spec.txt` §7/§8) but have been dropped from scope in favor of solidifying
the core pipeline (test coverage, CI, Docker verification).

See `spec.txt` for architecture, milestones, and extension ideas.

## Development

See `Makefile` for common tasks (`make dev`, `make test`, `make lint`,
`make docker-up`). Setup instructions will be filled in as each component
is implemented.

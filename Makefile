.PHONY: dev backend-dev frontend-dev ingest train test lint docker-up docker-down

dev: ## Run backend + frontend together (placeholder until both exist)
	@echo "TODO: run backend-dev and frontend-dev concurrently"

backend-dev: ## Run the FastAPI backend locally
	@echo "TODO: uvicorn grid_agent.api.main:app --reload (backend/)"

frontend-dev: ## Run the Next.js dashboard locally
	@echo "TODO: npm run dev (frontend/)"

ingest: ## Pull latest hourly demand data from EIA-930
	@echo "TODO: python -m grid_agent.ingestion.pull (backend/)"

train: ## Train/refresh the anomaly detector
	@echo "TODO: python -m grid_agent.models.train (backend/)"

test: ## Run backend + frontend test suites
	@echo "TODO: pytest (backend/), npm test (frontend/)"

lint: ## Lint backend + frontend
	@echo "TODO: ruff/mypy (backend/), eslint (frontend/)"

docker-up: ## Bring up local stack (Postgres, API, ...)
	docker-compose up --build

docker-down: ## Tear down local stack
	docker-compose down

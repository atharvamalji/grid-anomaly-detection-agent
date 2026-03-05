.PHONY: dev backend-dev frontend-dev ingest train test lint docker-up docker-down

dev: ## Run backend + frontend together
	@echo "Run 'make backend-dev' and 'make frontend-dev' in separate terminals."

backend-dev: ## Run the FastAPI backend locally
	cd backend && . .venv/bin/activate && uvicorn grid_agent.api.main:app --reload

frontend-dev: ## Run the Next.js dashboard locally
	cd frontend && npm run dev

ingest: ## Pull latest hourly demand data from EIA-930
	cd backend && . .venv/bin/activate && python -m grid_agent.ingestion.pull

train: ## Train/refresh the anomaly detector
	cd backend && . .venv/bin/activate && python -m grid_agent.models.train

test: ## Run backend test suite
	cd backend && . .venv/bin/activate && pytest -v

lint: ## Lint backend + frontend
	cd backend && . .venv/bin/activate && ruff check .
	cd frontend && npm run lint

docker-up: ## Bring up local stack (backend + frontend)
	docker compose up --build

docker-down: ## Tear down local stack
	docker compose down

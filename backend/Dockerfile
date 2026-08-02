FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY grid_agent ./grid_agent

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "grid_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]

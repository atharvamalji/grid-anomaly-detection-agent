import logging

import pandas as pd
from fastapi import FastAPI, HTTPException

from grid_agent.agent import analyze_anomaly
from grid_agent.db import get_anomaly_by_id, get_connection, get_recent_anomalies, insert_anomaly
from grid_agent.features import clean_and_resample, engineer_features
from grid_agent.ingestion.pull import RAW_DATA_DIR, pull_and_store
from grid_agent.models import AnomalyDetector
from grid_agent.rag import RagIndex

from .schemas import AnalyzeRequest, AnalyzeResponse, AnomalyExplanation

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Grid Anomaly Detection Agent",
    description=(
        "Portfolio/demo project. LLM explanations are hypotheses for human "
        "review, not autonomous decisions — this agent never takes action, "
        "only recommends. No real operational or non-public data is used."
    ),
)

_rag_index: RagIndex | None = None


def _get_rag_index() -> RagIndex:
    global _rag_index
    if _rag_index is None:
        _rag_index = RagIndex()
        _rag_index.load()
    return _rag_index


def _load_or_pull(respondent: str, start: str, end: str) -> pd.DataFrame:
    expected_path = RAW_DATA_DIR / f"{respondent}_{start}_{end}.parquet"
    if expected_path.exists():
        return pd.read_parquet(expected_path)
    path = pull_and_store(respondent, start, end)
    return pd.read_parquet(path)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        raw = _load_or_pull(request.respondent, request.start, request.end)
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    features = engineer_features(clean_and_resample(raw))

    detector = AnomalyDetector()
    try:
        detector.load()
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail="Anomaly detector model not found — train it first (grid_agent.models.train).",
        ) from e

    results = detector.predict(features)
    flagged = [r for r in results if r.is_anomaly]

    rag_index = _get_rag_index()
    conn = get_connection()
    explanations: list[AnomalyExplanation] = []
    try:
        for anomaly in flagged:
            try:
                state = analyze_anomaly(anomaly, rag_index=rag_index)
            except Exception:
                logger.exception("Agent analysis failed for anomaly at %s", anomaly.timestamp)
                state = {}

            explanation = AnomalyExplanation(
                timestamp=str(anomaly.timestamp),
                region=anomaly.region,
                severity_score=anomaly.severity_score,
                anomaly_type=state.get("anomaly_type"),
                explanation=state.get("explanation"),
                recommendation=state.get("recommendation"),
                citations=state.get("citations", []),
                contributing_features=anomaly.contributing_features,
            )
            explanation.id = insert_anomaly(
                conn,
                timestamp=explanation.timestamp,
                region=explanation.region,
                severity_score=explanation.severity_score,
                anomaly_type=explanation.anomaly_type,
                explanation=explanation.explanation,
                recommendation=explanation.recommendation,
                citations=explanation.citations,
                contributing_features=explanation.contributing_features,
            )
            explanations.append(explanation)
    finally:
        conn.close()

    return AnalyzeResponse(
        respondent=request.respondent,
        start=request.start,
        end=request.end,
        hours_scored=len(results),
        anomalies=explanations,
    )


def _row_to_explanation(row: dict) -> AnomalyExplanation:
    return AnomalyExplanation(
        id=row["id"],
        timestamp=row["timestamp"],
        region=row["region"],
        severity_score=row["severity_score"],
        anomaly_type=row["anomaly_type"],
        explanation=row["explanation"],
        recommendation=row["recommendation"],
        citations=row["citations"],
        contributing_features=row["contributing_features"],
    )


@app.get("/anomalies/recent", response_model=list[AnomalyExplanation])
def anomalies_recent(limit: int = 20) -> list[AnomalyExplanation]:
    rows = get_recent_anomalies(limit=limit)
    return [_row_to_explanation(row) for row in rows]


@app.get("/anomalies/{anomaly_id}", response_model=AnomalyExplanation)
def anomaly_detail(anomaly_id: int) -> AnomalyExplanation:
    row = get_anomaly_by_id(anomaly_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Anomaly {anomaly_id} not found")
    return _row_to_explanation(row)

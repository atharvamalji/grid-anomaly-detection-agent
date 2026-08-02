from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    respondent: str = "MISO"
    start: str  # ISO date-hour, e.g. "2025-12-01T00"
    end: str  # ISO date-hour, e.g. "2025-12-31T23"


class AnomalyExplanation(BaseModel):
    id: int | None = None
    timestamp: str
    region: str
    severity_score: float
    anomaly_type: str | None = None
    explanation: str | None = None
    recommendation: str | None = None
    citations: list[str] = []
    contributing_features: dict[str, float] = {}


class AnalyzeResponse(BaseModel):
    respondent: str
    start: str
    end: str
    hours_scored: int
    anomalies: list[AnomalyExplanation]

from typing import TypedDict

from grid_agent.rag import RetrievedChunk


class AnomalyInput(TypedDict):
    timestamp: str
    region: str
    severity_score: float
    contributing_features: dict[str, float]


class AgentState(TypedDict, total=False):
    anomaly: AnomalyInput
    anomaly_type: str
    retrieved_chunks: list[RetrievedChunk]
    explanation: str
    recommendation: str
    citations: list[str]

from fastapi.testclient import TestClient

from grid_agent.api.main import app

client = TestClient(app)


def test_anomalies_recent_returns_200_and_a_list():
    response = client.get("/anomalies/recent?limit=5")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_anomaly_detail_404_for_unknown_id():
    response = client.get("/anomalies/999999999")
    assert response.status_code == 404


def test_analyze_rejects_missing_required_fields():
    # start/end are required; omitting them should fail request validation
    # before ever touching the model, RAG index, or an LLM provider.
    response = client.post("/analyze", json={"respondent": "MISO"})
    assert response.status_code == 422

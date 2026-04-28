from fastapi.testclient import TestClient

from contract_risk_analyzer.api.main import app


def test_health(monkeypatch) -> None:
    monkeypatch.setenv("CONTRACT_RISK_MOCK_MODEL", "true")
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_clause_mock_mode(monkeypatch) -> None:
    monkeypatch.setenv("CONTRACT_RISK_MOCK_MODEL", "true")
    client = TestClient(app)
    response = client.post("/analyze/clause", json={"text": "Either party may terminate without cause."})
    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_label"] == "termination"
    assert payload["risk_flags"]


def test_analyze_document_mock_mode(monkeypatch) -> None:
    monkeypatch.setenv("CONTRACT_RISK_MOCK_MODEL", "true")
    client = TestClient(app)
    response = client.post(
        "/analyze/document",
        json={"document_id": "d1", "text": "1. Termination. Either party may terminate. 2. Payment. Customer shall pay invoices."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_clauses"] >= 1
    assert "not legal advice" in payload["disclaimer"].lower()

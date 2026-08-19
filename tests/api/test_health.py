from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/v1/health")

    assert response.status_code == 200


def test_health_status_is_ok():
    response = client.get("/api/v1/health")

    assert response.json()["status"] == "ok"


def test_health_has_all_10_tables():
    response = client.get("/api/v1/health")

    counts = response.json()["db_row_counts"]

    expected_tables = {
        "companies",
        "sectors",
        "peer_groups",
        "analysis",
        "prosandcons",
        "documents",
        "profitandloss",
        "balancesheet",
        "cashflow",
        "financial_ratios",
    }

    assert set(counts.keys()) == expected_tables

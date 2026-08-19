from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_screener_min_roe():
    response = client.get("/api/v1/screener", params={"min_roe": 15})

    assert response.status_code == 200

    data = response.json()

    companies = data.get("companies", data)

    for company in companies:
        roe = company.get("roe_pct")

        if roe is not None:
            assert roe >= 15


def test_screener_invalid_parameter_returns_400():
    response = client.get("/api/v1/screener", params={"min_roe": "invalid"})

    assert response.status_code == 400

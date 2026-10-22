import pytest
from fastapi.testclient import TestClient
from src.api.server import app

client = TestClient(app)

def test_portfolio_quotes_empty():
    res = client.post("/api/portfolio/quotes", json={"tickers": []})
    assert res.status_code == 200
    data = res.json()
    assert "quotes" in data
    assert data["quotes"] == {}

def test_portfolio_quotes_mock():
    # Test with tickers
    res = client.post("/api/portfolio/quotes", json={"tickers": ["PETR4", "VALE3"]})
    assert res.status_code == 200
    data = res.json()
    assert "quotes" in data

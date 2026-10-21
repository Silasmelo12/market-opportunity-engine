"""
Tests for radar pagination, caching, filters, and fault-tolerance.
"""

from fastapi.testclient import TestClient
from src.api.server import app
from src.api.cache import DailyCache
import pytest


client = TestClient(app)


def test_radar_endpoint_pagination():
    # Page 1 with page_size=5
    response = client.get("/api/radar?category=featured&page=1&page_size=5&direction=BUY")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total_assets"] >= 5
    assert data["total_pages"] >= 1
    assert data["direction"] == "BUY"


def test_radar_endpoint_out_of_range_page():
    response = client.get("/api/radar?category=featured&page=9999&page_size=20")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["page"] == 9999


def test_radar_endpoint_direction_filter():
    # Only SELL
    response = client.get("/api/radar?category=featured&page=1&page_size=10&direction=SELL")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["direction"] == "SELL"


def test_radar_cache_resilience(monkeypatch):
    # Set an invalid REDIS_URL to verify that DailyCache doesn't crash
    monkeypatch.setenv("REDIS_URL", "redis://invalid-host-99999.xyz:6379/0")
    cache = DailyCache()
    assert cache.backend == "disk"
    cache.set("foo", {"msg": "hello"})
    assert cache.get("foo") == {"msg": "hello"}


def test_health_check_backend():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cache_backend" in data

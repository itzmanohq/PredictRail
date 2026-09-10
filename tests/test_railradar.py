"""
Unit and Integration Tests for RailRadar Live Train Running Status Module.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.railradar_client import RailRadarClient, railradar_client
from backend.services import service_get_live_train_status

client = TestClient(app)


def test_railradar_client_initialization():
    """Verify RailRadarClient initializes settings and auth headers properly."""
    custom_client = RailRadarClient(api_key="test_key_xyz", base_url="https://api.railradar.in/v1")
    assert custom_client.is_configured is True
    assert custom_client.base_url == "https://api.railradar.in/v1"
    
    headers = custom_client._get_headers()
    assert headers["Authorization"] == "Bearer test_key_xyz"
    assert headers["Accept"] == "application/json"


def test_railradar_invalid_train_number():
    """Verify empty or blank train numbers fail gracefully."""
    res = railradar_client.get_live_train_status("")
    assert res["success"] is False
    assert "Invalid train number" in res["error"]


def test_railradar_live_fetch_and_cache():
    """Verify live train running status query and TTL caching."""
    if not railradar_client.is_configured:
        pytest.skip("RAILRADAR_API_KEY not configured in .env")

    # 0. Clear cache for test isolation
    railradar_client.clear_cache()

    # 1. First fetch (Live API)
    res1 = service_get_live_train_status("12423", authoritative=False)
    assert res1["success"] is True
    assert res1["train_number"] == "12423"
    assert "data" in res1
    assert res1.get("is_cached") is False

    # 2. Second fetch within TTL (Should hit in-memory cache)
    res2 = service_get_live_train_status("12423", authoritative=False)
    assert res2["success"] is True
    assert res2.get("is_cached") is True


def test_live_train_endpoint():
    """Verify GET /trains/{train_number}/live endpoint through FastAPI TestClient."""
    if not railradar_client.is_configured:
        pytest.skip("RAILRADAR_API_KEY not configured in .env")

    response = client.get("/trains/12423/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["train_number"] == "12423"
    assert data["source"] == "railradar_live"
    assert "data" in data

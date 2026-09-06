import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns operational status."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["project"] == "PredictRail"
    assert data["version"] == "1.0.0"


def test_list_trains():
    """Verify GET /trains returns train catalog with search/limit support."""
    resp = client.get("/trains?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_trains"] > 100
    assert len(data["trains"]) == 10
    
    first = data["trains"][0]
    assert "train_number" in first
    assert "train_name" in first
    assert "source_station" in first
    assert "destination_station" in first


def test_search_trains():
    """Verify GET /trains?search=Rajdhani searches by train name."""
    resp = client.get("/trains?search=Rajdhani&limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_trains"] > 0
    assert len(data["trains"]) <= 5
    for t in data["trains"]:
        assert "RAJDHANI" in t["train_name"].upper() or "RAJDHANI" in t["train_number"].upper()


def test_get_train_detail_valid():
    """Verify GET /trains/{train_number} returns full route itinerary."""
    resp = client.get("/trains/12423")
    assert resp.status_code == 200
    data = resp.json()
    assert data["train_number"] == "12423"
    assert "DBRT" in data["train_name"].upper() or "RA" in data["train_name"].upper()
    assert data["stations_count"] > 10
    assert len(data["stops"]) == data["stations_count"]
    assert data["stops"][0]["sequence"] == 1


def test_get_train_detail_not_found():
    """Verify GET /trains/{train_number} returns 404 for nonexistent train."""
    resp = client.get("/trains/99999999")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_predict_delay_endpoint():
    """Verify POST /predict-delay uses the ML pipeline."""
    payload = {
        "train_number": "12423",
        "station_code": "GHY",
        "current_delay_minutes": 15.0,
        "departure_hour": 14
    }
    resp = client.post("/predict-delay", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["train_number"] == "12423"
    assert data["station"] == "GHY"
    assert "predicted_delay_minutes" in data
    assert data["predicted_delay_minutes"] >= 0.0
    assert "delay_severity" in data


def test_predict_delay_invalid_station():
    """Verify POST /predict-delay returns 400 when station is not on route."""
    payload = {
        "train_number": "12423",
        "station_code": "MAS",  # Chennai Central is not on Dibrugarh-New Delhi Rajdhani
        "current_delay_minutes": 0.0
    }
    resp = client.post("/predict-delay", json=payload)
    assert resp.status_code == 400
    assert "not on the route" in resp.json()["detail"].lower()


def test_dynamic_eta_endpoint():
    """Verify POST /eta calculates multi-stop dynamic ETA."""
    payload = {
        "train_number": "12423",
        "current_station": "GHY",
        "current_delay_minutes": 30.0
    }
    resp = client.post("/eta", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["train_number"] == "12423"
    assert data["current_station"] == "GHY"
    assert data["destination"] == "NDLS"
    assert data["destination_dynamic_eta"] != ""
    assert data["destination_predicted_delay_min"] >= 0.0
    assert len(data["upcoming_itinerary"]) > 5


def test_weather_endpoint():
    """Verify GET /weather/{station_code} returns meteorological risk score."""
    resp = client.get("/weather/NDLS")
    assert resp.status_code == 200
    data = resp.json()
    assert data["station_code"] == "NDLS"
    assert data["station_name"] != ""
    assert "weather_category" in data
    assert "weather_risk_score" in data
    assert 0.0 <= data["weather_risk_score"] <= 100.0


def test_weather_endpoint_invalid_station():
    """Verify GET /weather/{station_code} handles unknown station gracefully."""
    resp = client.get("/weather/NONEXISTENT_STN")
    assert resp.status_code == 200
    data = resp.json()
    assert data["weather_category"] == "UNKNOWN"
    assert data["offline_fallback"] is True


def test_crowd_endpoint():
    """Verify POST /crowd returns prototype passenger density breakdown."""
    payload = {
        "train_number": "12423",
        "station_code": "GHY"
    }
    resp = client.post("/crowd", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["train_number"] == "12423"
    assert data["station_code"] == "GHY"
    assert data["data_type"] == "SYNTHETIC_PROTOTYPE"
    assert "overall_occupancy_percent" in data
    assert "overall_crowd_level" in data
    assert len(data["class_breakdown"]) > 0
    assert len(data["coach_details"]) > 0
    assert "PROTOTYPE" in data["disclaimer"]


def test_recommend_compartment_endpoint():
    """Verify POST /recommend-compartment recommends the least crowded class."""
    payload = {
        "train_number": "12423",
        "station_code": "GHY",
        "budget_filter": "ALL"
    }
    resp = client.post("/recommend-compartment", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["train_number"] == "12423"
    assert data["recommended_coach_or_class"] is not None
    assert data["crowd_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert len(data["ranked_options"]) > 0
    assert data["reason"] != ""
    assert "PROTOTYPE" in data["disclaimer"]


def test_recommend_compartment_budget_filter():
    """Verify POST /recommend-compartment with budget_filter='NON_AC'."""
    payload = {
        "train_number": "13009",
        "station_code": "HWH",
        "budget_filter": "NON_AC"
    }
    resp = client.post("/recommend-compartment", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    for opt in data["ranked_options"]:
        assert opt["coach_class"] in ["SL", "GEN", "2S"]


def test_combined_predict_endpoint():
    """Verify POST /predict combines all subsystems into unified dashboard payload."""
    payload = {
        "train_number": "12423",
        "current_station": "GHY",
        "current_delay_minutes": 30.0,
        "budget_filter": "ALL"
    }
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    
    # Subsystem key assertions
    assert "train" in data
    assert data["train"]["train_number"] == "12423"
    assert "delay_prediction" in data
    assert "dynamic_eta" in data
    assert "weather" in data
    assert "crowd" in data
    assert "compartment_recommendation" in data
    assert "network_bottlenecks" in data
    assert "delay_propagation" in data


def test_validation_errors():
    """Verify Pydantic input validation rejects negative delay and empty numbers."""
    # Negative delay
    resp = client.post("/eta", json={"train_number": "12423", "current_station": "GHY", "current_delay_minutes": -10.0})
    assert resp.status_code == 422

    # Blank train number
    resp = client.post("/eta", json={"train_number": "   ", "current_station": "GHY", "current_delay_minutes": 10.0})
    assert resp.status_code == 422


def test_cors_production_origin():
    """Verify CORS headers allow requests from production Vercel frontend."""
    headers = {
        "Origin": "https://predict-rail.vercel.app",
        "Access-Control-Request-Method": "GET"
    }
    # Preflight OPTIONS request
    resp = client.options("/health", headers=headers)
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "https://predict-rail.vercel.app"

    # Actual GET request
    resp = client.get("/health", headers={"Origin": "https://predict-rail.vercel.app"})
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "https://predict-rail.vercel.app"


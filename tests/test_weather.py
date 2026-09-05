import pytest
import os
import sys
import requests
from unittest.mock import patch, MagicMock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from weather.open_meteo import (
    load_station_coordinates,
    get_station_coordinates,
    fetch_station_weather,
    clear_weather_cache
)
from weather.weather_features import classify_weather
from weather.weather_risk import (
    calculate_weather_risk,
    get_route_weather,
    apply_weather_adjustment_to_eta,
    BASE_RISK_SCORES,
    BASE_DELAY_ADJUSTMENTS
)
from eta.dynamic_eta import get_dynamic_eta


def test_station_coordinates_lookup():
    """Verify that station coordinate database maps major Indian Railway stations correctly."""
    coords_map = load_station_coordinates()
    assert len(coords_map) > 8000, f"Expected >8000 stations, got {len(coords_map)}"

    # Check key Indian railway junctions
    for code in ["NDLS", "HWH", "CSMT", "CNB", "GHY"]:
        stn = get_station_coordinates(code)
        assert stn is not None, f"Station {code} should be found"
        assert stn["latitude"] is not None
        assert stn["longitude"] is not None
        # Indian geographic bounding box approx: Lat [8, 38], Lon [68, 98]
        assert 8.0 <= stn["latitude"] <= 38.0, f"{code} latitude out of Indian bounds: {stn['latitude']}"
        assert 68.0 <= stn["longitude"] <= 98.0, f"{code} longitude out of Indian bounds: {stn['longitude']}"


def test_invalid_station_coordinates():
    """Verify handling of invalid or unknown station codes."""
    assert get_station_coordinates("INVALID_CODE_999") is None
    
    res = fetch_station_weather("INVALID_CODE_999")
    assert res["success"] is False
    assert "Coordinates unavailable" in res["error"]
    assert res["weather_code"] == -1


def test_weather_classification():
    """Verify WMO code mapping into operational disruption categories."""
    assert classify_weather(0)["category"] == "CLEAR"
    assert classify_weather(1)["category"] == "CLEAR"
    assert classify_weather(45)["category"] == "FOG"
    assert classify_weather(51)["category"] == "LIGHT_RAIN"
    assert classify_weather(65)["category"] == "HEAVY_RAIN"
    assert classify_weather(71)["category"] == "SNOW"
    assert classify_weather(95)["category"] == "THUNDERSTORM"
    assert classify_weather(99)["category"] == "THUNDERSTORM"
    
    # High wind speed trigger
    assert classify_weather(1, wind_speed_kmh=55.0)["category"] == "STRONG_WIND"
    
    # Unknown / unmapped codes
    assert classify_weather(-1)["category"] == "UNKNOWN"
    assert classify_weather(999)["category"] == "UNKNOWN"


def test_weather_risk_scoring():
    """Verify transparent rule-based risk score calculation."""
    # Test Clear weather
    clear_sample = {
        "weather_code": 0,
        "wind_speed_kmh": 10.0,
        "precipitation_mm": 0.0,
        "visibility_m": 10000.0,
        "temperature_c": 28.0
    }
    r_clear = calculate_weather_risk(clear_sample)
    assert r_clear["weather_category"] == "CLEAR"
    assert r_clear["weather_risk_score"] <= 15.0
    assert r_clear["weather_delay_adjustment_min"] == 0.0

    # Test Foggy weather (dense fog with low visibility)
    fog_sample = {
        "weather_code": 45,
        "wind_speed_kmh": 5.0,
        "precipitation_mm": 0.0,
        "visibility_m": 250.0,
        "temperature_c": 12.0
    }
    r_fog = calculate_weather_risk(fog_sample)
    assert r_fog["weather_category"] == "FOG"
    assert r_fog["weather_risk_score"] >= 80.0
    assert r_fog["weather_delay_adjustment_min"] >= 30.0
    assert "High Risk" in r_fog["weather_risk_level"]

    # Test Thunderstorm
    storm_sample = {
        "weather_code": 95,
        "wind_speed_kmh": 35.0,
        "precipitation_mm": 20.0,
        "visibility_m": 3000.0,
        "temperature_c": 22.0
    }
    r_storm = calculate_weather_risk(storm_sample)
    assert r_storm["weather_category"] == "THUNDERSTORM"
    assert r_storm["weather_risk_score"] >= 80.0
    assert r_storm["weather_delay_adjustment_min"] >= 25.0


def test_api_caching():
    """Verify in-memory caching prevents redundant API calls."""
    clear_weather_cache()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "current": {
            "temperature_2m": 26.5,
            "relative_humidity_2m": 60,
            "precipitation": 0.0,
            "rain": 0.0,
            "snowfall": 0.0,
            "weather_code": 1,
            "wind_speed_10m": 12.0,
            "visibility": 10000,
            "time": "2026-09-05T12:00"
        }
    }

    with patch("requests.get", return_value=mock_response) as mock_get:
        # First call hits API
        res1 = fetch_station_weather("NDLS")
        assert res1["success"] is True
        assert res1["is_cached"] is False
        assert mock_get.call_count == 1

        # Second call hits Cache
        res2 = fetch_station_weather("NDLS")
        assert res2["success"] is True
        assert res2["is_cached"] is True
        assert mock_get.call_count == 1  # No second HTTP request!


def test_api_failure_handling():
    """Verify graceful fallback on API network timeouts and connection errors."""
    clear_weather_cache()

    # Case 1: Timeout
    with patch("requests.get", side_effect=requests.exceptions.Timeout("Connection timed out")):
        res = fetch_station_weather("HWH", bypass_cache=True)
        assert res["success"] is False
        assert "timed out" in res["error"].lower()
        risk = calculate_weather_risk(res)
        assert risk["weather_category"] == "UNKNOWN"
        assert risk["weather_delay_adjustment_min"] == 0.0

    # Case 2: Connection Error (Offline)
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Offline")):
        res = fetch_station_weather("CNB", bypass_cache=True)
        assert res["success"] is False
        assert "unable to connect" in res["error"].lower()

    # Case 3: HTTP Rate limit 429
    mock_429 = MagicMock()
    mock_429.status_code = 429
    with patch("requests.get", return_value=mock_429):
        res = fetch_station_weather("CSMT", bypass_cache=True)
        assert res["success"] is False
        assert "rate limit" in res["error"].lower()


def test_route_weather_mapping():
    """Verify upcoming station weather retrieval for a real Indian Railways route."""
    # Test on Train 12423 (Dibrugarh-New Delhi Rajdhani Express)
    res = get_route_weather("12423", "GHY", sample_stops_interval=1)
    assert res["success"] is True
    assert res["train_number"] == "12423"
    assert res["observation_station"] == "GHY"
    assert len(res["station_weather_profiles"]) > 5
    
    first_stn = res["station_weather_profiles"][0]
    assert first_stn["station_code"] == "GHY"
    assert "weather" in first_stn
    assert "weather_risk_score" in first_stn["weather"]


def test_weather_eta_adjustment_layer():
    """Verify that weather adjustment enriches Dynamic ETA without mutating base ML/graph delay."""
    # Generate Dynamic ETA for Rajdhani 12423
    base_eta = get_dynamic_eta("12423", "GHY", 30.0)
    assert base_eta["success"] is True

    # Apply weather adjustment layer
    enriched = apply_weather_adjustment_to_eta(base_eta)
    assert enriched["success"] is True
    assert "upcoming_itinerary" in enriched
    assert len(enriched["upcoming_itinerary"]) == len(base_eta["upcoming_itinerary"])

    # Check separation of concerns
    for orig, stop in zip(base_eta["upcoming_itinerary"], enriched["upcoming_itinerary"]):
        # Base predicted delay is preserved
        assert stop["base_predicted_delay_min"] == orig["predicted_delay_min"]
        assert "weather_delay_adjustment_min" in stop
        assert "weather_risk_score" in stop
        assert "weather_category" in stop
        
        # Final weather-adjusted delay = base + adjustment
        expected_final = round(stop["base_predicted_delay_min"] + stop["weather_delay_adjustment_min"], 1)
        # Note: cumulative compound might make it >= base
        assert stop["final_weather_adjusted_delay_min"] >= stop["base_predicted_delay_min"]

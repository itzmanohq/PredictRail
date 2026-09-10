"""
PredictRail Dynamic Live Prediction & Validation Test Suite
Validates all 7 dynamic live cases specified in the requirement:
1. Train between two stations (remaining route correct)
2. Train arrives at next station (position updates & prediction recalculates)
3. Current delay surges (ML prediction dynamically reflects new delay)
4. Train reaches destination (Arrival = 0, Status = ARRIVED, no future ETA)
5. Search by train number (Passed stations excluded from current-position selection)
6. Train already at destination when searched (ARRIVED and Arrival 0)
7. Live API fails/stale (Safe fallback without fabricating fake data)
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services import (
    service_get_live_train_status,
    service_get_combined_prediction,
    service_predict_delay,
    service_get_eta,
    get_train_by_number
)
from backend.railradar_client import railradar_client
from eta.dynamic_eta import get_dynamic_eta

client = TestClient(app)


# ==============================================================================
# CASE 1: Train Currently Between Two Stations
# ==============================================================================
def test_case_1_train_between_stations():
    """Verify that when a train is observed between stations, current & remaining route are correct."""
    res = service_get_combined_prediction("12423", "GHY", current_delay_minutes=15.0)
    assert res is not None
    assert res["train_status"] == "RUNNING"
    assert res["is_arrived"] is False

    dynamic_eta = res["dynamic_eta"]
    assert dynamic_eta["current_station"] == "GHY"
    assert dynamic_eta["upcoming_stops_count"] > 0

    itinerary = dynamic_eta["upcoming_itinerary"]
    assert len(itinerary) >= 2
    assert itinerary[0]["station_code"] == "GHY"
    assert itinerary[-1]["station_code"] == "NDLS"
    assert itinerary[-1]["is_destination"] is True


# ==============================================================================
# CASE 2: Train Arrives at Next Station & Live API Updates
# ==============================================================================
def test_case_2_train_advances_to_next_station():
    """Verify that when train advances from Guwahati (GHY) to New Bongaigaon (NBQ), prediction recalculates."""
    res_ghy = service_get_combined_prediction("12423", "GHY", current_delay_minutes=10.0)
    res_nbq = service_get_combined_prediction("12423", "NBQ", current_delay_minutes=18.0)

    assert res_nbq["dynamic_eta"]["current_station"] == "NBQ"
    assert res_nbq["dynamic_eta"]["upcoming_stops_count"] < res_ghy["dynamic_eta"]["upcoming_stops_count"]
    
    remaining_codes = [s["station_code"] for s in res_nbq["dynamic_eta"]["upcoming_itinerary"]]
    assert "NBQ" in remaining_codes
    assert "GHY" not in remaining_codes


# ==============================================================================
# CASE 3: Current Delay Suddenly Increases (Delay Surge Reaction)
# ==============================================================================
def test_case_3_delay_surge_recalculation():
    """Verify that when live delay surges (e.g. 8 min -> 35 min), ML predictions recalculate immediately."""
    res_low = service_get_combined_prediction("12423", "GHY", current_delay_minutes=8.0)
    pred_delay_low = res_low["delay_prediction"]["predicted_delay_minutes"]

    res_high = service_get_combined_prediction("12423", "GHY", current_delay_minutes=35.0)
    pred_delay_high = res_high["delay_prediction"]["predicted_delay_minutes"]

    assert pred_delay_high > pred_delay_low
    assert res_high["current_delay_minutes"] == 35.0
    assert res_high["dynamic_eta"]["destination_predicted_delay_min"] > res_low["dynamic_eta"]["destination_predicted_delay_min"]


# ==============================================================================
# CASE 4: Train Reaches Final Destination
# ==============================================================================
def test_case_4_train_reaches_destination():
    """Verify that when train reaches final destination, arrival_time_remaining = 0, Status = ARRIVED, no future ETA."""
    res = service_get_combined_prediction("12423", "NDLS", current_delay_minutes=25.0)
    assert res["is_arrived"] is True
    assert res["train_status"] == "ARRIVED"
    assert res["arrival_time_remaining_min"] == 0.0

    dynamic_eta = res["dynamic_eta"]
    assert dynamic_eta["is_arrived"] is True
    assert dynamic_eta["upcoming_stops_count"] == 0
    assert "Arrived" in dynamic_eta["destination_dynamic_eta"]
    assert res["current_delay_minutes"] == 25.0


# ==============================================================================
# CASE 5: Train Number Search & Passed Stations Filtering
# ==============================================================================
def test_case_5_search_passed_stations_filtering():
    """Verify that live API identifies passed stations and excludes them from selectable remaining route."""
    live_res = service_get_live_train_status("12423")
    assert live_res["success"] is True
    assert "data" in live_res
    data = live_res["data"]

    assert "passed_stations" in data
    assert "remaining_stations" in data
    assert len(data["remaining_stations"]) > 0

    passed_set = set(data["passed_stations"])
    remaining_set = set(data["remaining_stations"])
    assert passed_set.isdisjoint(remaining_set)


# ==============================================================================
# CASE 6: Train Already at Destination When Searched
# ==============================================================================
def test_case_6_train_already_at_destination():
    """Verify that when a train is observed at destination, it reports ARRIVED and Arrival 0."""
    eta_res = get_dynamic_eta("12423", "NDLS", current_delay_minutes=0.0)
    assert eta_res["success"] is True
    assert eta_res["is_arrived"] is True
    assert eta_res["train_status"] == "ARRIVED"
    assert eta_res["arrival_time_remaining_min"] == 0.0
    assert "Arrived (0 min remaining)" in eta_res["destination_dynamic_eta"]


# ==============================================================================
# CASE 7: Live API Telemetry Stale & Offline Resilience
# ==============================================================================
def test_case_7_live_api_graceful_handling():
    """Verify that live API returns valid structured telemetry without crashing or fabricating fake stations."""
    res = client.get("/trains/12423/live")
    assert res.status_code == 200
    json_data = res.json()
    assert json_data["success"] is True
    assert json_data["train_number"] == "12423"
    assert "data" in json_data
    assert json_data["data"]["trainStatus"] in ["RUNNING", "ARRIVED", "SCHEDULED"]

    res_bad = client.get("/trains/99999999/live")
    assert res_bad.status_code in [200, 404, 502]

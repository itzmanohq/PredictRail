import pytest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eta.eta_calculator import compute_dynamic_eta_timestamp, parse_time_to_minutes
from eta.dynamic_eta import get_dynamic_eta

def test_time_parsing():
    assert parse_time_to_minutes("14:30:00") == 870.0
    assert parse_time_to_minutes("00:00:00") == 0.0
    assert parse_time_to_minutes("23:59:00") == 1439.0
    assert parse_time_to_minutes("") == 0.0
    assert parse_time_to_minutes(None) == 0.0

def test_eta_calculator_basic():
    res = compute_dynamic_eta_timestamp("10:00:00", 30.0, scheduled_day=1)
    assert res["eta_time_str"] == "10:30:00"
    assert res["eta_day"] == 1
    assert res["days_delayed_offset"] == 0
    assert res["eta_formatted"] == "10:30:00"

def test_eta_calculator_midnight_rollover():
    # 23:45 with 30 min delay -> 00:15 next day
    res = compute_dynamic_eta_timestamp("23:45:00", 30.0, scheduled_day=1)
    assert res["eta_time_str"] == "00:15:00"
    assert res["eta_day"] == 2
    assert res["days_delayed_offset"] == 1
    assert "+1 Day" in res["eta_formatted"]

def test_eta_calculator_multiday_journey():
    # Day 2 scheduled at 02:00 + 120m delay -> 04:00 Day 2
    res = compute_dynamic_eta_timestamp("02:00:00", 120.0, scheduled_day=2)
    assert res["eta_time_str"] == "04:00:00"
    assert res["eta_day"] == 2
    assert res["days_delayed_offset"] == 0
    assert "Day 2" in res["eta_formatted"]

def test_get_dynamic_eta_doon_express():
    # Train 13009 (Doon Express) from Howrah
    res = get_dynamic_eta("13009", "HWH", 45.0)
    assert res["success"] is True
    assert res["train_number"] == "13009"
    assert res["current_station"] == "HWH"
    assert res["destination_station"] == "DDN"
    assert res["upcoming_stops_count"] > 50
    assert len(res["upcoming_itinerary"]) > 50

    # First stop (HWH) delay is initial delay
    assert res["upcoming_itinerary"][0]["predicted_delay_min"] == 45.0
    
    # Destination dynamic ETA must be present
    assert res["destination_dynamic_eta"] != ""
    assert res["destination_predicted_delay_min"] >= 0.0

def test_get_dynamic_eta_rajdhani_express():
    # Train 12423 (Dibrugarh-New Delhi Rajdhani) from Guwahati
    res = get_dynamic_eta("12423", "GHY", 30.0)
    assert res["success"] is True
    assert res["train_number"] == "12423"
    assert res["current_station"] == "GHY"
    assert res["destination_station"] == "NDLS"
    assert res["upcoming_stops_count"] > 5

    # Check that day progression and bottlenecks are populated
    for stop in res["upcoming_itinerary"]:
        assert stop["dynamic_eta_time"] != ""
        assert stop["predicted_delay_min"] >= 0.0
        assert "congestion_level" in stop

def test_get_dynamic_eta_intermediate_station():
    # Train 12345 starting mid-route at Bolpur (BHP)
    res = get_dynamic_eta("12345", "BHP", 15.0)
    assert res["success"] is True
    assert res["current_station"] == "BHP"
    # Should start from BHP, not HWH
    assert res["upcoming_itinerary"][0]["station_code"] == "BHP"

def test_get_dynamic_eta_terminus():
    # Train 12345 observed at destination Guwahati (GHY)
    res = get_dynamic_eta("12345", "GHY", 10.0)
    assert res["success"] is True
    assert res["upcoming_stops_count"] == 0
    assert len(res["upcoming_itinerary"]) == 1
    assert res["upcoming_itinerary"][0]["is_destination"] is True

def test_get_dynamic_eta_invalid_train():
    res = get_dynamic_eta("9999999", "NDLS", 0.0)
    assert res["success"] is False
    assert "not found" in res["error"].lower()

def test_get_dynamic_eta_invalid_station():
    # Train 13009 does not go through Chennai Central (MAS)
    res = get_dynamic_eta("13009", "MAS", 0.0)
    assert res["success"] is False
    assert "not on the scheduled route" in res["error"].lower()

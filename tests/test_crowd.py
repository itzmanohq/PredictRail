import pytest
import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crowd.crowd_detector import (
    CROWD_THRESHOLDS,
    calculate_occupancy_ratio,
    classify_crowd_level,
    get_coach_crowd_profile,
    estimate_station_crowd,
    load_crowd_data
)
from crowd.recommendation import recommend_smart_compartment


def test_occupancy_ratio_calculation():
    """Verify robust occupancy ratio calculation across standard and edge cases."""
    # Standard calculations
    assert calculate_occupancy_ratio(36, 72) == 0.50
    assert calculate_occupancy_ratio(54, 72) == 0.75
    assert calculate_occupancy_ratio(72, 72) == 1.00
    assert calculate_occupancy_ratio(0, 72) == 0.0

    # Overcapacity (realistic for unreserved coaches in Indian Railways)
    assert calculate_occupancy_ratio(108, 72) == 1.50

    # Edge cases & invalid inputs
    assert calculate_occupancy_ratio(50, 0) == 0.0, "Zero capacity must return 0.0 safely"
    assert calculate_occupancy_ratio(50, -10) == 0.0, "Negative capacity must return 0.0 safely"
    assert calculate_occupancy_ratio(-5, 72) == 0.0, "Negative passengers must return 0.0 safely"
    assert calculate_occupancy_ratio("invalid", 72) == 0.0
    assert calculate_occupancy_ratio(50, None) == 0.0


def test_crowd_level_classification():
    """Verify transparent classification into LOW, MEDIUM, and HIGH crowd levels."""
    # Configurable threshold assertions: LOW <= 0.50, MEDIUM 0.51-0.80, HIGH > 0.80
    assert classify_crowd_level(0.25) == "LOW"
    assert classify_crowd_level(0.50) == "LOW"
    assert classify_crowd_level(0.51) == "MEDIUM"
    assert classify_crowd_level(0.75) == "MEDIUM"
    assert classify_crowd_level(0.80) == "MEDIUM"
    assert classify_crowd_level(0.81) == "HIGH"
    assert classify_crowd_level(1.00) == "HIGH"
    assert classify_crowd_level(1.45) == "HIGH"

    # Invalid / boundary inputs
    assert classify_crowd_level(-0.1) == "UNKNOWN"
    assert classify_crowd_level(None) == "UNKNOWN"
    assert classify_crowd_level("invalid_string") == "UNKNOWN"


def test_central_configurable_thresholds():
    """Ensure central threshold keys are defined and logically ordered."""
    assert "LOW_MAX" in CROWD_THRESHOLDS
    assert "MEDIUM_MAX" in CROWD_THRESHOLDS
    assert 0.0 < CROWD_THRESHOLDS["LOW_MAX"] < CROWD_THRESHOLDS["MEDIUM_MAX"] < 1.0


def test_synthetic_dataset_integrity():
    """Verify the generated synthetic crowd dataset contains expected structure and tags."""
    df = load_crowd_data()
    assert not df.empty, "Synthetic crowd dataset must not be empty"
    assert len(df) > 10000, f"Expected >10,000 synthetic records, got {len(df)}"

    expected_cols = [
        "train_number", "train_name", "station_code", "station_name",
        "coach_class", "coach_id", "estimated_passengers", "estimated_capacity",
        "occupancy_ratio", "crowd_level", "data_tag"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"

    # Verify prototype data labeling
    assert (df["data_tag"] == "SYNTHETIC_PROTOTYPE").all(), "All rows must be explicitly tagged as SYNTHETIC_PROTOTYPE"


def test_station_crowd_estimation():
    """Verify aggregation of passenger density for a real train and station stop."""
    # Test on Rajdhani 12423 at Guwahati (GHY)
    res = estimate_station_crowd("12423", "GHY")
    assert res["success"] is True
    assert res["train_number"] == "12423"
    assert res["station_code"] == "GHY"
    assert res["total_estimated_passengers"] > 0
    assert res["total_estimated_capacity"] > 0
    assert 0.0 <= res["overall_occupancy_ratio"] <= 2.0
    assert res["overall_crowd_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert len(res["class_breakdown"]) > 0
    assert len(res["coach_details"]) > 0
    assert "PROTOTYPE" in res["disclaimer"]


def test_smart_compartment_recommendation_least_crowded():
    """Verify that recommendation algorithm correctly picks the lowest occupancy option."""
    rec = recommend_smart_compartment("12423", "GHY")
    assert rec["success"] is True
    assert rec["recommended_coach_or_class"] is not None
    assert rec["crowd_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert rec["occupancy_ratio"] > 0.0
    assert len(rec["ranked_options"]) > 0
    assert rec["reason"] != ""
    assert "PROTOTYPE" in rec["disclaimer"]

    # Verify that the recommended class is indeed the minimum occupancy option
    min_occupancy = min(o["occupancy_ratio"] for o in rec["ranked_options"])
    assert rec["occupancy_ratio"] == min_occupancy, "Recommended class must have the lowest occupancy ratio"
    assert rec["ranked_options"][0]["is_recommended"] is True


def test_smart_compartment_recommendation_budget_filter():
    """Verify budget / Non-AC class filtering (e.g., Sleeper vs General vs 2S)."""
    rec_non_ac = recommend_smart_compartment("13009", "HWH", budget_filter="NON_AC")
    assert rec_non_ac["success"] is True
    
    # All ranked options should be Non-AC classes
    for opt in rec_non_ac["ranked_options"]:
        assert opt["coach_class"] in ["SL", "GEN", "2S"]


def test_smart_compartment_recommendation_preferred_classes():
    """Verify user preferred class list restriction."""
    pref = ["2A", "3A"]
    rec = recommend_smart_compartment("12423", "GHY", preferred_classes=pref)
    assert rec["success"] is True
    assert rec["recommended_coach_or_class"] in pref
    for opt in rec["ranked_options"]:
        assert opt["coach_class"] in pref


def test_fallback_for_unindexed_train():
    """Verify graceful handling and fallback for trains/stations not in synthetic CSV."""
    rec = recommend_smart_compartment("99999", "UNKNOWN_STN")
    assert rec["success"] is True
    assert rec["recommended_coach_or_class"] is not None
    assert rec["crowd_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert rec["occupancy_ratio"] > 0.0

"""
PredictRail Prototype Crowd Estimation & Smart Compartment Recommendation Module
"""
from crowd.crowd_detector import (
    CROWD_THRESHOLDS,
    DEFAULT_COACH_CAPACITIES,
    load_crowd_data,
    calculate_occupancy_ratio,
    classify_crowd_level,
    get_coach_crowd_profile,
    estimate_station_crowd
)

from crowd.recommendation import (
    recommend_smart_compartment,
    CLASS_DISPLAY_NAMES
)

from crowd.generate_synthetic import (
    generate_synthetic_crowd_dataset,
    COACH_CAPACITIES,
    RAKE_COMPOSITIONS
)

__all__ = [
    "CROWD_THRESHOLDS",
    "DEFAULT_COACH_CAPACITIES",
    "load_crowd_data",
    "calculate_occupancy_ratio",
    "classify_crowd_level",
    "get_coach_crowd_profile",
    "estimate_station_crowd",
    "recommend_smart_compartment",
    "CLASS_DISPLAY_NAMES",
    "generate_synthetic_crowd_dataset",
    "COACH_CAPACITIES",
    "RAKE_COMPOSITIONS"
]

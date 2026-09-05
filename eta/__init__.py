"""
PredictRail Dynamic ETA Module
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eta.eta_calculator import compute_dynamic_eta_timestamp, parse_time_to_minutes
from eta.dynamic_eta import get_dynamic_eta, format_eta_table

__all__ = [
    "get_dynamic_eta",
    "format_eta_table",
    "compute_dynamic_eta_timestamp",
    "parse_time_to_minutes"
]

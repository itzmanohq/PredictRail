"""
PredictRail Prototype Crowd Estimation & Density Detection Module

DISCLAIMER:
This module operates on SYNTHETIC PROTOTYPE DATA for academic and architectural demonstration.
It does NOT connect to live camera sensors, thermal imagers, or live IRCTC reservation counters.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SYNTHETIC_CROWD_CSV = BASE_DIR / "data" / "synthetic" / "crowd_data.csv"

# Transparent, Configurable Central Crowd Level Thresholds
# Occupancy Ratio = Estimated Passengers / Nominal Seating Capacity
CROWD_THRESHOLDS: Dict[str, float] = {
    "LOW_MAX": 0.50,       # Occupancy <= 50%  -> LOW (Comfortable, ample empty seats/berths)
    "MEDIUM_MAX": 0.80,    # 50% < Occupancy <= 80% -> MEDIUM (Moderately full, limited choice)
    # Occupancy > 80%  -> HIGH (Heavily crowded / Overcrowded / Standing room only)
}

# Standard Nominal Coach Capacities
DEFAULT_COACH_CAPACITIES: Dict[str, int] = {
    "1A": 24,    # AC First Class
    "2A": 54,    # AC 2-Tier
    "3A": 72,    # AC 3-Tier
    "3E": 83,    # AC 3-Tier Economy
    "SL": 72,    # Sleeper Class
    "GEN": 90,   # General Unreserved
    "CC": 78,    # AC Chair Car
    "EC": 56,    # Executive Chair Car
    "2S": 108    # Second Sitting
}

_CROWD_DF_CACHE: Optional[pd.DataFrame] = None

def load_crowd_data() -> pd.DataFrame:
    """
    Loads and caches the synthetic prototype crowd occupancy dataset.
    """
    global _CROWD_DF_CACHE
    if _CROWD_DF_CACHE is not None:
        return _CROWD_DF_CACHE

    if os.path.exists(SYNTHETIC_CROWD_CSV):
        try:
            df = pd.read_csv(SYNTHETIC_CROWD_CSV, dtype={'train_number': str, 'station_code': str})
            df['train_number'] = df['train_number'].str.strip().str.lstrip('0')
            df['station_code'] = df['station_code'].str.strip().str.upper()
            _CROWD_DF_CACHE = df
            return _CROWD_DF_CACHE
        except Exception as e:
            print(f"Warning: Error loading crowd_data.csv: {e}")

    # Return empty DataFrame if file is not found
    _CROWD_DF_CACHE = pd.DataFrame()
    return _CROWD_DF_CACHE

def calculate_occupancy_ratio(
    passengers: Union[int, float],
    capacity: Union[int, float]
) -> float:
    """
    Calculates passenger occupancy ratio with robust edge-case validation.
    
    Formula:
      occupancy_ratio = passengers / capacity
      
    Parameters:
      - passengers: Estimated passenger count (must be non-negative)
      - capacity: Coach capacity (must be positive)
      
    Returns:
      Float ratio rounded to 3 decimal places (0.0 if invalid or capacity <= 0).
    """
    try:
        pax = float(passengers)
        cap = float(capacity)
    except (TypeError, ValueError):
        return 0.0

    if np.isnan(pax) or np.isnan(cap) or cap <= 0.0 or pax < 0.0:
        return 0.0

    return round(pax / cap, 3)

def classify_crowd_level(occupancy_ratio: Union[int, float]) -> str:
    """
    Classifies occupancy ratio into standardized operational crowd levels
    using the centrally configured thresholds.
    
    Returns:
      'LOW', 'MEDIUM', 'HIGH', or 'UNKNOWN'
    """
    try:
        ratio = float(occupancy_ratio)
    except (TypeError, ValueError):
        return "UNKNOWN"

    if np.isnan(ratio) or ratio < 0.0:
        return "UNKNOWN"

    if ratio <= CROWD_THRESHOLDS["LOW_MAX"]:
        return "LOW"
    elif ratio <= CROWD_THRESHOLDS["MEDIUM_MAX"]:
        return "MEDIUM"
    else:
        return "HIGH"

def get_coach_crowd_profile(
    train_number: str,
    station_code: str,
    coach_class: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves synthetic prototype crowd records for a specific train and station.
    
    Parameters:
      - train_number: Indian Railways train number (e.g., '12423', '13009')
      - station_code: Station code (e.g., 'NDLS', 'GHY', 'HWH')
      - coach_class: Optional filter (e.g., '3A', '2A', 'SL')
      
    Returns:
      List of coach status dictionaries.
    """
    t_no = str(train_number).strip().lstrip('0')
    stn = str(station_code).strip().upper()
    df = load_crowd_data()

    if df.empty:
        return []

    subset = df[(df['train_number'] == t_no) & (df['station_code'] == stn)]
    
    if coach_class:
        c_cls = str(coach_class).strip().upper()
        subset = subset[subset['coach_class'] == c_cls]

    if subset.empty:
        return []

    results = []
    for _, row in subset.iterrows():
        results.append({
            "coach_id": row["coach_id"],
            "coach_class": row["coach_class"],
            "estimated_passengers": int(row["estimated_passengers"]),
            "estimated_capacity": int(row["estimated_capacity"]),
            "occupancy_ratio": float(row["occupancy_ratio"]),
            "occupancy_percent": round(float(row["occupancy_ratio"]) * 100.0, 1),
            "crowd_level": row["crowd_level"],
            "data_tag": row.get("data_tag", "SYNTHETIC_PROTOTYPE")
        })

    return results

def estimate_station_crowd(
    train_number: str,
    station_code: str
) -> Dict[str, Any]:
    """
    Aggregates synthetic prototype passenger density across all coach classes for a train stop.
    
    Returns structured overview with overall train load, breakdown per class, and crowd levels.
    """
    t_no = str(train_number).strip().lstrip('0')
    stn = str(station_code).strip().upper()
    
    coaches = get_coach_crowd_profile(t_no, stn)
    
    # If not in synthetic CSV, synthesize a deterministic fallback profile
    if not coaches:
        df_sched_path = os.path.join(BASE_DIR, "data", "raw", "indian_railway_schedules.csv")
        stn_name = stn
        train_name = f"Train {t_no}"
        
        if os.path.exists(df_sched_path):
            try:
                sched = pd.read_csv(df_sched_path, nrows=5000, low_memory=False)
                # Find matching row if possible
            except Exception:
                pass

        # Generate on-the-fly prototype estimation
        fallback_classes = [("1A", 24, 0.42), ("2A", 54, 0.62), ("3A", 72, 0.82), ("SL", 72, 0.94), ("GEN", 90, 1.15)]
        coaches = []
        for c_cls, cap, r in fallback_classes:
            pax = int(round(r * cap))
            ratio = calculate_occupancy_ratio(pax, cap)
            coaches.append({
                "coach_id": f"{c_cls}1",
                "coach_class": c_cls,
                "estimated_passengers": pax,
                "estimated_capacity": cap,
                "occupancy_ratio": ratio,
                "occupancy_percent": round(ratio * 100.0, 1),
                "crowd_level": classify_crowd_level(ratio),
                "data_tag": "SYNTHETIC_PROTOTYPE_FALLBACK"
            })

    # Group by coach class
    class_summary: Dict[str, Dict[str, Any]] = {}
    total_pax = 0
    total_cap = 0

    for c in coaches:
        cls_name = c["coach_class"]
        pax = c["estimated_passengers"]
        cap = c["estimated_capacity"]
        
        total_pax += pax
        total_cap += cap

        if cls_name not in class_summary:
            class_summary[cls_name] = {
                "coach_class": cls_name,
                "coach_count": 0,
                "total_passengers": 0,
                "total_capacity": 0,
                "average_occupancy_ratio": 0.0,
                "crowd_level": "UNKNOWN"
            }
            
        class_summary[cls_name]["coach_count"] += 1
        class_summary[cls_name]["total_passengers"] += pax
        class_summary[cls_name]["total_capacity"] += cap

    # Finalize class metrics
    for cls_name, info in class_summary.items():
        avg_r = calculate_occupancy_ratio(info["total_passengers"], info["total_capacity"])
        info["average_occupancy_ratio"] = avg_r
        info["average_occupancy_percent"] = round(avg_r * 100.0, 1)
        info["crowd_level"] = classify_crowd_level(avg_r)

    overall_ratio = calculate_occupancy_ratio(total_pax, total_cap)
    
    return {
        "success": True,
        "train_number": t_no,
        "station_code": stn,
        "data_type": "SYNTHETIC_PROTOTYPE",
        "disclaimer": "PROTOTYPE DATA: Synthetic passenger density estimate for demonstration purposes only. Not live sensor or IRCTC PNR data.",
        "total_estimated_passengers": total_pax,
        "total_estimated_capacity": total_cap,
        "overall_occupancy_ratio": overall_ratio,
        "overall_occupancy_percent": round(overall_ratio * 100.0, 1),
        "overall_crowd_level": classify_crowd_level(overall_ratio),
        "class_breakdown": list(class_summary.values()),
        "coach_details": coaches
    }

if __name__ == "__main__":
    print("Testing Prototype Crowd Estimation & Detection...")
    res = estimate_station_crowd("12423", "GHY")
    print(f"Train {res['train_number']} at {res['station_code']} | Overall Occupancy: {res['overall_occupancy_percent']}% ({res['overall_crowd_level']})")
    print("\nClass Breakdown:")
    for c in res["class_breakdown"]:
        print(f" - Class {c['coach_class']:<4}: {c['total_passengers']}/{c['total_capacity']} pax ({c['average_occupancy_percent']}%) -> {c['crowd_level']}")

"""
PredictRail Smart Compartment & Coach Class Recommendation Engine

DISCLAIMER:
All compartment occupancy recommendations are generated using SYNTHETIC PROTOTYPE ESTIMATES.
They are intended for algorithmic and passenger advisory UX demonstration, NOT as guaranteed live seat availability.
"""
import os
import sys
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crowd.crowd_detector import estimate_station_crowd, calculate_occupancy_ratio, classify_crowd_level

# Friendly Indian Railways Class Descriptions
CLASS_DISPLAY_NAMES = {
    "1A": "AC First Class (1A)",
    "2A": "AC 2-Tier (2A)",
    "3A": "AC 3-Tier (3A)",
    "3E": "AC 3 Economy (3E)",
    "SL": "Sleeper Class (SL)",
    "GEN": "General Unreserved (GEN/GS)",
    "CC": "AC Chair Car (CC)",
    "EC": "Executive Chair Car (EC)",
    "2S": "Second Sitting (2S)"
}

def recommend_smart_compartment(
    train_number: str,
    station_code: str,
    preferred_classes: Optional[List[str]] = None,
    budget_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates available prototype coach classes on a train stop and recommends
    the least crowded compartment/class option with transparent reasoning.

    Parameters:
      - train_number: Indian Railways train number (e.g. '12423', '13009')
      - station_code: Station code (e.g. 'NDLS', 'GHY', 'HWH')
      - preferred_classes: Optional list of class codes to restrict recommendation to (e.g. ['3A', '2A'])
      - budget_filter: 'AC' (1A, 2A, 3A, 3E, CC, EC), 'NON_AC' (SL, GEN, 2S), or None ('ALL')

    Returns:
      Structured recommendation dictionary with recommended option, alternative rankings, and explanation.
    """
    t_no = str(train_number).strip().lstrip('0')
    stn = str(station_code).strip().upper()

    crowd_overview = estimate_station_crowd(t_no, stn)
    all_classes = crowd_overview["class_breakdown"]

    if not all_classes:
        return {
            "success": False,
            "train_number": t_no,
            "station_code": stn,
            "error": f"No coach data available for train {t_no} at station {stn}.",
            "recommended_coach_or_class": None,
            "crowd_level": "UNKNOWN",
            "occupancy_ratio": 0.0,
            "reason": "Station or train not found in schedule database."
        }

    # Apply class and budget filters
    candidate_classes = all_classes.copy()

    if budget_filter:
        b_filter = budget_filter.strip().upper()
        if b_filter == "AC":
            candidate_classes = [c for c in candidate_classes if c["coach_class"] in ["1A", "2A", "3A", "3E", "CC", "EC"]]
        elif b_filter in ["NON_AC", "NON-AC", "BUDGET"]:
            candidate_classes = [c for c in candidate_classes if c["coach_class"] in ["SL", "GEN", "2S"]]

    if preferred_classes:
        pref_set = {str(c).strip().upper() for c in preferred_classes}
        candidate_classes = [c for c in candidate_classes if c["coach_class"] in pref_set]

    # Fallback to all classes if filter excludes everything
    if not candidate_classes:
        candidate_classes = all_classes.copy()

    # Sort candidate classes by average occupancy ratio ascending (least crowded first)
    sorted_candidates = sorted(candidate_classes, key=lambda x: x["average_occupancy_ratio"])
    best_option = sorted_candidates[0]

    # Find the most specific coach in this class with the lowest occupancy
    best_cls = best_option["coach_class"]
    matching_coaches = [c for c in crowd_overview["coach_details"] if c["coach_class"] == best_cls]
    matching_coaches_sorted = sorted(matching_coaches, key=lambda x: x["occupancy_ratio"])
    best_coach_id = matching_coaches_sorted[0]["coach_id"] if matching_coaches_sorted else f"{best_cls}1"
    best_coach_pax = matching_coaches_sorted[0]["estimated_passengers"] if matching_coaches_sorted else best_option["total_passengers"]
    best_coach_cap = matching_coaches_sorted[0]["estimated_capacity"] if matching_coaches_sorted else best_option["total_capacity"]

    # Generate transparent domain reasoning
    reasons = []
    reasons.append(
        f"Class {best_cls} ({CLASS_DISPLAY_NAMES.get(best_cls, best_cls)}) has the lowest estimated occupancy "
        f"at {best_option['average_occupancy_percent']}% ({best_option['crowd_level']} crowd density)."
    )

    # Compare with crowded alternatives if present
    other_classes = [c for c in candidate_classes if c["coach_class"] != best_cls]
    if other_classes:
        worst_option = max(candidate_classes, key=lambda x: x["average_occupancy_ratio"])
        diff_pct = round(worst_option["average_occupancy_percent"] - best_option["average_occupancy_percent"], 1)
        if diff_pct > 10.0:
            reasons.append(
                f"Saves ~{diff_pct}% congestion compared to {worst_option['coach_class']} ({worst_option['average_occupancy_percent']}% - {worst_option['crowd_level']})."
            )

    full_reason = " ".join(reasons)

    # Format candidate ranking table for UI/API
    ranked_options = []
    for opt in sorted_candidates:
        c_name = opt["coach_class"]
        ranked_options.append({
            "coach_class": c_name,
            "class_display_name": CLASS_DISPLAY_NAMES.get(c_name, c_name),
            "occupancy_ratio": opt["average_occupancy_ratio"],
            "occupancy_percent": opt["average_occupancy_percent"],
            "crowd_level": opt["crowd_level"],
            "total_passengers": opt["total_passengers"],
            "total_capacity": opt["total_capacity"],
            "is_recommended": (c_name == best_cls)
        })

    return {
        "success": True,
        "train_number": t_no,
        "station_code": stn,
        "data_type": "SYNTHETIC_PROTOTYPE",
        "disclaimer": "PROTOTYPE DATA: Synthetic passenger density estimate for demonstration purposes only. Not live sensor or IRCTC PNR data.",
        "recommended_coach_or_class": best_cls,
        "recommended_coach_id": best_coach_id,
        "recommended_class_name": CLASS_DISPLAY_NAMES.get(best_cls, best_cls),
        "crowd_level": best_option["crowd_level"],
        "occupancy_ratio": best_option["average_occupancy_ratio"],
        "occupancy_percent": best_option["average_occupancy_percent"],
        "estimated_passengers": best_coach_pax,
        "estimated_capacity": best_coach_cap,
        "reason": full_reason,
        "ranked_options": ranked_options
    }

if __name__ == "__main__":
    print("Testing Smart Compartment Recommendation...")
    
    # 1. Rajdhani Express at Guwahati
    rec_rajdhani = recommend_smart_compartment("12423", "GHY")
    print("\n--- Recommendation for Rajdhani 12423 at GHY ---")
    print(f"Recommended Class: {rec_rajdhani['recommended_coach_or_class']} ({rec_rajdhani['crowd_level']} - {rec_rajdhani['occupancy_percent']}%)")
    print(f"Reason: {rec_rajdhani['reason']}")
    print("All Options Ranked:")
    for o in rec_rajdhani["ranked_options"]:
        print(f"  * {o['coach_class']:<4} -> {o['crowd_level']:<6} ({o['occupancy_percent']}%) [{'RECOMMENDED' if o['is_recommended'] else 'ALTERNATIVE'}]")

    # 2. Mail Express with Budget Filter (Non-AC)
    rec_budget = recommend_smart_compartment("13009", "HWH", budget_filter="NON_AC")
    print("\n--- Budget (Non-AC) Recommendation for Doon Express 13009 at HWH ---")
    print(f"Recommended Class: {rec_budget['recommended_coach_or_class']} ({rec_budget['crowd_level']} - {rec_budget['occupancy_percent']}%)")
    print(f"Reason: {rec_budget['reason']}")

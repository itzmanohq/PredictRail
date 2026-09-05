"""
PredictRail Step 7 Prototype Demonstration Script
Tests Prototype Crowd Estimation and Smart Compartment Recommendation on real Indian Railway trains.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from crowd.crowd_detector import estimate_station_crowd
from crowd.recommendation import recommend_smart_compartment

DEMO_SCENARIOS = [
    {"train_no": "12423", "train_title": "Dibrugarh - New Delhi Rajdhani Express", "station": "GHY", "filter": None},
    {"train_no": "13009", "train_title": "Doon Express (Howrah - Dehradun)", "station": "HWH", "filter": "NON_AC"},
    {"train_no": "12002", "train_title": "New Delhi - Habibganj Shatabdi Express", "station": "NDLS", "filter": None},
    {"train_no": "12301", "train_title": "Howrah - New Delhi Rajdhani Express", "station": "CNB", "filter": None},
    {"train_no": "12840", "train_title": "Chennai Central - Howrah Mail", "station": "MAS", "filter": None}
]

def run_crowd_demo():
    print("================================================================================")
    print(" PREDICTRAIL -- STEP 7: PROTOTYPE CROWD ESTIMATION & SMART RECOMMENDATION")
    print(" DISCLAIMER: Demonstrating SYNTHETIC PROTOTYPE ESTIMATES (Not live sensor data)")
    print("================================================================================\n")

    for idx, sc in enumerate(DEMO_SCENARIOS, 1):
        t_no = sc["train_no"]
        t_name = sc["train_title"]
        stn = sc["station"]
        b_filter = sc["filter"]

        crowd_info = estimate_station_crowd(t_no, stn)
        rec_info = recommend_smart_compartment(t_no, stn, budget_filter=b_filter)

        print(f"[{idx}] Train: {t_no} ({t_name})")
        print(f"    Station: {stn}")
        if b_filter:
            print(f"    Filter: {b_filter} (Budget Non-AC)")
        print(f"    Overall Train Load: {crowd_info['overall_occupancy_percent']}% ({crowd_info['overall_crowd_level']}) | Est. Pax: {crowd_info['total_estimated_passengers']:,} / {crowd_info['total_estimated_capacity']:,}")
        print("    Coach/Class Breakdown:")
        for opt in rec_info["ranked_options"]:
            bar_len = int(opt["occupancy_percent"] / 5)
            bar = "#" * bar_len + "-" * (20 - bar_len)
            status_tag = "<-- RECOMMENDED" if opt["is_recommended"] else ""
            print(f"      * {opt['coach_class']:<4} [{bar}] {opt['crowd_level']:<6} -> {opt['occupancy_percent']:>5.1f}% ({opt['total_passengers']}/{opt['total_capacity']} pax) {status_tag}")

        print(f"    Recommendation: {rec_info['recommended_coach_or_class']} (Coach {rec_info['recommended_coach_id']})")
        print(f"    Reason: {rec_info['reason']}")
        print(f"    Notice: {rec_info['disclaimer']}")
        print("-" * 80 + "\n")

if __name__ == "__main__":
    run_crowd_demo()

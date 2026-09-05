"""
PredictRail Rule-Based Weather Risk & ETA Adjustment Engine
Transparent heuristics for Indian Railways operational delay risk.
"""
import os
import sys
import pandas as pd
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from weather.open_meteo import fetch_station_weather
from weather.weather_features import classify_weather
from eta.dynamic_eta import get_dynamic_eta
from graph.delay_propagation import get_schedules_df

# Heuristic base risk scores (0 to 100)
BASE_RISK_SCORES = {
    "CLEAR": 5.0,
    "LIGHT_RAIN": 20.0,
    "STRONG_WIND": 50.0,
    "SNOW": 70.0,
    "HEAVY_RAIN": 65.0,
    "FOG": 80.0,
    "THUNDERSTORM": 85.0,
    "UNKNOWN": 10.0
}

# Heuristic base delay buffer additions (in minutes)
BASE_DELAY_ADJUSTMENTS = {
    "CLEAR": 0.0,
    "LIGHT_RAIN": 3.0,
    "STRONG_WIND": 8.0,
    "SNOW": 15.0,
    "HEAVY_RAIN": 18.0,
    "FOG": 30.0,
    "THUNDERSTORM": 25.0,
    "UNKNOWN": 0.0
}

def calculate_weather_risk(weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a transparent rule-based weather risk score and estimated delay buffer.
    
    Parameters:
      - weather_data: Output dictionary from fetch_station_weather()
      
    Returns:
      Dict with risk_score (0-100), risk_level, weather_delay_adjustment_min, and explanation.
    """
    w_code = weather_data.get("weather_code", -1)
    wind_spd = weather_data.get("wind_speed_kmh", 0.0)
    precip = weather_data.get("precipitation_mm", 0.0) or 0.0
    vis = weather_data.get("visibility_m")
    
    # 1. Category classification
    cls_res = classify_weather(w_code, wind_speed_kmh=wind_spd)
    category = cls_res["category"]
    desc = cls_res["description"]
    
    # 2. Base risk score
    score = BASE_RISK_SCORES.get(category, 10.0)
    base_delay = BASE_DELAY_ADJUSTMENTS.get(category, 0.0)

    # 3. Fine-grained adjustments
    # Visibility penalty (Fog speed restriction in Indian Railways)
    vis_penalty = 0.0
    if vis is not None:
        if vis < 500.0:
            vis_penalty = 15.0
            if category == "CLEAR":
                category = "FOG"
        elif vis < 1000.0:
            vis_penalty = 8.0

    # Precipitation penalty (waterlogging risk)
    precip_penalty = min(15.0, precip * 1.2)

    total_score = min(100.0, max(0.0, score + vis_penalty + precip_penalty))
    total_score = round(float(total_score), 1)

    # Delay adjustment calculation (minutes)
    if category == "CLEAR":
        delay_adj = 0.0
    else:
        delay_adj = base_delay + max(0.0, (total_score - 20.0) * 0.20)
    delay_adj = round(float(delay_adj), 1)

    # Risk level label
    if total_score <= 15.0:
        level = "Very Low (Optimal Rail Conditions)"
        badge_color = "green"
    elif total_score <= 40.0:
        level = "Low Risk (Minor Precipitation)"
        badge_color = "blue"
    elif total_score <= 65.0:
        level = "Moderate Risk (Caution Required)"
        badge_color = "orange"
    else:
        level = "High Risk (Severe Disruption Expected)"
        badge_color = "red"

    return {
        "weather_category": category,
        "weather_description": desc,
        "temperature_c": weather_data.get("temperature_c"),
        "precipitation_mm": precip,
        "wind_speed_kmh": wind_spd,
        "visibility_m": vis,
        "weather_risk_score": total_score,
        "weather_risk_level": level,
        "badge_color": badge_color,
        "weather_delay_adjustment_min": delay_adj,
        "rationale": f"{category} conditions ({desc}) -> Base {base_delay}m buffer + {delay_adj - base_delay:.1f}m severity adjustment."
    }

def get_route_weather(
    train_number: str,
    current_station: str,
    sample_stops_interval: int = 1
) -> Dict[str, Any]:
    """
    Fetches weather profiles for all upcoming station stops along a train route.
    """
    df_sched = get_schedules_df()
    t_no = str(train_number).strip().lstrip('0')
    cur_stn = str(current_station).strip().upper()
    
    route_df = df_sched[df_sched['Train_No'] == t_no].copy()
    if route_df.empty:
        return {"success": False, "error": f"Train {train_number} not found."}

    stops = route_df.to_dict('records')
    cur_idx = -1
    for idx, stop in enumerate(stops):
        if stop['Station_Code'] == cur_stn:
            cur_idx = idx
            break

    if cur_idx == -1:
        cur_idx = 0

    route_weather_list = []
    for i in range(cur_idx, len(stops), sample_stops_interval):
        s = stops[i]
        stn_code = s['Station_Code']
        raw_w = fetch_station_weather(stn_code)
        risk_info = calculate_weather_risk(raw_w)
        
        route_weather_list.append({
            "sequence": s['SEQ'],
            "station_code": stn_code,
            "station_name": s['Station_Name'],
            "distance_km": s['Distance'],
            "weather": risk_info,
            "raw_observation": raw_w
        })

    return {
        "success": True,
        "train_number": t_no,
        "train_name": route_df['Train Name'].iloc[0],
        "observation_station": cur_stn,
        "station_weather_profiles": route_weather_list
    }

def apply_weather_adjustment_to_eta(eta_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Consumes a Dynamic ETA response and enriches it with station-level weather risks
    while keeping the base ML/graph prediction and weather adjustment separately visible.
    """
    if not eta_response.get("success"):
        return eta_response

    enriched_itinerary = []
    cumulative_weather_buffer = 0.0

    for stn in eta_response["upcoming_itinerary"]:
        stn_code = stn["station_code"]
        raw_w = fetch_station_weather(stn_code)
        w_risk = calculate_weather_risk(raw_w)

        base_pred = stn["predicted_delay_min"]
        weather_adj = w_risk["weather_delay_adjustment_min"]
        
        # Incremental weather buffer (mild compounding along route)
        cumulative_weather_buffer = max(cumulative_weather_buffer, weather_adj)
        final_delay = round(base_pred + cumulative_weather_buffer, 1)

        enriched_stop = stn.copy()
        enriched_stop["weather_category"] = w_risk["weather_category"]
        enriched_stop["weather_description"] = w_risk["weather_description"]
        enriched_stop["weather_risk_score"] = w_risk["weather_risk_score"]
        enriched_stop["weather_risk_level"] = w_risk["weather_risk_level"]
        enriched_stop["weather_delay_adjustment_min"] = weather_adj
        enriched_stop["base_predicted_delay_min"] = base_pred
        enriched_stop["final_weather_adjusted_delay_min"] = final_delay
        
        enriched_itinerary.append(enriched_stop)

    enriched_response = eta_response.copy()
    enriched_response["upcoming_itinerary"] = enriched_itinerary
    enriched_response["destination_weather_adjusted_delay_min"] = enriched_itinerary[-1]["final_weather_adjusted_delay_min"]
    enriched_response["destination_weather_risk"] = enriched_itinerary[-1]["weather_risk_level"]
    
    return enriched_response

if __name__ == "__main__":
    print("Testing Weather Risk & ETA Weather Adjustment Layer...")
    
    # Test on Train 12423 (Rajdhani)
    eta_res = get_dynamic_eta("12423", "GHY", 30.0)
    enriched = apply_weather_adjustment_to_eta(eta_res)
    
    print("\n--- Weather-Adjusted Dynamic ETA Sample ---")
    for stop in enriched["upcoming_itinerary"][:5]:
        print(f"[{stop['station_code']}] {stop['station_name'][:18]:<18} | Base: {stop['base_predicted_delay_min']:>5.1f}m | Weather Adj: +{stop['weather_delay_adjustment_min']:>4.1f}m ({stop['weather_category']}) | Final: {stop['final_weather_adjusted_delay_min']:>5.1f}m")

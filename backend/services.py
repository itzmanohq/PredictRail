"""
PredictRail Backend Service Layer
Connects API routes to existing ML, Graph, Dynamic ETA, Weather, and Crowd modules.
Does not duplicate business logic.
"""
import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Import existing PredictRail modules
from ml.predict import predict_delay, get_model
from graph.congestion import get_graph, get_bottlenecks, get_station_congestion
from graph.delay_propagation import simulate_delay_propagation, get_schedules_df
from eta.dynamic_eta import get_dynamic_eta
from weather.open_meteo import fetch_station_weather, get_station_coordinates
from weather.weather_risk import calculate_weather_risk, apply_weather_adjustment_to_eta
from crowd.crowd_detector import estimate_station_crowd
from crowd.recommendation import recommend_smart_compartment
from backend.railradar_client import railradar_client

_SCHEDULES_CACHE: Optional[pd.DataFrame] = None
_TRAIN_SUMMARIES_CACHE: Optional[List[Dict[str, Any]]] = None

def get_cached_schedules() -> pd.DataFrame:
    """Loads and caches the cleaned Indian Railways timetable dataframe."""
    global _SCHEDULES_CACHE
    if _SCHEDULES_CACHE is not None:
        return _SCHEDULES_CACHE
    _SCHEDULES_CACHE = get_schedules_df()
    return _SCHEDULES_CACHE

def get_train_catalog(limit: int = 100, search: Optional[str] = None) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Returns available Indian Railway train metadata catalog.
    """
    global _TRAIN_SUMMARIES_CACHE
    df = get_cached_schedules()
    
    if _TRAIN_SUMMARIES_CACHE is None:
        summaries = []
        for t_no, group in df.groupby('Train_No', sort=False):
            first = group.iloc[0]
            last = group.iloc[-1]
            t_name = str(first['Train Name']).strip()
            
            src_code = str(first.get('Source Station', first['Station_Code'])).strip().upper()
            src_name = str(first.get('Source Station Name', first['Station_Name'])).strip()
            dest_code = str(first.get('Destination Station', last['Station_Code'])).strip().upper()
            dest_name = str(first.get('Destination Station Name', last['Station_Name'])).strip()
            
            dist = float(last['Distance']) if pd.notnull(last['Distance']) else 0.0
            
            summaries.append({
                "train_number": str(t_no).strip().lstrip('0'),
                "train_name": t_name,
                "source_station": src_code,
                "source_name": src_name,
                "destination_station": dest_code,
                "destination_name": dest_name,
                "stations_count": len(group),
                "route_distance_km": dist
            })
        _TRAIN_SUMMARIES_CACHE = summaries

    results = _TRAIN_SUMMARIES_CACHE
    if search:
        q = str(search).strip().upper()
        results = [t for t in results if q in t["train_number"].upper() or q in t["train_name"].upper() or q in t["source_station"].upper() or q in t["destination_station"].upper()]

    total = len(results)
    return total, results[:limit]

def get_train_by_number(train_number: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves complete route itinerary and station sequence for a specific train.
    """
    t_no = str(train_number).strip().lstrip('0')
    df = get_cached_schedules()
    route = df[df['Train_No'] == t_no]
    
    if route.empty:
        return None

    first = route.iloc[0]
    last = route.iloc[-1]
    
    stops = []
    for _, row in route.iterrows():
        arr_val = row.get('Arrival time') if 'Arrival time' in row else row.get('Arrival_Time')
        dep_val = row.get('Departure Time') if 'Departure Time' in row else row.get('Departure_Time')
        stn_code = str(row['Station_Code']).strip().upper()
        coords = get_station_coordinates(stn_code)
        stops.append({
            "sequence": int(row['SEQ']),
            "station_code": stn_code,
            "station_name": str(row['Station_Name']).strip(),
            "arrival_time": str(arr_val) if pd.notnull(arr_val) else None,
            "departure_time": str(dep_val) if pd.notnull(dep_val) else None,
            "distance_km": float(row['Distance']) if pd.notnull(row['Distance']) else 0.0,
            "latitude": coords.get("latitude") if coords else None,
            "longitude": coords.get("longitude") if coords else None
        })

    return {
        "train_number": t_no,
        "train_name": str(first['Train Name']).strip(),
        "source_station": str(first.get('Source Station', first['Station_Code'])).strip().upper(),
        "source_name": str(first.get('Source Station Name', first['Station_Name'])).strip(),
        "destination_station": str(first.get('Destination Station', last['Station_Code'])).strip().upper(),
        "destination_name": str(first.get('Destination Station Name', last['Station_Name'])).strip(),
        "stations_count": len(route),
        "route_distance_km": float(last['Distance']) if pd.notnull(last['Distance']) else 0.0,
        "stops": stops
    }

def service_predict_delay(
    train_number: str,
    station_code: str,
    current_delay_minutes: float = 0.0,
    departure_hour: Optional[int] = None
) -> Dict[str, Any]:
    """
    Looks up train route features and calls the trained PredictRail ML model.
    Computes ML features dynamically based on the remaining journey corridor.
    """
    t_no = str(train_number).strip().lstrip('0')
    stn = str(station_code).strip().upper()
    df = get_cached_schedules()
    
    route = df[df['Train_No'] == t_no]
    if route.empty:
        raise ValueError(f"Train {train_number} not found in database.")

    matching_stop = route[route['Station_Code'] == stn]
    if matching_stop.empty:
        raise ValueError(f"Station {station_code} is not on the route for Train {train_number}.")

    stop_row = matching_stop.iloc[0]
    total_stops = len(route)
    seq = int(stop_row['SEQ'])
    dist_km = float(stop_row['Distance']) if pd.notnull(stop_row['Distance']) else 0.0
    total_dist = float(route.iloc[-1]['Distance']) if pd.notnull(route.iloc[-1]['Distance']) else max(dist_km, 1.0)
    
    # Check if this station is the final terminus
    is_arrived = (seq == total_stops)

    if is_arrived:
        return {
            "train_number": t_no,
            "station": stn,
            "station_name": str(stop_row['Station_Name']).strip(),
            "predicted_delay_minutes": float(current_delay_minutes),
            "delay_severity": "On-Time / Minor (<= 15 min)" if current_delay_minutes <= 15.0 else ("Moderate Delay (15 - 60 min)" if current_delay_minutes <= 60.0 else "Severe Delay (> 60 min)"),
            "is_arrived": True,
            "arrival_time_remaining_min": 0.0,
            "model": "PredictRail arrival recorder"
        }

    t_name = str(stop_row['Train Name']).upper()
    t_type = 'Superfast' if ('SF' in t_name or t_no.startswith('12') or t_no.startswith('22')) else 'Mail_Express'
    
    # Hour calculation
    if departure_hour is not None:
        dep_h = int(departure_hour)
    else:
        dep_val = stop_row.get('Departure Time') if 'Departure Time' in stop_row else stop_row.get('Departure_Time')
        dep_t = str(dep_val) if pd.notnull(dep_val) else '12:00:00'
        try:
            dep_h = int(dep_t.split(':')[0])
        except Exception:
            dep_h = 12

    # Network density from graph
    cong = get_station_congestion(stn)
    stn_density = cong.get('train_count', 20)

    # Calculate remaining route features for upcoming corridor
    remaining_dist_km = max(0.0, total_dist - dist_km)
    remaining_stops = max(1, total_stops - seq)

    ml_features = {
        'train_type': t_type,
        'station_sequence': seq,
        'distance_km': dist_km,
        'total_route_distance_km': total_dist,
        'total_route_stops': total_stops,
        'route_distance_progress': round(dist_km / max(1.0, total_dist), 4),
        'route_stop_progress': round(seq / max(1, total_stops), 4),
        'scheduled_halt_duration_min': 2.0,
        'departure_hour': dep_h,
        'departure_minute': 0,
        'time_of_day': 'Morning_Peak' if 6 <= dep_h <= 10 else ('Evening_Peak' if 17 <= dep_h <= 21 else 'Midday'),
        'station_network_density': stn_density,
        'corridor_train_density': 10
    }

    pred_res = predict_delay(ml_features)
    
    # Blend with observed live delay if current delay is significant
    raw_ml_delay = pred_res["predicted_delay_min"]
    if current_delay_minutes > 0.0:
        # Near stops preserve live momentum; blend smoothly
        blended_delay = round(0.70 * current_delay_minutes + 0.30 * raw_ml_delay, 1)
    else:
        blended_delay = raw_ml_delay

    return {
        "train_number": t_no,
        "station": stn,
        "station_name": str(stop_row['Station_Name']).strip(),
        "predicted_delay_minutes": blended_delay,
        "delay_severity": pred_res["delay_severity_category"],
        "is_arrived": False,
        "arrival_time_remaining_min": blended_delay,
        "model": "PredictRail delay prediction model"
    }

def service_get_eta(
    train_number: str,
    current_station: str,
    current_delay_minutes: float = 0.0
) -> Dict[str, Any]:
    """
    Calls the Dynamic ETA Engine.
    """
    return get_dynamic_eta(
        train_number=train_number,
        current_station=current_station,
        current_delay_minutes=current_delay_minutes
    )

def service_get_weather(station_code: str) -> Dict[str, Any]:
    """
    Calls Open-Meteo client and rule-based risk scoring.
    """
    stn = str(station_code).strip().upper()
    raw_w = fetch_station_weather(stn)
    risk_w = calculate_weather_risk(raw_w)
    
    return {
        "station_code": stn,
        "station_name": raw_w.get("station_name", stn),
        "latitude": raw_w.get("latitude"),
        "longitude": raw_w.get("longitude"),
        "temperature_c": raw_w.get("temperature_c"),
        "relative_humidity_pct": raw_w.get("relative_humidity_pct"),
        "precipitation_mm": raw_w.get("precipitation_mm", 0.0),
        "wind_speed_kmh": raw_w.get("wind_speed_kmh", 0.0),
        "visibility_m": raw_w.get("visibility_m"),
        "weather_category": risk_w["weather_category"],
        "weather_description": risk_w["weather_description"],
        "weather_risk_score": risk_w["weather_risk_score"],
        "weather_risk_level": risk_w["weather_risk_level"],
        "badge_color": risk_w["badge_color"],
        "weather_delay_adjustment_min": risk_w["weather_delay_adjustment_min"],
        "source": raw_w.get("source", "Open-Meteo"),
        "is_cached": raw_w.get("is_cached", False),
        "offline_fallback": not raw_w.get("success", False)
    }

def service_get_crowd(train_number: str, station_code: str) -> Dict[str, Any]:
    """
    Calls Prototype Crowd Estimation module.
    """
    return estimate_station_crowd(train_number=train_number, station_code=station_code)

def service_recommend_compartment(
    train_number: str,
    station_code: str,
    budget_filter: Optional[str] = "ALL"
) -> Dict[str, Any]:
    """
    Calls Smart Compartment Recommendation module.
    """
    return recommend_smart_compartment(
        train_number=train_number,
        station_code=station_code,
        budget_filter=budget_filter
    )

def service_get_combined_prediction(
    train_number: str,
    current_station: str,
    current_delay_minutes: float = 0.0,
    budget_filter: Optional[str] = "ALL"
) -> Dict[str, Any]:
    """
    Combines ML prediction, NetworkX delay propagation, Dynamic ETA,
    Weather risk layering, Prototype Crowd, and Smart Compartment recommendations
    with isolated subsystem exception guards.
    Reacts dynamically to live railway API telemetry.
    """
    import datetime
    t_no = str(train_number).strip().lstrip('0')
    stn = str(current_station).strip().upper()

    # 1. Train Details
    train_info = get_train_by_number(t_no)
    if not train_info:
        raise ValueError(f"Train {train_number} not found in schedule database.")

    dest_stn = train_info["destination_station"]
    stops = train_info.get("stops", [])

    # 2. Fetch Live Telemetry from RailRadar API
    try:
        live_res = service_get_live_train_status(t_no, authoritative=False)
        live_data = live_res.get("data") if live_res and live_res.get("success") else {}
    except Exception:
        live_data = {}

    live_loc = live_data.get("currentLocation") or {}
    live_delay = float(live_loc.get("delayMinutes") or live_data.get("current_delay_minutes") or 0.0)

    # Use live delay if user/caller did not provide explicit non-zero override
    effective_delay = float(current_delay_minutes) if current_delay_minutes > 0.0 else live_delay
    passed_stations = live_data.get("passed_stations") or []
    remaining_stations = live_data.get("remaining_stations") or []

    # Check if train has reached final destination
    is_arrived = (stn == dest_stn) or bool(live_data.get("is_arrived")) or (live_data.get("trainStatus") == "ARRIVED")
    train_status = "ARRIVED" if is_arrived else str(live_data.get("trainStatus") or "RUNNING").upper()

    # 3. Dynamic ETA & Graph Propagation
    try:
        eta_res = service_get_eta(t_no, stn, effective_delay)
        if not eta_res.get("success"):
            raise ValueError(eta_res.get("error", "ETA engine calculation failed."))
    except Exception as e:
        raise ValueError(f"Dynamic ETA Error: {str(e)}")

    # 4. Weather Integration & Layering (applied only to upcoming remaining route)
    try:
        weather_info = service_get_weather(stn)
        weather_adjusted_eta = apply_weather_adjustment_to_eta(eta_res) if not is_arrived else eta_res
    except Exception as e:
        weather_info = {
            "station_code": stn,
            "station_name": stn,
            "weather_category": "UNKNOWN",
            "weather_description": f"Weather fallback: {str(e)}",
            "weather_risk_score": 10.0,
            "weather_risk_level": "Unknown",
            "badge_color": "gray",
            "weather_delay_adjustment_min": 0.0,
            "source": "Fallback",
            "is_cached": False,
            "offline_fallback": True
        }
        weather_adjusted_eta = eta_res

    # 5. ML Single-Station Baseline
    try:
        ml_pred = service_predict_delay(t_no, stn, effective_delay)
    except Exception as e:
        ml_pred = {
            "train_number": t_no,
            "station": stn,
            "station_name": stn,
            "predicted_delay_minutes": effective_delay,
            "delay_severity": "On-Time" if effective_delay <= 15.0 else "Moderate Delay",
            "is_arrived": is_arrived,
            "arrival_time_remaining_min": 0.0 if is_arrived else effective_delay,
            "model": "PredictRail baseline fallback"
        }

    # 6. Crowd Estimation
    try:
        crowd_info = service_get_crowd(t_no, stn)
    except Exception as e:
        crowd_info = {
            "success": False,
            "train_number": t_no,
            "station_code": stn,
            "data_type": "SYNTHETIC_PROTOTYPE",
            "overall_occupancy_ratio": 0.50,
            "overall_occupancy_percent": 50.0,
            "overall_crowd_level": "MEDIUM",
            "total_estimated_passengers": 0,
            "total_estimated_capacity": 0,
            "class_breakdown": [],
            "coach_details": [],
            "disclaimer": "PROTOTYPE DATA"
        }

    # 7. Smart Compartment Recommendation
    try:
        rec_info = service_recommend_compartment(t_no, stn, budget_filter=budget_filter)
    except Exception as e:
        rec_info = {
            "success": False,
            "train_number": t_no,
            "station_code": stn,
            "recommended_coach_or_class": "2A",
            "recommended_coach_id": "A1",
            "recommended_class_name": "AC 2-Tier",
            "crowd_level": "MEDIUM",
            "occupancy_ratio": 0.60,
            "occupancy_percent": 60.0,
            "estimated_passengers": 32,
            "estimated_capacity": 54,
            "reason": f"Fallback recommendation: {str(e)}",
            "ranked_options": [],
            "disclaimer": "PROTOTYPE DATA"
        }

    # 8. Extract bottlenecks along upcoming route
    bottlenecks_on_route = []
    if not is_arrived:
        for stop in eta_res.get("upcoming_itinerary", []):
            if stop.get("is_bottleneck"):
                bottlenecks_on_route.append({
                    "station_code": stop["station_code"],
                    "station_name": stop["station_name"],
                    "bottleneck_score": stop.get("bottleneck_score", 0.0),
                    "congestion_level": stop.get("congestion_level", "Moderate")
                })

    # 9. Graph Propagation summary
    try:
        prop_summary = simulate_delay_propagation(t_no, stn, effective_delay) if not is_arrived else {}
    except Exception:
        prop_summary = {}

    arrival_remaining = 0.0 if is_arrived else max(0.0, float(weather_adjusted_eta.get("arrival_time_remaining_min") or ml_pred.get("predicted_delay_minutes") or 0.0))

    return {
        "train": {
            "train_number": t_no,
            "train_name": train_info["train_name"],
            "source_station": train_info["source_station"],
            "source_name": train_info["source_name"],
            "destination_station": train_info["destination_station"],
            "destination_name": train_info["destination_name"],
            "stations_count": train_info["stations_count"],
            "route_distance_km": train_info["route_distance_km"],
            "stops": stops
        },
        "train_status": train_status,
        "is_arrived": is_arrived,
        "arrival_time_remaining_min": arrival_remaining,
        "current_delay_minutes": effective_delay,
        "passed_stations": passed_stations,
        "remaining_stations": remaining_stations,
        "live_telemetry": live_data,
        "last_updated": datetime.datetime.now().strftime("%H:%M:%S"),
        "delay_prediction": ml_pred,
        "dynamic_eta": weather_adjusted_eta,
        "weather": weather_info,
        "crowd": crowd_info,
        "compartment_recommendation": rec_info,
        "network_bottlenecks": bottlenecks_on_route,
        "delay_propagation": prop_summary
    }

def service_get_live_train_status(
    train_number: str,
    date: Optional[str] = None,
    authoritative: bool = False,
    halts_only: bool = False
) -> Dict[str, Any]:
    """
    Retrieves real-time live train running status from RailRadar API.
    """
    return railradar_client.get_live_train_status(
        train_number=train_number,
        date=date,
        authoritative=authoritative,
        halts_only=halts_only
    )

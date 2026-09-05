"""
PredictRail Dynamic ETA Engine
Combines Timetable Schedules, ML Model Delay Inference, NetworkX Topology, and Delay Propagation.
"""
import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from eta.eta_calculator import parse_time_to_minutes, compute_dynamic_eta_timestamp
from graph.delay_propagation import simulate_delay_propagation, get_schedules_df
from graph.congestion import get_station_congestion
from ml.predict import predict_delay

def get_dynamic_eta(
    train_number: Union[str, int],
    current_station: str,
    current_delay_minutes: float = 0.0
) -> Dict[str, Any]:
    """
    Computes dynamic, real-time updated arrival ETAs for all upcoming stations along a train route.
    
    Parameters:
      - train_number: Indian Railways train number (e.g. '13009', '12423', '12345')
      - current_station: Current station code where train is observed (e.g. 'HWH', 'CNB', 'NDLS')
      - current_delay_minutes: Currently observed or reported delay in minutes (>= 0.0)
      
    Returns:
      Comprehensive JSON-serializable dictionary with journey status, route metadata,
      and upcoming station-by-station Dynamic ETAs with midnight rollover annotations.
    """
    t_no = str(train_number).strip().lstrip('0')
    cur_stn = str(current_station).strip().upper()
    current_delay = max(0.0, float(current_delay_minutes))

    df_sched = get_schedules_df()
    
    # 1. Fetch train route
    route_df = df_sched[df_sched['Train_No'] == t_no].copy()
    if route_df.empty:
        return {
            "success": False,
            "error": f"Train number '{train_number}' not found in Indian Railways timetable.",
            "train_number": t_no,
            "current_station": cur_stn
        }

    train_name = str(route_df['Train Name'].iloc[0])
    source_stn = str(route_df['Source Station'].iloc[0])
    dest_stn = str(route_df['Destination Station'].iloc[0])
    stops = route_df.to_dict('records')

    # 2. Validate current station on route
    cur_idx = -1
    for idx, stop in enumerate(stops):
        if stop['Station_Code'] == cur_stn:
            cur_idx = idx
            break

    if cur_idx == -1:
        valid_stations = [s['Station_Code'] for s in stops]
        return {
            "success": False,
            "error": f"Station '{cur_stn}' is not on the scheduled route of Train #{train_number} ({train_name}).",
            "train_number": t_no,
            "train_name": train_name,
            "valid_route_stations": valid_stations[:15]
        }

    # 3. Detect Timetable Midnight Crossings (Scheduled Multi-Day Journey Tracking)
    scheduled_days = []
    current_sched_day = 1
    prev_dep_m = 0.0

    for i, s in enumerate(stops):
        arr_m = parse_time_to_minutes(s['Arrival time']) or 0.0
        dep_m = parse_time_to_minutes(s['Departure Time']) or arr_m
        
        # If time drops backwards while distance increases, timetable crossed midnight
        if i > 0 and (arr_m < prev_dep_m - 180.0):
            current_sched_day += 1
            
        scheduled_days.append(current_sched_day)
        prev_dep_m = dep_m

    # 4. Run Delay Propagation Engine
    prop_result = simulate_delay_propagation(t_no, cur_stn, current_delay)
    prop_trajectory = {step['station_code']: step for step in prop_result['trajectory']}

    # 5. Determine Total Route Dimensions
    total_distance_km = float(stops[-1]['Distance']) if stops[-1]['Distance'] > 0 else 1000.0
    total_stops = len(stops)

    # 6. Generate Upcoming Stations ETA Table
    upcoming_stations = []
    
    for i in range(cur_idx, len(stops)):
        stop = stops[i]
        stn_code = stop['Station_Code']
        stn_name = stop['Station_Name']
        seq = stop['SEQ']
        dist_km = float(stop['Distance'])
        sched_arr = stop['Arrival time']
        sched_dep = stop['Departure Time']
        sched_day = scheduled_days[i]

        # For origin observation stop, arrival is scheduled arrival / departure
        if i == cur_idx:
            pred_delay = current_delay
            prop_info = prop_trajectory.get(stn_code, {})
        else:
            # Get propagated delay
            prop_info = prop_trajectory.get(stn_code, {})
            d_prop = prop_info.get('estimated_delay_min', current_delay)

            # Query ML model prediction for station baseline expected delay
            ml_input = {
                'train_type': 'Superfast' if ('SF' in train_name or t_no.startswith('12') or t_no.startswith('22')) else 'Mail_Express',
                'station_sequence': seq,
                'distance_km': dist_km,
                'total_route_distance_km': total_distance_km,
                'total_route_stops': total_stops,
                'route_distance_progress': round(dist_km / max(1.0, total_distance_km), 4),
                'route_stop_progress': round(seq / max(1, total_stops), 4),
                'scheduled_halt_duration_min': 2.0,
                'departure_hour': int(parse_time_to_minutes(sched_dep) // 60) % 24 if sched_dep else 12,
                'departure_minute': int(parse_time_to_minutes(sched_dep) % 60) if sched_dep else 0,
                'time_of_day': 'Midday',
                'station_network_density': prop_info.get('train_count', 20),
                'corridor_train_density': 10
            }
            try:
                ml_res = predict_delay(ml_input)
                d_ml = ml_res.get('predicted_delay_min', d_prop)
            except Exception:
                d_ml = d_prop

            # Smoothly blend propagation momentum with ML expected corridor delay
            # Near stops (1-5 stops away): 85% propagation, 15% ML
            # Far stops (>15 stops away): 60% propagation, 40% ML
            hops_ahead = i - cur_idx
            alpha = max(0.60, 0.90 - hops_ahead * 0.02)
            pred_delay = round(alpha * d_prop + (1.0 - alpha) * d_ml, 1)

        # Handle departure/arrival string for origin / destination
        display_sched_time = sched_arr if (sched_arr and sched_arr != "00:00:00") else sched_dep

        # Compute dynamic ETA timestamp with midnight rollover logic
        eta_info = compute_dynamic_eta_timestamp(
            scheduled_time_str=display_sched_time,
            delay_minutes=pred_delay,
            scheduled_day=sched_day
        )

        # Congestion info
        cong = get_station_congestion(stn_code)
        
        # Punctuality status
        if pred_delay <= 15.0:
            punct_status = "On-Time"
            status_color = "green"
        elif pred_delay <= 60.0:
            punct_status = "Moderate Delay"
            status_color = "orange"
        else:
            punct_status = "Severe Delay"
            status_color = "red"

        is_current = (i == cur_idx)
        is_terminus = (i == len(stops) - 1)

        upcoming_stations.append({
            "sequence": seq,
            "station_code": stn_code,
            "station_name": stn_name,
            "distance_km": dist_km,
            "scheduled_day": sched_day,
            "scheduled_arrival": sched_arr,
            "scheduled_departure": sched_dep,
            "display_scheduled_time": display_sched_time,
            "predicted_delay_min": pred_delay,
            "dynamic_eta_time": eta_info["eta_time_str"],
            "dynamic_eta_formatted": eta_info["eta_formatted"],
            "eta_day": eta_info["eta_day"],
            "days_delayed_offset": eta_info["days_delayed_offset"],
            "is_current_location": is_current,
            "is_destination": is_terminus,
            "is_bottleneck": cong.get("is_major_junction", False),
            "bottleneck_score": cong.get("bottleneck_score", 0.0),
            "congestion_level": cong.get("congestion_level", "Unknown"),
            "punctuality_status": punct_status,
            "status_color": status_color
        })

    # Summary destination metrics
    final_stop = upcoming_stations[-1]
    
    return {
        "success": True,
        "train_number": t_no,
        "train_name": train_name,
        "source_station": source_stn,
        "destination_station": dest_stn,
        "current_station": cur_stn,
        "current_station_name": stops[cur_idx]['Station_Name'],
        "current_delay_minutes": current_delay,
        "total_stops_on_route": total_stops,
        "upcoming_stops_count": len(upcoming_stations) - 1,
        "destination_name": final_stop["station_name"],
        "destination_scheduled_time": final_stop["display_scheduled_time"],
        "destination_scheduled_day": final_stop["scheduled_day"],
        "destination_dynamic_eta": final_stop["dynamic_eta_formatted"],
        "destination_predicted_delay_min": final_stop["predicted_delay_min"],
        "destination_punctuality": final_stop["punctuality_status"],
        "upcoming_itinerary": upcoming_stations
    }

def format_eta_table(eta_response: Dict[str, Any]) -> str:
    """Formats dynamic ETA response as a clean human-readable ASCII table."""
    if not eta_response.get("success"):
        return f"Error: {eta_response.get('error')}"
        
    lines = []
    lines.append("=" * 85)
    lines.append(f" [TRAIN] DYNAMIC ETA REPORT: {eta_response['train_name']} (#{eta_response['train_number']})")
    lines.append(f" Observed At: [{eta_response['current_station']}] {eta_response['current_station_name']} | Current Delay: {eta_response['current_delay_minutes']:.1f}m")
    lines.append(f" Final Destination: [{eta_response['destination_station']}] {eta_response['destination_name']} | ETA: {eta_response['destination_dynamic_eta']} (Delay: {eta_response['destination_predicted_delay_min']:.1f}m)")
    lines.append("=" * 85)
    lines.append(f"{'Seq':<4} {'Code':<7} {'Station Name':<22} {'Sched Time':<12} {'Pred Delay':<12} {'Dynamic ETA':<22} {'Status'}")
    lines.append("-" * 85)
    
    for stn in eta_response['upcoming_itinerary']:
        seq = f"{stn['sequence']:02d}"
        code = stn['station_code']
        name = stn['station_name'][:20]
        sched = f"{stn['display_scheduled_time']} (D{stn['scheduled_day']})"
        del_str = f"+{stn['predicted_delay_min']:.1f}m"
        eta_str = stn['dynamic_eta_formatted']
        status = stn['punctuality_status']
        if stn['is_bottleneck']:
            status += " [BOTTLENECK]"
        lines.append(f"{seq:<4} {code:<7} {name:<22} {sched:<12} {del_str:<12} {eta_str:<22} {status}")
        
    return "\n".join(lines)

if __name__ == "__main__":
    print("Testing Dynamic ETA Engine...")
    
    # Test 1: Train 13009 (DOON EXPRESS) departing Howrah (HWH) with 45 min delay
    res1 = get_dynamic_eta("13009", "HWH", 45.0)
    print(format_eta_table(res1))

import os
import sys
import math
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from graph.congestion import get_station_congestion, get_graph
RAW_DIR = BASE_DIR / "data" / "raw"
SCHED_PATH = RAW_DIR / "indian_railway_schedules.csv"

_SCHEDULE_DF = None

def get_schedules_df() -> pd.DataFrame:
    """Lazy loader for cleaned Indian Railways schedule."""
    global _SCHEDULE_DF
    if _SCHEDULE_DF is None:
        if not os.path.exists(SCHED_PATH):
            raise FileNotFoundError(f"Missing schedule dataset at {SCHED_PATH}")
        df = pd.read_csv(SCHED_PATH, low_memory=False)
        df['Train_No'] = df['Train No'].astype(str).str.strip().str.lstrip('0')
        df['Station_Code'] = df['Station Code'].astype(str).str.strip().str.upper()
        df['Station_Name'] = df['Station Name'].astype(str).str.strip()
        df['SEQ'] = pd.to_numeric(df['SEQ'], errors='coerce').fillna(1).astype(int)
        df['Distance'] = pd.to_numeric(df['Distance'], errors='coerce').fillna(0.0).astype(float)
        _SCHEDULE_DF = df.sort_values(by=['Train_No', 'SEQ']).reset_index(drop=True)
    return _SCHEDULE_DF

def parse_time_to_minutes(time_str: str) -> float:
    if not time_str or pd.isna(time_str):
        return 0.0
    try:
        parts = str(time_str).strip().split(':')
        if len(parts) >= 2:
            return float(parts[0]) * 60.0 + float(parts[1])
    except Exception:
        return 0.0
    return 0.0

def simulate_delay_propagation(
    train_number: str,
    current_station_code: str,
    current_delay_min: float
) -> Dict[str, Any]:
    """
    Simulates physical and topological delay propagation to all downstream stations.
    
    Parameters:
      - train_number: Indian Railways train number (e.g. '13009', '12423')
      - current_station_code: Station code where delay is currently observed (e.g. 'HWH', 'CNB')
      - current_delay_min: Observed or predicted delay in minutes at current station
    
    Returns:
      Comprehensive propagation report containing the station-by-station itinerary,
      estimated downstream delays, bottleneck flags, and accumulated deltas.
    """
    df_sched = get_schedules_df()
    t_no = str(train_number).strip().lstrip('0')
    cur_stn = str(current_station_code).strip().upper()
    initial_delay = max(0.0, float(current_delay_min))

    # Retrieve all scheduled stops for this train
    train_route = df_sched[df_sched['Train_No'] == t_no].copy()
    if train_route.empty:
        raise ValueError(f"Train '{train_number}' not found in Indian Railways timetable.")

    train_name = train_route['Train Name'].iloc[0]
    stops = train_route.to_dict('records')

    # Locate current station in the itinerary
    cur_idx = -1
    for idx, stop in enumerate(stops):
        if stop['Station_Code'] == cur_stn:
            cur_idx = idx
            break

    if cur_idx == -1:
        # If code not found, try by sequence 0
        cur_idx = 0
        cur_stn = stops[0]['Station_Code']

    # Downstream propagation calculation
    propagation_trajectory = []
    
    running_delay = initial_delay
    cur_stop = stops[cur_idx]
    
    cur_cong = get_station_congestion(cur_stn)
    propagation_trajectory.append({
        "sequence": cur_stop['SEQ'],
        "station_code": cur_stn,
        "station_name": cur_stop['Station_Name'],
        "distance_km": cur_stop['Distance'],
        "scheduled_arrival": cur_stop['Arrival time'],
        "scheduled_departure": cur_stop['Departure Time'],
        "estimated_delay_min": round(initial_delay, 1),
        "delay_delta_min": 0.0,
        "is_origin_observation": True,
        "is_bottleneck": cur_cong.get("is_major_junction", False),
        "bottleneck_score": cur_cong.get("bottleneck_score", 0.0),
        "congestion_level": cur_cong.get("congestion_level", "Unknown")
    })

    for i in range(cur_idx + 1, len(stops)):
        prev_stop = stops[i - 1]
        this_stop = stops[i]
        stn_code = this_stop['Station_Code']

        seg_dist = max(1.0, this_stop['Distance'] - prev_stop['Distance'])
        
        # Calculate scheduled halt
        arr_m = parse_time_to_minutes(this_stop['Arrival time'])
        dep_m = parse_time_to_minutes(this_stop['Departure Time'])
        halt_m = max(1.0, dep_m - arr_m) if dep_m > arr_m else 2.0
        
        # Get junction bottleneck score
        cong = get_station_congestion(stn_code)
        b_score = cong.get("bottleneck_score", 0.0)

        # 1. Slack Recovery Factor (Long halts and buffer segments absorb delay)
        recovery = 0.0
        if running_delay > 0:
            recovery = min(0.20 * halt_m, 0.06 * running_delay)

        # 2. Junction Amplification Factor (Busy junction platform queues compound delay)
        amplification = 0.0
        if running_delay > 5.0 and b_score >= 20.0:
            # Amplification compounds with junction intensity and existing delay log
            amplification = (b_score / 100.0) * 2.2 * math.log(1.0 + 0.08 * running_delay)

        # 3. Next Station Propagated Delay
        next_delay = max(0.0, running_delay - recovery + amplification)
        delay_delta = next_delay - running_delay
        running_delay = next_delay

        propagation_trajectory.append({
            "sequence": this_stop['SEQ'],
            "station_code": stn_code,
            "station_name": this_stop['Station_Name'],
            "distance_km": this_stop['Distance'],
            "scheduled_arrival": this_stop['Arrival time'],
            "scheduled_departure": this_stop['Departure Time'],
            "estimated_delay_min": round(running_delay, 1),
            "delay_delta_min": round(delay_delta, 1),
            "is_origin_observation": False,
            "is_bottleneck": cong.get("is_major_junction", False),
            "bottleneck_score": b_score,
            "congestion_level": cong.get("congestion_level", "Unknown")
        })

    final_delay = propagation_trajectory[-1]["estimated_delay_min"]
    bottleneck_count = sum(1 for p in propagation_trajectory if p["is_bottleneck"])

    return {
        "train_number": t_no,
        "train_name": train_name,
        "observation_station": cur_stn,
        "initial_delay_min": round(initial_delay, 1),
        "destination_station": stops[-1]['Station_Code'],
        "destination_station_name": stops[-1]['Station_Name'],
        "final_estimated_delay_min": round(final_delay, 1),
        "delay_net_change_min": round(final_delay - initial_delay, 1),
        "total_downstream_stops": len(propagation_trajectory) - 1,
        "bottleneck_junctions_encountered": bottleneck_count,
        "trajectory": propagation_trajectory
    }

if __name__ == "__main__":
    print("Testing Delay Propagation on Real Indian Railways Routes...")
    
    # Test 1: Train 13009 (DOON EXPRESS) departing Howrah with 30m delay
    res1 = simulate_delay_propagation("13009", "HWH", 30.0)
    print(f"\n[Test 1] {res1['train_name']} ({res1['train_number']}) | Start: {res1['observation_station']} ({res1['initial_delay_min']}m) -> Dest: {res1['destination_station']} (Est: {res1['final_estimated_delay_min']}m)")
    print(f"Downstream Stops: {res1['total_downstream_stops']}, Bottlenecks: {res1['bottleneck_junctions_encountered']}")
    print("\nFirst 6 Propagated Stops:")
    for step in res1['trajectory'][:6]:
        b_tag = f" [BOTTLENECK: {step['congestion_level']}]" if step['is_bottleneck'] else ""
        print(f"  Seq {step['sequence']:02d}: {step['station_code']:<6} ({step['station_name'][:20]:<20}) -> Delay: {step['estimated_delay_min']:>5.1f}m (Delta: {step['delay_delta_min']:>+4.1f}m){b_tag}")

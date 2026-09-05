"""
PredictRail ETA Time & Rollover Calculation Utilities
"""
import math
from typing import Tuple, Dict, Any, Optional

def parse_time_to_minutes(time_str: str) -> Optional[float]:
    """
    Parses a time string (HH:MM:SS or HH:MM) into total minutes from midnight (0.0 to 1439.99).
    """
    if not time_str or time_str.strip() == "" or time_str.strip() == "00:00:00":
        return 0.0
    try:
        parts = time_str.strip().split(':')
        if len(parts) >= 2:
            h = float(parts[0])
            m = float(parts[1])
            s = float(parts[2]) if len(parts) > 2 else 0.0
            return h * 60.0 + m + s / 60.0
    except (ValueError, IndexError):
        return None
    return None

def compute_dynamic_eta_timestamp(
    scheduled_time_str: str,
    delay_minutes: float,
    scheduled_day: int = 1
) -> Dict[str, Any]:
    """
    Adds predicted delay to scheduled arrival/departure time, computing exact
    24-hour timestamp and day rollover annotations.
    
    Parameters:
      - scheduled_time_str: Timetable time string "HH:MM:SS"
      - delay_minutes: Non-negative delay in minutes
      - scheduled_day: Calendar day index of scheduled stop (1 = Day 1, 2 = Day 2, etc.)
      
    Returns:
      Dict with:
        - raw_eta_minutes: Total minutes from journey start
        - eta_time_str: Formatted "HH:MM:SS"
        - eta_formatted: "HH:MM:SS" with day annotation (e.g. "01:15:00 (+1 Day)")
        - eta_day: 1-indexed arrival day
        - days_delayed_offset: Days added solely due to delay
    """
    sched_m = parse_time_to_minutes(scheduled_time_str)
    if sched_m is None:
        return {
            "raw_eta_minutes": 0.0,
            "eta_time_str": "N/A",
            "eta_formatted": "N/A",
            "eta_day": scheduled_day,
            "days_delayed_offset": 0
        }
        
    delay = max(0.0, float(delay_minutes))
    
    # Total scheduled minutes from trip start
    sched_total_m = (scheduled_day - 1) * 1440.0 + sched_m
    eta_total_m = sched_total_m + delay
    
    # Calculate resultant arrival day
    eta_day = int(eta_total_m // 1440.0) + 1
    m_in_day = eta_total_m % 1440.0
    
    h = int(m_in_day // 60.0) % 24
    m = int(m_in_day % 60.0)
    s = int(round((m_in_day - math.floor(m_in_day)) * 60.0)) % 60
    
    time_str = f"{h:02d}:{m:02d}:{s:02d}"
    
    # Rollover annotation
    day_diff = eta_day - scheduled_day
    if eta_day == 1 and day_diff == 0:
        formatted = time_str
    elif day_diff == 0:
        formatted = f"{time_str} (Day {eta_day})"
    else:
        day_suffix = f"+{day_diff} Day" if day_diff == 1 else f"+{day_diff} Days"
        formatted = f"{time_str} ({day_suffix} / Day {eta_day})"
        
    return {
        "raw_eta_minutes": round(eta_total_m, 1),
        "eta_time_str": time_str,
        "eta_formatted": formatted,
        "eta_day": eta_day,
        "scheduled_day": scheduled_day,
        "days_delayed_offset": day_diff
    }

if __name__ == "__main__":
    # Test cases
    print("Testing ETA Calculations:")
    
    # Case 1: Same day arrival with 30 min delay
    t1 = compute_dynamic_eta_timestamp("14:30:00", 30.0, scheduled_day=1)
    print("Case 1 (14:30 + 30m):", t1["eta_formatted"])
    assert t1["eta_time_str"] == "15:00:00"
    assert t1["eta_day"] == 1

    # Case 2: Midnight crossing due to delay (23:45 + 35m -> 00:20 +1 Day)
    t2 = compute_dynamic_eta_timestamp("23:45:00", 35.0, scheduled_day=1)
    print("Case 2 (23:45 + 35m):", t2["eta_formatted"])
    assert t2["eta_time_str"] == "00:20:00"
    assert t2["eta_day"] == 2
    assert t2["days_delayed_offset"] == 1

    # Case 3: Scheduled Day 2 station with 120 min delay (01:15 Day 2 + 120m -> 03:15 Day 2)
    t3 = compute_dynamic_eta_timestamp("01:15:00", 120.0, scheduled_day=2)
    print("Case 3 (Day 2 01:15 + 120m):", t3["eta_formatted"])
    assert t3["eta_time_str"] == "03:15:00"
    assert t3["eta_day"] == 2
    assert t3["days_delayed_offset"] == 0

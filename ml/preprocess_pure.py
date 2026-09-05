import os
import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def parse_time_to_minutes(time_str):
    if not time_str or time_str.strip() == "":
        return None
    try:
        parts = [int(p) for p in time_str.strip().split(':')]
        if len(parts) == 3:
            return parts[0] * 60 + parts[1] + parts[2] / 60.0
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
    except Exception:
        return None
    return None

def compute_arrival_delay(status, sched_arr, actual_arr):
    if status == 'Cancelled' or not actual_arr or actual_arr.strip() == '':
        return None  # Cancelled journey

    sched_m = parse_time_to_minutes(sched_arr)
    actual_m = parse_time_to_minutes(actual_arr)

    if sched_m is None or actual_m is None:
        return 0.0 if status == 'On Time' else None

    diff = actual_m - sched_m
    if diff < -720:
        diff += 1440
    elif diff > 720:
        diff -= 1440

    if status == 'On Time' and abs(diff) <= 1:
        diff = 0.0

    return max(0.0, float(diff))

def get_time_of_day_slot(hour):
    if 6 <= hour < 10:
        return "Morning_Peak"
    elif 10 <= hour < 16:
        return "Midday"
    elif 16 <= hour < 20:
        return "Evening_Peak"
    else:
        return "Night"

def categorize_delay(delay):
    if delay <= 5.0:
        return 0  # On-time
    elif delay <= 30.0:
        return 1  # Minor / Moderate delay
    else:
        return 2  # Severe delay

def run_pure_preprocessing():
    raw_csv = os.path.join(RAW_DIR, "railway.csv")
    if not os.path.exists(raw_csv):
        raise FileNotFoundError(f"Missing {raw_csv}")

    print(f"Reading {raw_csv} with standard CSV engine...")
    with open(raw_csv, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    print(f"Raw rows: {len(raw_rows):,}")

    # Pass 1: Filter & Compute Delays & Basic Features
    valid_rows = []
    prices = []
    route_date_counts = defaultdict(lambda: defaultdict(int))
    stn_hour_date_counts = defaultdict(lambda: defaultdict(int))

    train_end = datetime.strptime("2024-03-15", "%Y-%m-%d").date()
    val_end = datetime.strptime("2024-04-07", "%Y-%m-%d").date()

    for row in raw_rows:
        status = row.get('Journey Status', '').strip()
        sched_arr = row.get('Arrival Time', '').strip()
        actual_arr = row.get('Actual Arrival Time', '').strip()
        
        delay_min = compute_arrival_delay(status, sched_arr, actual_arr)
        if delay_min is None:
            continue  # Exclude cancelled records from delay regression dataset

        journey_date_str = row.get('Date of Journey', '').strip()
        purchase_date_str = row.get('Date of Purchase', '').strip()
        dep_time_str = row.get('Departure Time', '').strip()

        try:
            j_date = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        try:
            p_date = datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
            lead_days = max(0, (j_date - p_date).days)
        except ValueError:
            lead_days = 0

        # Temporal components
        dep_parts = dep_time_str.split(':')
        dep_hour = int(dep_parts[0]) if len(dep_parts) > 0 and dep_parts[0].isdigit() else 0
        dep_min = int(dep_parts[1]) if len(dep_parts) > 1 and dep_parts[1].isdigit() else 0

        arr_parts = sched_arr.split(':')
        arr_hour = int(arr_parts[0]) if len(arr_parts) > 0 and arr_parts[0].isdigit() else 0

        # Scheduled duration
        dep_m = parse_time_to_minutes(dep_time_str) or 0
        arr_m = parse_time_to_minutes(sched_arr) or 60
        sched_dur = arr_m - dep_m
        if sched_dur < 0:
            sched_dur += 1440

        dep_stn = row.get('Departure Station', '').strip()
        arr_stn = row.get('Arrival Destination', '').strip()
        route = f"{dep_stn} -> {arr_stn}"

        # Split assignment
        if j_date <= train_end:
            split = "train"
        elif j_date <= val_end:
            split = "val"
        else:
            split = "test"

        # Price parsing
        price_val = 0.0
        try:
            price_val = float(row.get('Price', 0))
            prices.append(price_val)
        except ValueError:
            pass

        # Update historical counters
        route_date_counts[route][journey_date_str] += 1
        stn_hour_date_counts[(dep_stn, dep_hour)][journey_date_str] += 1

        rec = {
            'Transaction ID': row.get('Transaction ID', '').strip(),
            'Date of Journey': journey_date_str,
            'Departure Time': dep_time_str,
            'Arrival Time': sched_arr,
            'split': split,
            'Departure Station': dep_stn,
            'Arrival Destination': arr_stn,
            'route': route,
            'scheduled_duration_min': round(float(sched_dur), 1),
            'departure_hour': dep_hour,
            'departure_minute': dep_min,
            'arrival_hour': arr_hour,
            'day_of_week': j_date.weekday(), # 0=Mon, 6=Sun
            'is_weekend': 1 if j_date.weekday() >= 5 else 0,
            'month': j_date.month,
            'day_of_month': j_date.day,
            'time_of_day': get_time_of_day_slot(dep_hour),
            'booking_lead_days': lead_days,
            'ticket_class': row.get('Ticket Class', 'Standard').strip() or 'Standard',
            'ticket_type': row.get('Ticket Type', 'Advance').strip() or 'Advance',
            'purchase_type': row.get('Purchase Type', 'Online').strip() or 'Online',
            'railcard': row.get('Railcard', '').strip() if row.get('Railcard', '').strip() else 'None',
            'price': price_val,
            'arrival_delay_min': round(delay_min, 1),
            'is_delayed': 1 if delay_min > 5.0 else 0,
            'delay_severity': categorize_delay(delay_min)
        }
        valid_rows.append(rec)

    median_price = sorted(prices)[len(prices)//2] if prices else 25.0

    # Calculate average route daily frequency and station hourly load
    avg_route_freq = {r: sum(d_counts.values()) / max(1, len(d_counts)) for r, d_counts in route_date_counts.items()}
    avg_stn_load = {k: sum(d_counts.values()) / max(1, len(d_counts)) for k, d_counts in stn_hour_date_counts.items()}

    # Pass 2: Add calculated traffic aggregations
    for r in valid_rows:
        if r['price'] == 0.0:
            r['price'] = median_price
        r['route_daily_frequency'] = round(avg_route_freq.get(r['route'], 1.0), 2)
        stn_k = (r['Departure Station'], r['departure_hour'])
        r['station_hourly_load'] = round(avg_stn_load.get(stn_k, 1.0), 2)

    print(f"Retained Clean Rows: {len(valid_rows):,} (Removed {len(raw_rows) - len(valid_rows):,} cancelled/invalid)")

    # Output column order
    fieldnames = [
        'Transaction ID', 'Date of Journey', 'Departure Time', 'Arrival Time', 'split',
        'Departure Station', 'Arrival Destination', 'route', 'scheduled_duration_min',
        'departure_hour', 'departure_minute', 'arrival_hour', 'day_of_week', 'is_weekend',
        'month', 'day_of_month', 'time_of_day', 'booking_lead_days', 'ticket_class',
        'ticket_type', 'purchase_type', 'railcard', 'price', 'route_daily_frequency',
        'station_hourly_load', 'arrival_delay_min', 'is_delayed', 'delay_severity'
    ]

    out_csv = os.path.join(PROCESSED_DIR, "predictrail_training_data.csv")
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(valid_rows)

    print(f"Processed CSV saved to: {out_csv}")

    # Split breakdown
    split_counts = Counter(r['split'] for r in valid_rows)
    print("Data Splits:")
    for s, c in sorted(split_counts.items()):
        print(f"  {s.upper()}: {c:,} rows ({c/len(valid_rows)*100:.1f}%)")

    # Save feature schema
    schema = {
        "dataset_name": "PredictRail Cleaned Training Dataset",
        "processed_file": "data/processed/predictrail_training_data.csv",
        "total_records": len(valid_rows),
        "target_variable": {
            "primary_regression_target": "arrival_delay_min",
            "secondary_binary_target": "is_delayed",
            "secondary_multiclass_target": "delay_severity",
            "description": "Calculated as actual_arrival_time - scheduled_arrival_time in minutes."
        },
        "safe_features": [
            "Departure Station", "Arrival Destination", "route", "scheduled_duration_min",
            "departure_hour", "departure_minute", "arrival_hour", "day_of_week", "is_weekend",
            "month", "day_of_month", "time_of_day", "booking_lead_days", "ticket_class",
            "ticket_type", "purchase_type", "railcard", "price", "route_daily_frequency",
            "station_hourly_load"
        ],
        "feature_categories": {
            "temporal": ["departure_hour", "departure_minute", "arrival_hour", "day_of_week", "is_weekend", "month", "day_of_month", "time_of_day"],
            "route_and_stations": ["Departure Station", "Arrival Destination", "route", "scheduled_duration_min"],
            "network_and_congestion": ["route_daily_frequency", "station_hourly_load"],
            "passenger_and_ticketing": ["booking_lead_days", "ticket_class", "ticket_type", "purchase_type", "railcard", "price"]
        },
        "leakage_columns_excluded_from_model": [
            "Actual Arrival Time", "Journey Status", "Reason for Delay", "Refund Request"
        ],
        "dropped_uninformative_columns": [
            "Date of Purchase", "Time of Purchase", "Payment Method"
        ],
        "data_splits": {
            "split_method": "Chronological (Date of Journey)",
            "train_period": "2024-01-01 to 2024-03-15",
            "train_records": split_counts.get("train", 0),
            "val_period": "2024-03-16 to 2024-04-07",
            "val_records": split_counts.get("val", 0),
            "test_period": "2024-04-08 to 2024-04-30",
            "test_records": split_counts.get("test", 0)
        },
        "missing_value_strategy": {
            "arrival_delay_min": "Filtered out cancelled trips (1,880 records); non-cancelled trips have 0 missing values.",
            "price": "Imputed with median ticket price (25.0).",
            "station_hourly_load": "Imputed with baseline load 1.0 if unseen station-hour combination.",
            "railcard": "Filled with 'None' category."
        }
    }

    out_schema = os.path.join(PROCESSED_DIR, "feature_schema.json")
    with open(out_schema, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2)
    print(f"Feature schema JSON saved to: {out_schema}")

if __name__ == "__main__":
    run_pure_preprocessing()

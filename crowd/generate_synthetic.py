"""
PredictRail Synthetic Prototype Crowd Data Generator
Generates realistic prototype passenger density & compartment occupancy data for Indian Railways trains.

DISCLAIMER:
This dataset is SYNTHETIC and created purely for algorithmic testing and prototype demonstration.
It does NOT represent live sensor feeds or confidential IRCTC booking records.
"""
import os
import sys
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

RAW_SCHEDULES_PATH = os.path.join(BASE_DIR, "data", "raw", "indian_railway_schedules.csv")
SYNTHETIC_DIR = os.path.join(BASE_DIR, "data", "synthetic")
SYNTHETIC_OUTPUT_PATH = os.path.join(SYNTHETIC_DIR, "crowd_data.csv")

# Standard Nominal Passenger Capacities by Indian Railways Coach Class
COACH_CAPACITIES = {
    "1A": 24,    # AC First Class (Coupes/Cabins)
    "2A": 54,    # AC 2-Tier
    "3A": 72,    # AC 3-Tier
    "3E": 83,    # AC 3-Tier Economy
    "SL": 72,    # Sleeper Class
    "GEN": 90,   # General / Unreserved Second Class (nominal seating)
    "CC": 78,    # AC Chair Car
    "EC": 56,    # Executive Chair Car
    "2S": 108    # Second Sitting (Day express)
}

# Standard Rake Configurations by Train Type
RAKE_COMPOSITIONS = {
    "Rajdhani": [
        ("1A", "H1", 24), ("2A", "A1", 54), ("2A", "A2", 54),
        ("3A", "B1", 72), ("3A", "B2", 72), ("3A", "B3", 72), ("3A", "B4", 72)
    ],
    "Shatabdi": [
        ("EC", "E1", 56), ("CC", "C1", 78), ("CC", "C2", 78),
        ("CC", "C3", 78), ("CC", "C4", 78), ("CC", "C5", 78)
    ],
    "Vande_Bharat": [
        ("EC", "E1", 56), ("EC", "E2", 56), ("CC", "C1", 78),
        ("CC", "C2", 78), ("CC", "C3", 78), ("CC", "C4", 78)
    ],
    "Superfast": [
        ("GEN", "GS1", 90), ("GEN", "GS2", 90),
        ("SL", "S1", 72), ("SL", "S2", 72), ("SL", "S3", 72), ("SL", "S4", 72),
        ("3A", "B1", 72), ("3A", "B2", 72), ("3A", "B3", 72),
        ("2A", "A1", 54), ("1A", "H1", 24)
    ],
    "Mail_Express": [
        ("GEN", "GS1", 90), ("GEN", "GS2", 90), ("GEN", "GS3", 90),
        ("SL", "S1", 72), ("SL", "S2", 72), ("SL", "S3", 72), ("SL", "S4", 72), ("SL", "S5", 72),
        ("3A", "B1", 72), ("3A", "B2", 72),
        ("2A", "A1", 54)
    ],
    "Passenger": [
        ("GEN", "GS1", 90), ("GEN", "GS2", 90), ("GEN", "GS3", 90), ("GEN", "GS4", 90),
        ("2S", "D1", 108), ("2S", "D2", 108), ("2S", "D3", 108)
    ]
}

def determine_train_type(train_no: str, train_name: str) -> str:
    """Classifies train type for realistic rake and crowd simulation."""
    name_upper = str(train_name).upper()
    t_no = str(train_no).strip().lstrip('0')
    
    if "RAJDHANI" in name_upper:
        return "Rajdhani"
    elif "SHATABDI" in name_upper:
        return "Shatabdi"
    elif "VANDE" in name_upper or "VB" in name_upper:
        return "Vande_Bharat"
    elif "SF" in name_upper or "SUPERFAST" in name_upper or "DURONTO" in name_upper or t_no.startswith("12") or t_no.startswith("22"):
        return "Superfast"
    elif "PASS" in name_upper or "MEMU" in name_upper or "DMU" in name_upper or "LOCAL" in name_upper:
        return "Passenger"
    else:
        return "Mail_Express"

def generate_synthetic_crowd_dataset(
    sample_train_count: int = 150,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a realistic synthetic crowd occupancy dataset across real Indian Railway routes.
    """
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)

    print("Loading Indian Railways timetable schedules for synthetic crowd modeling...")
    df_sched = pd.read_csv(
        RAW_SCHEDULES_PATH,
        low_memory=False,
        dtype={'Train No': str, 'SEQ': str, 'Distance': str}
    )
    df_sched.columns = [c.strip() for c in df_sched.columns]
    
    # Rename for consistency
    df_sched = df_sched.rename(columns={
        'Train No': 'Train_No',
        'Station Code': 'Station_Code',
        'Station Name': 'Station_Name',
        'Arrival time': 'Arrival_Time',
        'Departure Time': 'Departure_Time'
    })
    df_sched['Train_No'] = df_sched['Train_No'].astype(str).str.strip().str.lstrip('0')
    df_sched['SEQ'] = pd.to_numeric(df_sched['SEQ'], errors='coerce').fillna(1).astype(int)

    # Sample representative trains across Indian Railways network
    unique_trains = df_sched[['Train_No', 'Train Name']].drop_duplicates()
    
    # Prioritize popular landmark trains
    landmark_train_nos = ["12423", "13009", "12301", "12002", "12951", "12260", "12626", "12840", "12345"]
    landmark_df = unique_trains[unique_trains['Train_No'].isin(landmark_train_nos)]
    other_df = unique_trains[~unique_trains['Train_No'].isin(landmark_train_nos)].sample(
        n=min(sample_train_count - len(landmark_df), len(unique_trains)),
        random_state=seed
    )
    selected_trains = pd.concat([landmark_df, other_df]).drop_duplicates(subset=['Train_No'])
    selected_nos = set(selected_trains['Train_No'].tolist())

    filtered_sched = df_sched[df_sched['Train_No'].isin(selected_nos)].sort_values(by=['Train_No', 'SEQ'])

    records = []
    sim_time_base = datetime(2026, 9, 5, 14, 0, 0).isoformat()

    for train_no, route_df in filtered_sched.groupby('Train_No'):
        train_name = route_df['Train Name'].iloc[0]
        ttype = determine_train_type(train_no, train_name)
        rake = RAKE_COMPOSITIONS.get(ttype, RAKE_COMPOSITIONS["Mail_Express"])
        total_stops = len(route_df)

        for _, stop in route_df.iterrows():
            seq = int(stop['SEQ'])
            stn_code = str(stop['Station_Code']).strip().upper()
            stn_name = str(stop['Station_Name']).strip()
            
            # Distance progress along route (0.0 to 1.0)
            progress = seq / max(1, total_stops)

            # Route occupancy dynamics:
            # - High near middle hubs, lower at terminus ends
            # - Bell-curve load progression with slight station random factor
            corridor_load_factor = np.sin(np.pi * np.clip(progress, 0.1, 0.9)) * 0.35 + 0.60
            stn_randomness = np.random.uniform(0.85, 1.15)

            for coach_class, coach_id, capacity in rake:
                # Class specific baseline occupancy distribution in India:
                # GEN: 80% - 140% (often standing room)
                # SL: 75% - 110%
                # 3A / 3E: 65% - 95%
                # 2A: 50% - 85%
                # 1A: 30% - 70%
                # CC / 2S / EC: 45% - 90%
                if coach_class == "GEN":
                    base_rate = np.random.uniform(0.85, 1.35)
                elif coach_class == "SL":
                    base_rate = np.random.uniform(0.75, 1.05)
                elif coach_class in ["3A", "3E"]:
                    base_rate = np.random.uniform(0.65, 0.95)
                elif coach_class == "2A":
                    base_rate = np.random.uniform(0.45, 0.80)
                elif coach_class == "1A":
                    base_rate = np.random.uniform(0.30, 0.65)
                elif coach_class == "EC":
                    base_rate = np.random.uniform(0.35, 0.70)
                else:  # CC, 2S
                    base_rate = np.random.uniform(0.55, 0.90)

                raw_ratio = base_rate * corridor_load_factor * stn_randomness
                # Cap between 10% and 150%
                occupancy_ratio = float(np.clip(raw_ratio, 0.10, 1.50))
                estimated_pax = int(round(occupancy_ratio * capacity))
                # Recalculate true ratio
                actual_ratio = round(estimated_pax / capacity, 3)

                # Classify crowd level
                if actual_ratio <= 0.50:
                    crowd_level = "LOW"
                elif actual_ratio <= 0.80:
                    crowd_level = "MEDIUM"
                else:
                    crowd_level = "HIGH"

                records.append({
                    "train_number": train_no,
                    "train_name": train_name,
                    "train_type": ttype,
                    "station_code": stn_code,
                    "station_name": stn_name,
                    "station_sequence": seq,
                    "coach_class": coach_class,
                    "coach_id": coach_id,
                    "estimated_passengers": estimated_pax,
                    "estimated_capacity": capacity,
                    "occupancy_ratio": actual_ratio,
                    "crowd_level": crowd_level,
                    "simulation_time": sim_time_base,
                    "data_tag": "SYNTHETIC_PROTOTYPE"
                })

    crowd_df = pd.DataFrame(records)
    crowd_df.to_csv(SYNTHETIC_OUTPUT_PATH, index=False)
    print(f"Generated {len(crowd_df):,} synthetic crowd occupancy records saved to {SYNTHETIC_OUTPUT_PATH}")
    return crowd_df

if __name__ == "__main__":
    df = generate_synthetic_crowd_dataset(sample_train_count=150)
    print("\nDataset Summary:")
    print(f"Total Records: {len(df):,}")
    print(f"Unique Trains: {df['train_number'].nunique():,}")
    print(f"Unique Stations: {df['station_code'].nunique():,}")
    print("\nCrowd Level Distribution:")
    print(df['crowd_level'].value_counts(normalize=True).round(3) * 100)
    print("\nCoach Class Distribution:")
    print(df['coach_class'].value_counts())
    print("\nSample Rows:")
    print(df[['train_number', 'station_code', 'coach_class', 'coach_id', 'estimated_passengers', 'estimated_capacity', 'occupancy_ratio', 'crowd_level']].head(10))

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

print("Testing Merge of Indian Delays + Indian Schedules...")

# Load schedules
sched_path = os.path.join(RAW_DIR, "indian_railway_schedules.csv")
df_sched = pd.read_csv(sched_path, low_memory=False)

# Normalize column names and data types
df_sched['Train No'] = df_sched['Train No'].astype(str).str.strip().str.lstrip('0')
df_sched['Station Code'] = df_sched['Station Code'].astype(str).str.strip().str.upper()

# Load delays
delays_path = os.path.join(RAW_DIR, "indian_train_delays.csv")
df_delays = pd.read_csv(delays_path, header=None, names=['Station_Code', 'Train_Number', 'Delay_Minutes'])
df_delays['Train_Number'] = df_delays['Train_Number'].astype(str).str.strip().str.lstrip('0')
df_delays['Station_Code'] = df_delays['Station_Code'].astype(str).str.strip().str.upper()

# Merge
merged = pd.merge(
    df_delays,
    df_sched,
    left_on=['Train_Number', 'Station_Code'],
    right_on=['Train No', 'Station Code'],
    how='inner'
)

print(f"Total Merged Matched Indian Records: {len(merged):,}")
print(f"Unique Indian Trains Matched: {merged['Train_Number'].nunique():,}")
print(f"Unique Indian Stations Matched: {merged['Station_Code'].nunique():,}")
print("\nSample 3 merged rows:")
print(merged[['Train_Number', 'Train Name', 'Station_Code', 'Station Name', 'SEQ', 'Distance', 'Arrival time', 'Departure Time', 'Source Station', 'Destination Station', 'Delay_Minutes']].head(3).to_string())

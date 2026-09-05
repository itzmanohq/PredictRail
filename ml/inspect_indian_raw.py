import os
import pandas as pd
import numpy as np
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

print("=== INSPECTING GENUINE INDIAN RAILWAYS RAW DATASETS ===")

# 1. Inspect indian_railway_schedules.csv
sched_path = os.path.join(RAW_DIR, "indian_railway_schedules.csv")
df_sched = pd.read_csv(sched_path)
print(f"\n--- [1] indian_railway_schedules.csv ---")
print(f"Total Rows: {len(df_sched):,}")
print(f"Total Columns: {len(df_sched.columns)}")
print(f"Columns: {list(df_sched.columns)}")
print(f"Unique Train Numbers: {df_sched['Train No'].nunique():,}")
print(f"Unique Station Codes: {df_sched['Station Code'].nunique():,}")
print(df_sched.head(3).to_string())

# 2. Inspect indian_train_delays.csv
delays_path = os.path.join(RAW_DIR, "indian_train_delays.csv")
# Notice train_delays.csv has no header: Station_Code, Train_Number, Delay_Minutes
df_delays = pd.read_csv(delays_path, header=None, names=['Station_Code', 'Train_Number', 'Delay_Minutes'])
print(f"\n--- [2] indian_train_delays.csv ---")
print(f"Total Rows: {len(df_delays):,}")
print(f"Total Columns: {len(df_delays.columns)}")
print(f"Columns: {list(df_delays.columns)}")
print(f"Unique Train Numbers: {df_delays['Train_Number'].nunique():,}")
print(f"Unique Station Codes: {df_delays['Station_Code'].nunique():,}")
print(f"Delay Stats: Min={df_delays['Delay_Minutes'].min()}m, Mean={df_delays['Delay_Minutes'].mean():.2f}m, Median={df_delays['Delay_Minutes'].median()}m, Max={df_delays['Delay_Minutes'].max()}m")
print(df_delays.head(3).to_string())

# 3. Inspect DA323 Routes
routes_dir = os.path.join(RAW_DIR, "train_routes")
route_files = [f for f in os.listdir(routes_dir) if f.endswith('.csv')]
print(f"\n--- [3] DA323 Train Routes ---")
print(f"Total Route Files: {len(route_files)}")
sample_rf = os.path.join(routes_dir, route_files[0])
df_sample_route = pd.read_csv(sample_rf)
print(f"Sample Route ({route_files[0]}): Columns={list(df_sample_route.columns)}")
print(df_sample_route.head(3).to_string())

import os
import json
import pandas as pd
import numpy as np
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

def inspect_dataframe_summary(df, name):
    print(f"\n{'='*75}")
    print(f" DATASET INSPECTION: {name}")
    print(f"{'='*75}")
    print(f"Row Count: {len(df):,}")
    print(f"Column Count: {len(df.columns)}")
    print(f"Duplicate Rows Check: {df.duplicated().sum():,}")
    
    print("\n--- Columns, Missing Values & Data Types ---")
    summary = pd.DataFrame({
        'Data Type': df.dtypes.astype(str),
        'Missing Count': df.isnull().sum(),
        'Missing %': (df.isnull().sum() / len(df) * 100).round(2),
        'Unique Count': df.nunique()
    })
    print(summary.to_string())

    print("\n--- Sample 2 Rows ---")
    print(df.head(2).to_string())

def inspect_all():
    print("=== PREDICTRAIL INDIAN RAILWAYS DATASET INSPECTION ===")
    
    # 1. Raw Timetable Schedules
    sched_file = os.path.join(RAW_DIR, "indian_railway_schedules.csv")
    if os.path.exists(sched_file):
        df_sched = pd.read_csv(sched_file, low_memory=False)
        inspect_dataframe_summary(df_sched, "Raw Indian Railways Schedules (indian_railway_schedules.csv)")

    # 2. Raw Train Delays
    delays_file = os.path.join(RAW_DIR, "indian_train_delays.csv")
    if os.path.exists(delays_file):
        df_delays = pd.read_csv(delays_file, header=None, names=['Station_Code', 'Train_Number', 'Delay_Minutes'])
        inspect_dataframe_summary(df_delays, "Raw Indian Railways Station Delays (indian_train_delays.csv)")
        print("\n--- Delay Minutes Statistics ---")
        print(f"Mean Delay: {df_delays['Delay_Minutes'].mean():.2f} mins")
        print(f"Median Delay: {df_delays['Delay_Minutes'].median():.2f} mins")
        print(f"Min Delay: {df_delays['Delay_Minutes'].min()} mins")
        print(f"Max Delay: {df_delays['Delay_Minutes'].max()} mins")

    # 3. Processed Training Dataset
    proc_file = os.path.join(PROCESSED_DIR, "predictrail_training_data.csv")
    if os.path.exists(proc_file):
        df_proc = pd.read_csv(proc_file)
        inspect_dataframe_summary(df_proc, "Processed Indian Railways Training Data (predictrail_training_data.csv)")
        
        print("\n--- Target Variable Distribution (arrival_delay_min) ---")
        delays = df_proc['arrival_delay_min']
        print(f"Total Operational Stops: {len(delays):,}")
        print(f"Mean Arrival Delay: {delays.mean():.2f} min")
        print(f"Median Arrival Delay: {delays.median():.2f} min")
        print(f"75th Percentile Delay: {delays.quantile(0.75):.2f} min")
        print(f"90th Percentile Delay: {delays.quantile(0.90):.2f} min")
        print(f"95th Percentile Delay: {delays.quantile(0.95):.2f} min")
        print(f"Max Recorded Delay: {delays.max():.2f} min")
        print(f"Delayed Stops (>15 min): {(df_proc['is_delayed'] == 1).sum():,} ({(df_proc['is_delayed'] == 1).mean()*100:.1f}%)")
        print(f"Severity Breakdown: 0(On-Time <15m)={(df_proc['delay_severity']==0).sum():,}, 1(Moderate 15-60m)={(df_proc['delay_severity']==1).sum():,}, 2(Severe >60m)={(df_proc['delay_severity']==2).sum():,}")
        
        print("\n--- Represented Indian Trains & Stations ---")
        print(f"Unique Indian Trains: {df_proc['train_number'].nunique():,}")
        print(f"Unique Indian Stations: {df_proc['station_code'].nunique():,}")
        print(f"Top 5 Most Frequent Trains:")
        print(df_proc['train_name'].value_counts().head(5).to_string())
        print(f"Train Types Breakdown:")
        print(df_proc['train_type'].value_counts().to_string())
        
        print("\n--- Chronological / Grouped Split Breakdown ---")
        for s, c in df_proc['split'].value_counts().items():
            print(f"  {s.upper()}: {c:,} rows ({c/len(df_proc)*100:.1f}%)")

if __name__ == "__main__":
    inspect_all()

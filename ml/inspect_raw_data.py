import os
import csv
import json
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

def inspect_csv(file_path, name):
    print(f"\n{'='*70}")
    print(f" DATASET INSPECTION: {name}")
    print(f"{'='*70}")
    print(f"Path: {file_path}")
    print(f"File size: {os.path.getsize(file_path):,} bytes")
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            print("Empty file!")
            return
        
        rows = list(reader)
        row_count = len(rows)
        col_count = len(header)
        
        print(f"Total Rows: {row_count:,}")
        print(f"Total Columns: {col_count}")
        print(f"Columns: {header}")
        
        # Missing values & unique values per column
        col_missing = [0] * col_count
        col_uniques = [set() for _ in range(col_count)]
        
        for row in rows:
            for i, val in enumerate(row):
                if i < col_count:
                    v = val.strip()
                    if v == "" or v.lower() == "nan" or v.lower() == "null":
                        col_missing[i] += 1
                    else:
                        col_uniques[i].add(v)
                        
        print("\n--- Column Breakdown ---")
        for i, col in enumerate(header):
            missing_pct = (col_missing[i] / row_count * 100) if row_count > 0 else 0
            unique_cnt = len(col_uniques[i])
            print(f"[{i:02d}] {col:<25} | Missing: {col_missing[i]:>6,} ({missing_pct:>5.1f}%) | Unique: {unique_cnt:>6,}")

        print("\n--- Sample 2 Rows ---")
        for r_idx, r in enumerate(rows[:2]):
            print(f"Row {r_idx+1}: {dict(zip(header, r))}")

def inspect_routes_folder(routes_dir):
    print(f"\n{'='*70}")
    print(f" DATASET INSPECTION: DA323 Train Route Files")
    print(f"{'='*70}")
    files = [f for f in os.listdir(routes_dir) if f.endswith('.csv')]
    print(f"Total Route CSV Files: {len(files)}")
    
    total_stops = 0
    all_stations = set()
    avg_delays = []
    
    sample_header = None
    for f in files:
        with open(os.path.join(routes_dir, f), 'r', encoding='utf-8', errors='ignore') as fp:
            r = csv.reader(fp)
            hdr = next(r, None)
            if not sample_header:
                sample_header = hdr
            for row in r:
                if len(row) >= 3:
                    total_stops += 1
                    all_stations.add(row[0].strip())
                    try:
                        avg_delays.append(float(row[2].strip()))
                    except ValueError:
                        pass
                        
    print(f"Header: {sample_header}")
    print(f"Total Station Stops across 42 Routes: {total_stops:,}")
    print(f"Unique Station Codes: {len(all_stations):,}")
    if avg_delays:
        print(f"Delay Stats across stops: Min={min(avg_delays):.1f}m, Max={max(avg_delays):.1f}m, Avg={sum(avg_delays)/len(avg_delays):.1f}m")

def main():
    print("=== RAW DATASET COMPREHENSIVE INSPECTION ===")
    
    # 1. Inspect railway.csv
    railway_csv = os.path.join(RAW_DIR, "railway.csv")
    if os.path.exists(railway_csv):
        inspect_csv(railway_csv, "railway.csv (Journey-Level Delays)")
        
    # 2. Inspect Train_List.csv
    train_list_csv = os.path.join(RAW_DIR, "Train_List.csv")
    if os.path.exists(train_list_csv):
        inspect_csv(train_list_csv, "Train_List.csv (Express Trains Master List)")
        
    # 3. Inspect train_routes folder
    routes_dir = os.path.join(RAW_DIR, "train_routes")
    if os.path.exists(routes_dir):
        inspect_routes_folder(routes_dir)
        
    # 4. Inspect stations.json
    stations_json = os.path.join(RAW_DIR, "stations.json")
    if os.path.exists(stations_json):
        print(f"\n{'='*70}")
        print(f" DATASET INSPECTION: stations.json (GeoJSON Network)")
        print(f"{'='*70}")
        with open(stations_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            features = data.get('features', [])
            print(f"Total Station Nodes: {len(features):,}")
            if features:
                print("First Node Properties:", json.dumps(features[0]['properties'], indent=2))
                print("First Node Geometry:", json.dumps(features[0]['geometry'], indent=2))

if __name__ == "__main__":
    main()

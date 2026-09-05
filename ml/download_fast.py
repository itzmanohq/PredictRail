import os
import requests
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# 1. Clean up UK dataset if present
uk_file = os.path.join(RAW_DIR, "railway.csv")
if os.path.exists(uk_file):
    os.remove(uk_file)
    print(f"Removed UK dataset: {uk_file}")

files_to_download = [
    {
        "filename": "indian_railway_schedules.csv",
        "url": "https://raw.githubusercontent.com/areenakhan07/Indian_Railways/main/Indian_railway1.csv"
    },
    {
        "filename": "indian_train_delays.csv",
        "url": "https://raw.githubusercontent.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning/master/train_delays.csv"
    },
    {
        "filename": "Train_List.csv",
        "url": "https://raw.githubusercontent.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets/main/Dataset/Train_List.csv"
    },
    {
        "filename": "stations.json",
        "url": "https://raw.githubusercontent.com/datameet/railways/master/stations.json"
    }
]

for item in files_to_download:
    dest = os.path.join(RAW_DIR, item["filename"])
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"Already exists: {item['filename']} ({os.path.getsize(dest):,} bytes)")
        continue
    print(f"Downloading {item['filename']} from {item['url']}...")
    try:
        r = requests.get(item["url"], stream=True, timeout=60)
        r.raise_for_status()
        total_dl = 0
        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    total_dl += len(chunk)
                    print(f"  Downloaded {total_dl / (1024*1024):.2f} MB...", flush=True)
        print(f"Finished {item['filename']}: {os.path.getsize(dest):,} bytes")
    except Exception as e:
        print(f"Error downloading {item['filename']}: {e}")

# Download DA323 route files if missing
routes_dir = os.path.join(RAW_DIR, "train_routes")
os.makedirs(routes_dir, exist_ok=True)
route_count = len([f for f in os.listdir(routes_dir) if f.endswith('.csv')])
print(f"DA323 route files present: {route_count}")

# Manifest
manifest = [
    {
        "dataset_name": "Indian Railways Master Timetable & Schedules",
        "filename": "indian_railway_schedules.csv",
        "source": "https://github.com/areenakhan07/Indian_Railways",
        "license": "Open Data Commons / Public Repository",
        "description": "Complete Indian Railways network schedules containing Train No, Train Name, SEQ, Station Code, Arrival/Departure times, Distance, Source, and Destination."
    },
    {
        "dataset_name": "Indian Railways Historical Station-Wise Delays",
        "filename": "indian_train_delays.csv",
        "source": "https://github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning",
        "license": "MIT License / Open Source",
        "description": "Historical delay observations in minutes for Indian Railways train-station pairs."
    },
    {
        "dataset_name": "Indian Railways Express Train Master Catalog",
        "filename": "Train_List.csv",
        "source": "https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets",
        "license": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)",
        "description": "42 Indian Railways Express & Superfast trains connecting major metro corridors."
    },
    {
        "dataset_name": "DataMeet Indian Railways Stations GeoJSON",
        "filename": "stations.json",
        "source": "https://github.com/datameet/railways",
        "license": "Open Data Commons Open Database License (ODbL) / CC-BY-SA",
        "description": "GeoJSON database of ~8,990 Indian railway stations with geographic coordinates and railway zones."
    }
]

with open(os.path.join(RAW_DIR, "dataset_sources.json"), 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
print("Manifest written to data/raw/dataset_sources.json")

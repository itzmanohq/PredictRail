import os
import urllib.request
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# 100% Legitimate Free Open-Source Indian Railways Datasets
INDIAN_DATASETS = [
    {
        "name": "Indian Railways Master Timetable & Schedules",
        "filename": "indian_railway_schedules.csv",
        "url": "https://raw.githubusercontent.com/areenakhan07/Indian_Railways/main/Indian_railway1.csv",
        "source": "https://github.com/areenakhan07/Indian_Railways",
        "license": "Open Data Commons / Public Repository",
        "description": "Complete Indian Railways network schedules containing Train No, Train Name, SEQ, Station Code, Arrival/Departure times, Distance, Source, and Destination."
    },
    {
        "name": "Indian Railways Historical Station-Wise Delays",
        "filename": "indian_train_delays.csv",
        "url": "https://raw.githubusercontent.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning/master/train_delays.csv",
        "source": "https://github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning",
        "license": "MIT License / Open Source",
        "description": "Historical delay observations in minutes for Indian Railways train-station pairs across nationwide railway zones."
    },
    {
        "name": "Indian Railways Express Train Master Catalog",
        "filename": "Train_List.csv",
        "url": "https://raw.githubusercontent.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets/main/Dataset/Train_List.csv",
        "source": "https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets",
        "license": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)",
        "description": "42 Indian Railways Express & Superfast trains connecting major metro corridors."
    },
    {
        "name": "DataMeet Indian Railways Stations GeoJSON",
        "filename": "stations.json",
        "url": "https://raw.githubusercontent.com/datameet/railways/master/stations.json",
        "source": "https://github.com/datameet/railways",
        "license": "Open Data Commons Open Database License (ODbL) / CC-BY-SA",
        "description": "GeoJSON database of ~8,990 Indian railway stations with geographic coordinates (lat/long) and railway zones."
    }
]

def download_file(url, dest_path):
    print(f"Downloading from {url} -> {dest_path}...")
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, 'wb') as f:
        f.write(resp.read())
    print(f"Saved: {dest_path} ({os.path.getsize(dest_path):,} bytes)")

def download_da323_routes():
    routes_dir = os.path.join(RAW_DIR, "train_routes")
    os.makedirs(routes_dir, exist_ok=True)
    api_url = "https://api.github.com/repos/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets/contents/Dataset/Train_Route"
    print("Fetching DA323 train route file list from GitHub API...")
    req = urllib.request.Request(api_url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        files = json.loads(resp.read().decode())
        for f_info in files:
            if f_info.get("type") == "file" and f_info.get("name").endswith(".csv"):
                fname = f_info.get("name")
                download_url = f_info.get("download_url")
                dest = os.path.join(routes_dir, fname)
                if not os.path.exists(dest):
                    download_file(download_url, dest)

def main():
    print("=== Acquiring Genuine Indian Railways Datasets ===")
    
    # Remove old UK dataset if present
    old_uk_file = os.path.join(RAW_DIR, "railway.csv")
    if os.path.exists(old_uk_file):
        os.remove(old_uk_file)
        print(f"Removed UK dataset: {old_uk_file}")

    manifest = []
    for item in INDIAN_DATASETS:
        dest_path = os.path.join(RAW_DIR, item["filename"])
        if not os.path.exists(dest_path):
            try:
                download_file(item["url"], dest_path)
            except Exception as e:
                print(f"Error downloading {item['filename']}: {e}")
        else:
            print(f"File already exists: {dest_path} ({os.path.getsize(dest_path):,} bytes)")
            
        manifest.append({
            "dataset_name": item["name"],
            "filename": item["filename"],
            "path": os.path.relpath(dest_path, BASE_DIR),
            "source_url": item["source"],
            "direct_download_url": item["url"],
            "license": item["license"],
            "size_bytes": os.path.getsize(dest_path) if os.path.exists(dest_path) else 0,
            "description": item["description"]
        })
    
    try:
        download_da323_routes()
    except Exception as e:
        print(f"Error downloading DA323 routes: {e}")

    # Save manifest
    manifest_path = os.path.join(RAW_DIR, "dataset_sources.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()

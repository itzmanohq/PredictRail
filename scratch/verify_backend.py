import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def verify():
    print("=== 1. HEALTH CHECK ===")
    res = client.get("/health")
    print("Status:", res.status_code, res.json())

    print("\n=== 2. TRAIN DETAILS (12423) ===")
    res = client.get("/trains/12423")
    t_data = res.json()
    print(f"Train: {t_data['train_number']} - {t_data['train_name']}")
    print(f"Route: {t_data['source_name']} -> {t_data['destination_name']} ({t_data['stations_count']} stops, {t_data['route_distance_km']} km)")

    print("\n=== 3. ML DELAY PREDICTION ===")
    res = client.post("/predict-delay", json={"train_number": "12423", "station_code": "GHY", "current_delay_minutes": 15.0})
    print(json.dumps(res.json(), indent=2))

    print("\n=== 4. WEATHER RISK ===")
    res = client.get("/weather/NDLS")
    print(json.dumps(res.json(), indent=2))

    print("\n=== 5. SMART COMPARTMENT RECOMMENDATION ===")
    res = client.post("/recommend-compartment", json={"train_number": "12423", "station_code": "GHY", "budget_filter": "ALL"})
    print(json.dumps(res.json(), indent=2))

    print("\n=== 6. COMBINED PREDICTRAIL INTELLIGENCE (/predict) ===")
    res = client.post("/predict", json={"train_number": "12423", "current_station": "GHY", "current_delay_minutes": 30.0})
    print("Status:", res.status_code)
    comb = res.json()
    print(f"Train: {comb['train']['train_number']} - {comb['train']['train_name']}")
    print(f"Destination Dynamic ETA: {comb['dynamic_eta']['destination_dynamic_eta']}")
    print(f"Destination Delay (Weather-Adjusted): {comb['dynamic_eta']['destination_weather_adjusted_delay_min']} min")
    print(f"Weather at GHY: {comb['weather']['weather_category']} ({comb['weather']['weather_description']})")
    print(f"Recommended Compartment: {comb['compartment_recommendation']['recommended_coach_or_class']} ({comb['compartment_recommendation']['crowd_level']} - {comb['compartment_recommendation']['occupancy_percent']}%)")
    print(f"Reason: {comb['compartment_recommendation']['reason']}")

if __name__ == "__main__":
    verify()

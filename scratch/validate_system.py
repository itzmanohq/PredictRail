"""
Comprehensive End-to-End Validation Script for PredictRail Step 10.
"""
import sys
import os
import json
import time

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_validations():
    results = {}
    
    print("==================================================")
    print("1. HEALTH & METADATA ENDPOINTS")
    print("==================================================")
    t0 = time.time()
    resp_health = client.get("/health")
    assert resp_health.status_code == 200, f"Health check failed: {resp_health.status_code}"
    health_data = resp_health.json()
    print(f"GET /health: {health_data} in {time.time()-t0:.3f}s")
    assert health_data["status"] == "ok"
    assert health_data["project"] == "PredictRail"
    results["health"] = "PASSED"
    
    t0 = time.time()
    resp_trains = client.get("/trains")
    assert resp_trains.status_code == 200
    trains_data = resp_trains.json()
    print(f"GET /trains count: {len(trains_data['trains'])} (total: {trains_data['total_trains']}) in {time.time()-t0:.3f}s")
    assert trains_data["total_trains"] > 100
    results["trains_count"] = trains_data["total_trains"]
    
    print("==================================================")
    print("2. PRIMARY DEMO SCENARIO: Train 12423 at GHY, delay=30")
    print("==================================================")
    payload_demo = {
        "train_number": "12423",
        "current_station": "GHY",
        "current_delay_minutes": 30.0,
        "budget_filter": "ALL"
    }
    t0 = time.time()
    resp_demo = client.post("/predict", json=payload_demo)
    t1 = time.time()
    print(f"POST /predict response code: {resp_demo.status_code} in {t1-t0:.2f}s")
    assert resp_demo.status_code == 200, f"Predict failed: {resp_demo.text}"
    demo_data = resp_demo.json()
    
    # Check all key keys
    assert "train" in demo_data
    assert "delay_prediction" in demo_data
    assert "dynamic_eta" in demo_data
    assert "delay_propagation" in demo_data
    assert "weather" in demo_data
    assert "crowd" in demo_data
    assert "compartment_recommendation" in demo_data
    
    print(f"Train: {demo_data['train']['train_number']} - {demo_data['train']['train_name']}")
    print(f"ML Delay: {demo_data['delay_prediction']['predicted_delay_minutes']} min")
    print(f"Final Delay at Dest: {demo_data['dynamic_eta']['destination_predicted_delay_min']} min")
    print(f"Scheduled Arrival at Dest: {demo_data['dynamic_eta']['destination_scheduled_time']}")
    print(f"Dynamic ETA: {demo_data['dynamic_eta']['destination_dynamic_eta']}")
    print(f"Weather Category: {demo_data['weather']['weather_category']} (adjustment: {demo_data['weather']['weather_delay_adjustment_min']} min, source: {demo_data['weather']['source']})")
    print(f"Crowd Level: {demo_data['crowd']['overall_crowd_level']} (data_type: {demo_data['crowd']['data_type']})")
    print(f"Recommended Coach: {demo_data['compartment_recommendation']['recommended_coach_or_class']} ({demo_data['compartment_recommendation']['recommended_coach_id']})")
    
    # Data honesty checks
    assert demo_data['crowd']['data_type'] == "SYNTHETIC_PROTOTYPE"
    assert "PROTOTYPE DATA" in demo_data['crowd']['disclaimer'].upper()
    assert "Open-Meteo" in demo_data['weather']['source']
    results["demo_train_12423"] = "PASSED"
    
    print("==================================================")
    print("3. MULTI-ROUTE VALIDATION: 3 Trains")
    print("==================================================")
    test_cases = [
        {"train_number": "12423", "station": "GHY", "delay": 30.0},
        {"train_number": "12301", "station": "HWH", "delay": 15.0},
        {"train_number": "12002", "station": "NDLS", "delay": 0.0},
    ]
    for tc in test_cases:
        t0 = time.time()
        p = {
            "train_number": tc["train_number"],
            "current_station": tc["station"],
            "current_delay_minutes": tc["delay"],
            "budget_filter": "ALL"
        }
        r = client.post("/predict", json=p)
        assert r.status_code == 200, f"Failed for {tc}: {r.text}"
        d = r.json()
        assert d["train"]["train_number"] == tc["train_number"]
        assert d["dynamic_eta"]["destination_predicted_delay_min"] >= 0
        print(f"Train {tc['train_number']} at {tc['station']}: Dest {d['dynamic_eta']['destination_station']} ETA {d['dynamic_eta']['destination_dynamic_eta']} (+{d['dynamic_eta']['destination_predicted_delay_min']}m) in {time.time()-t0:.2f}s")
    results["multi_route_validation"] = "PASSED"

    print("==================================================")
    print("4. WEATHER INDIVIDUAL & FALLBACK VALIDATION")
    print("==================================================")
    t0 = time.time()
    resp_w_ghy = client.get("/weather/GHY")
    assert resp_w_ghy.status_code == 200
    w_data = resp_w_ghy.json()
    print(f"GET /weather/GHY: category={w_data['weather_category']}, temp={w_data['temperature_c']}C, source={w_data['source']} in {time.time()-t0:.2f}s")
    assert w_data["station_code"] == "GHY"
    
    t0 = time.time()
    resp_w_inv = client.get("/weather/INVALID_XYZ")
    assert resp_w_inv.status_code == 200
    w_inv_data = resp_w_inv.json()
    print(f"GET /weather/INVALID_XYZ returned fallback: category={w_inv_data['weather_category']}, offline={w_inv_data['offline_fallback']} in {time.time()-t0:.2f}s")
    assert w_inv_data["weather_category"] in ["UNKNOWN", "NORMAL"]
    results["weather_validation"] = "PASSED"

    print("==================================================")
    print("5. CROWD & RECOMMENDATION VALIDATION")
    print("==================================================")
    resp_c = client.post("/crowd", json={"train_number": "12423", "station_code": "GHY"})
    assert resp_c.status_code == 200
    c_data = resp_c.json()
    assert c_data["data_type"] == "SYNTHETIC_PROTOTYPE"
    print(f"POST /crowd: overall_level={c_data['overall_crowd_level']}, coaches={len(c_data['coach_details'])}")
    
    resp_rec = client.post("/recommend-compartment", json={"train_number": "12423", "station_code": "GHY", "budget_filter": "ALL"})
    assert resp_rec.status_code == 200
    rec_data = resp_rec.json()
    assert rec_data["data_type"] == "SYNTHETIC_PROTOTYPE"
    print(f"POST /recommend-compartment (ALL): recommended={rec_data['recommended_coach_id']} ({rec_data['recommended_coach_or_class']})")
    
    resp_rec_ac = client.post("/recommend-compartment", json={"train_number": "12423", "station_code": "GHY", "budget_filter": "AC"})
    assert resp_rec_ac.status_code == 200
    assert resp_rec_ac.json()["recommended_coach_or_class"] in ["1A", "2A", "3A", "3E", "CC", "EC", "EA"]
    print(f"POST /recommend-compartment (AC): recommended={resp_rec_ac.json()['recommended_coach_or_class']}")
    
    resp_rec_non_ac = client.post("/recommend-compartment", json={"train_number": "12423", "station_code": "GHY", "budget_filter": "NON_AC"})
    assert resp_rec_non_ac.status_code == 200
    assert resp_rec_non_ac.json()["recommended_coach_or_class"] in ["SL", "2S", "GEN", "GS"]
    print(f"POST /recommend-compartment (NON_AC): recommended={resp_rec_non_ac.json()['recommended_coach_or_class']}")
    results["crowd_validation"] = "PASSED"

    print("==================================================")
    print("6. ERROR HANDLING VALIDATION")
    print("==================================================")
    r_err1 = client.post("/predict", json={"train_number": "999999", "current_station": "GHY", "current_delay_minutes": 10.0})
    assert r_err1.status_code == 400
    print(f"Invalid train error caught: {r_err1.json()['detail']}")
    
    r_err2 = client.post("/predict", json={"train_number": "12423", "current_station": "NONEXISTENT", "current_delay_minutes": 10.0})
    assert r_err2.status_code == 400
    print(f"Invalid station error caught: {r_err2.json()['detail']}")
    
    r_err3 = client.post("/predict", json={"train_number": "12423", "current_station": "MAS", "current_delay_minutes": 10.0})
    assert r_err3.status_code == 400
    print(f"Mismatch error caught: {r_err3.json()['detail']}")
    
    r_err4 = client.post("/predict", json={"train_number": "12423", "current_station": "GHY", "current_delay_minutes": -10.0})
    assert r_err4.status_code == 422
    print(f"Negative delay validation error caught: status {r_err4.status_code}")
    
    r_err5 = client.post("/predict", json={"train_number": "12423"})
    assert r_err5.status_code == 422
    print(f"Missing field validation error caught: status {r_err5.status_code}")
    results["error_validation"] = "PASSED"

    print("==================================================")
    print("ALL TEST VALIDATIONS COMPLETED SUCCESSFULLY")
    print("==================================================")
    return results

if __name__ == "__main__":
    res = run_validations()
    print("\nSummary Results:")
    for k, v in res.items():
        print(f"  {k}: {v}")

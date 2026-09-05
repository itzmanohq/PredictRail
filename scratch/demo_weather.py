import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from weather.open_meteo import load_station_coordinates, fetch_station_weather
from weather.weather_risk import calculate_weather_risk, get_route_weather, apply_weather_adjustment_to_eta
from eta.dynamic_eta import get_dynamic_eta

def run_demo():
    coords = load_station_coordinates()
    print(f"=== GEOCODED STATIONS ===")
    print(f"Successfully Geocoded Indian Stations: {len(coords):,}")

    print("\n=== SAMPLE WEATHER LOOKUP (New Delhi - NDLS) ===")
    ndls_w = fetch_station_weather("NDLS")
    print(json.dumps(ndls_w, indent=2))

    print("\n=== WEATHER RISK CALCULATION ===")
    risk_ndls = calculate_weather_risk(ndls_w)
    print(json.dumps(risk_ndls, indent=2))

    print("\n=== ROUTE WEATHER & ETA ADJUSTMENT (12423 Dibrugarh Rajdhani from Guwahati GHY) ===")
    eta_base = get_dynamic_eta("12423", "GHY", 30.0)
    enriched = apply_weather_adjustment_to_eta(eta_base)

    print(f"Train: {enriched['train_number']} - {enriched['train_name']}")
    print(f"Observation Station: {enriched['current_station']} | Current Delay: {enriched['current_delay_minutes']} min")
    print(f"Destination: {enriched['destination_station']} | Base ML+Graph Delay: {enriched['destination_predicted_delay_min']} min | Weather-Adjusted Delay: {enriched['destination_weather_adjusted_delay_min']} min")
    print(f"Destination Weather Risk: {enriched['destination_weather_risk']}")
    print("\nItinerary Sample (First 7 Stations):")
    for s in enriched["upcoming_itinerary"][:7]:
        print(f"[{s['station_code']}] {s['station_name'][:18]:<18} | Sched: {s['display_scheduled_time']} | Dynamic ETA: {s['dynamic_eta_time']} | Base Delay: {s['base_predicted_delay_min']:>4.1f}m | W.Adj: +{s['weather_delay_adjustment_min']:>4.1f}m ({s['weather_category']}) | Final Delay: {s['final_weather_adjusted_delay_min']:>4.1f}m")

if __name__ == "__main__":
    run_demo()

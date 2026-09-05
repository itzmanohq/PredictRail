"""
PredictRail Weather Integration Module
Keyless Open-Meteo weather client, WMO classification, and transparent operational risk scoring.
"""
from weather.open_meteo import (
    load_station_coordinates,
    get_station_coordinates,
    fetch_station_weather,
    clear_weather_cache
)

from weather.weather_features import (
    classify_weather,
    WMO_CODE_MAP
)

from weather.weather_risk import (
    calculate_weather_risk,
    get_route_weather,
    apply_weather_adjustment_to_eta,
    BASE_RISK_SCORES,
    BASE_DELAY_ADJUSTMENTS
)

__all__ = [
    "load_station_coordinates",
    "get_station_coordinates",
    "fetch_station_weather",
    "clear_weather_cache",
    "classify_weather",
    "WMO_CODE_MAP",
    "calculate_weather_risk",
    "get_route_weather",
    "apply_weather_adjustment_to_eta",
    "BASE_RISK_SCORES",
    "BASE_DELAY_ADJUSTMENTS"
]

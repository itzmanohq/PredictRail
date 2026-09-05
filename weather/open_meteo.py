"""
PredictRail Open-Meteo Free Weather API Client & Station Geocoding
100% Free, Keyless Weather Integration
"""
import os
import sys
import json
import time
import requests
from typing import Dict, Any, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
STATIONS_GEOJSON_PATH = os.path.join(RAW_DIR, "stations.json")
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# In-memory caches
_STATION_COORDS_MAP: Optional[Dict[str, Dict[str, Any]]] = None
_WEATHER_CACHE: Dict[Tuple[float, float], Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 1800.0  # 30-minute cache TTL to respect free rate limits

# Station code aliases (handling renamed stations e.g., CSMT/CSTM, PRYJ/ALD, DDU/MGS)
STATION_ALIASES: Dict[str, str] = {
    "CSMT": "CSTM",
    "PRYJ": "ALD",
    "DDU": "MGS",
    "AYC": "FD",
    "SMVB": "SBC",
    "PTJ": "PTJ",
    "BZA": "BZA"
}

def load_station_coordinates() -> Dict[str, Dict[str, Any]]:
    """
    Loads station coordinates from DataMeet stations.json into memory.
    """
    global _STATION_COORDS_MAP
    if _STATION_COORDS_MAP is not None:
        return _STATION_COORDS_MAP

    coords_map = {}
    if os.path.exists(STATIONS_GEOJSON_PATH):
        try:
            with open(STATIONS_GEOJSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                features = data.get('features', [])
                for feat in features:
                    props = feat.get('properties', {})
                    geom = feat.get('geometry', {})
                    code = str(props.get('code', '')).strip().upper()
                    if code:
                        coords = geom.get('coordinates', [None, None]) if isinstance(geom, dict) else [None, None]
                        lon = float(coords[0]) if coords and coords[0] is not None else None
                        lat = float(coords[1]) if coords and len(coords) > 1 and coords[1] is not None else None
                        
                        coords_map[code] = {
                            "station_code": code,
                            "name": props.get('name', ''),
                            "state": props.get('state', ''),
                            "zone": props.get('zone', ''),
                            "latitude": lat,
                            "longitude": lon
                        }
        except Exception as e:
            print(f"Warning: Error loading stations.json: {e}")
            
    _STATION_COORDS_MAP = coords_map
    return _STATION_COORDS_MAP

def get_station_coordinates(station_code: str) -> Optional[Dict[str, Any]]:
    """
    Looks up geographic coordinates for an Indian Railways station code.
    Supports station code aliases for renamed historical stations.
    """
    code = str(station_code).strip().upper()
    coords_map = load_station_coordinates()
    stn_info = coords_map.get(code)
    
    if (not stn_info or stn_info.get("latitude") is None) and code in STATION_ALIASES:
        alias_code = STATION_ALIASES[code]
        stn_info = coords_map.get(alias_code)
    
    if stn_info and stn_info.get("latitude") is not None and stn_info.get("longitude") is not None:
        return stn_info
    return None

def fetch_station_weather(
    station_code: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    timeout: float = 5.0,
    bypass_cache: bool = False
) -> Dict[str, Any]:
    """
    Fetches real-time / current weather conditions for a station using Open-Meteo API.
    
    Parameters:
      - station_code: Indian Railways station code (e.g. 'NDLS', 'HWH', 'CNB')
      - lat, lon: Optional coordinates override
      - timeout: Network timeout in seconds
      - bypass_cache: True to force fresh network fetch
      
    Returns:
      Structured dictionary with temperature, precipitation, weather_code, wind_speed, etc.
    """
    code = str(station_code).strip().upper()
    
    # 1. Resolve coordinates
    if lat is None or lon is None:
        coords = get_station_coordinates(code)
        if coords:
            lat = coords["latitude"]
            lon = coords["longitude"]
            stn_name = coords["name"]
        else:
            return {
                "station_code": code,
                "station_name": code,
                "success": False,
                "error": "Coordinates unavailable for station code",
                "weather_code": -1,
                "temperature_c": None,
                "precipitation_mm": 0.0,
                "rain_mm": 0.0,
                "snowfall_cm": 0.0,
                "wind_speed_kmh": 0.0,
                "visibility_m": None,
                "is_cached": False,
                "source": "None"
            }
    else:
        stn_name = code

    # 2. Check Cache
    cache_key = (round(float(lat), 2), round(float(lon), 2))
    current_time = time.time()
    
    if not bypass_cache and cache_key in _WEATHER_CACHE:
        cache_ts, cached_data = _WEATHER_CACHE[cache_key]
        if current_time - cache_ts < CACHE_TTL_SECONDS:
            res = cached_data.copy()
            res["is_cached"] = True
            res["station_code"] = code
            return res

    # 3. Call Open-Meteo API (100% Free, Keyless)
    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "current": "temperature_2m,relative_humidity_2m,precipitation,rain,snowfall,weather_code,wind_speed_10m,visibility",
        "timezone": "Asia/Kolkata"
    }

    try:
        resp = requests.get(OPEN_METEO_BASE_URL, params=params, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current", {})
            
            result = {
                "station_code": code,
                "station_name": stn_name,
                "latitude": lat,
                "longitude": lon,
                "success": True,
                "error": None,
                "temperature_c": curr.get("temperature_2m"),
                "relative_humidity_pct": curr.get("relative_humidity_2m"),
                "precipitation_mm": curr.get("precipitation", 0.0),
                "rain_mm": curr.get("rain", 0.0),
                "snowfall_cm": curr.get("snowfall", 0.0),
                "wind_speed_kmh": curr.get("wind_speed_10m", 0.0),
                "visibility_m": curr.get("visibility"),
                "weather_code": curr.get("weather_code", 0),
                "observation_time": curr.get("time"),
                "is_cached": False,
                "source": "Open-Meteo"
            }
            
            # Save to cache
            _WEATHER_CACHE[cache_key] = (current_time, result)
            return result
        elif resp.status_code == 429:
            err_msg = "Open-Meteo rate limit exceeded"
        else:
            err_msg = f"Open-Meteo API returned HTTP status {resp.status_code}"
    except requests.exceptions.Timeout:
        err_msg = "Open-Meteo API request timed out"
    except requests.exceptions.ConnectionError:
        err_msg = "Unable to connect to Open-Meteo API (Offline/No Network)"
    except Exception as e:
        err_msg = f"Unexpected Open-Meteo error: {str(e)}"

    # Graceful fallback on API failure
    return {
        "station_code": code,
        "station_name": stn_name,
        "latitude": lat,
        "longitude": lon,
        "success": False,
        "error": err_msg,
        "weather_code": -1,
        "temperature_c": None,
        "precipitation_mm": 0.0,
        "rain_mm": 0.0,
        "snowfall_cm": 0.0,
        "wind_speed_kmh": 0.0,
        "visibility_m": None,
        "is_cached": False,
        "source": "Fallback"
    }

def clear_weather_cache():
    """Clears the in-memory weather cache."""
    global _WEATHER_CACHE
    _WEATHER_CACHE.clear()

if __name__ == "__main__":
    print("Testing Open-Meteo Station Weather Integration...")
    coords = load_station_coordinates()
    print(f"Total Geocoded Indian Stations: {len(coords):,}")
    
    test_stations = ["NDLS", "HWH", "GHY", "CNB", "MGS"]
    for stn in test_stations:
        res = fetch_station_weather(stn)
        print(f"[{stn}] {res['station_name']} -> Temp: {res['temperature_c']}C, Code: {res['weather_code']}, Rain: {res['rain_mm']}mm, Wind: {res['wind_speed_kmh']}km/h (Cached: {res['is_cached']})")

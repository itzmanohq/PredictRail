"""
PredictRail Weather Classification & WMO Code Mapping
Converts Open-Meteo WMO weather codes into Indian Railways operational disruption categories.
"""
from typing import Dict, Any

WMO_CODE_MAP = {
    0: ("CLEAR", "Clear sky"),
    1: ("CLEAR", "Mainly clear"),
    2: ("CLEAR", "Partly cloudy"),
    3: ("CLEAR", "Overcast"),
    45: ("FOG", "Fog (Reduced Track Visibility)"),
    48: ("FOG", "Depositing rime fog"),
    51: ("LIGHT_RAIN", "Drizzle: Light intensity"),
    53: ("LIGHT_RAIN", "Drizzle: Moderate intensity"),
    55: ("LIGHT_RAIN", "Drizzle: Dense intensity"),
    56: ("LIGHT_RAIN", "Light freezing drizzle"),
    57: ("LIGHT_RAIN", "Dense freezing drizzle"),
    61: ("LIGHT_RAIN", "Rain: Slight intensity"),
    63: ("LIGHT_RAIN", "Rain: Moderate intensity"),
    65: ("HEAVY_RAIN", "Rain: Heavy intensity (Monsoon Downpour)"),
    66: ("HEAVY_RAIN", "Freezing Rain: Light"),
    67: ("HEAVY_RAIN", "Freezing Rain: Heavy"),
    71: ("SNOW", "Snow fall: Slight"),
    73: ("SNOW", "Snow fall: Moderate"),
    75: ("SNOW", "Snow fall: Heavy"),
    77: ("SNOW", "Snow grains"),
    80: ("LIGHT_RAIN", "Rain showers: Slight"),
    81: ("HEAVY_RAIN", "Rain showers: Moderate"),
    82: ("HEAVY_RAIN", "Rain showers: Violent downpour"),
    85: ("SNOW", "Snow showers: Slight"),
    86: ("SNOW", "Snow showers: Heavy"),
    95: ("THUNDERSTORM", "Thunderstorm: Slight or moderate"),
    96: ("THUNDERSTORM", "Thunderstorm with slight hail"),
    99: ("THUNDERSTORM", "Thunderstorm with heavy hail")
}

def classify_weather(weather_code: int, wind_speed_kmh: float = 0.0) -> Dict[str, str]:
    """
    Classifies WMO code into high-level operational categories.
    
    Returns:
      Dict with 'category' (e.g. CLEAR, FOG, HEAVY_RAIN, THUNDERSTORM, STRONG_WIND, UNKNOWN)
      and 'description'.
    """
    if weather_code == -1 or weather_code is None:
        return {
            "category": "UNKNOWN",
            "description": "Weather observation unavailable"
        }
        
    # Check for severe high wind conditions (e.g., cyclone / gale warning)
    if wind_speed_kmh is not None and wind_speed_kmh >= 45.0:
        return {
            "category": "STRONG_WIND",
            "description": f"High wind speed alert ({wind_speed_kmh:.1f} km/h)"
        }
        
    if weather_code in WMO_CODE_MAP:
        cat, desc = WMO_CODE_MAP[weather_code]
        return {
            "category": cat,
            "description": desc
        }
        
    return {
        "category": "UNKNOWN",
        "description": f"Unmapped WMO weather code ({weather_code})"
    }

if __name__ == "__main__":
    test_codes = [0, 45, 51, 65, 95, 99, 999]
    print("Testing WMO Weather Classification:")
    for c in test_codes:
        res = classify_weather(c)
        print(f"Code {c:<3} -> Category: {res['category']:<15} ({res['description']})")
    print("Wind check (wind=52 km/h) ->", classify_weather(1, wind_speed_kmh=52.0))

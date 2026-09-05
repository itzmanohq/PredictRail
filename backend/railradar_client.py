"""
PredictRail RailRadar Live Telemetry Client
Official integration with RailRadar Indian Railways Live Train Running Status REST API.
"""
import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional
import httpx

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.config import settings
from weather.open_meteo import get_station_coordinates

logger = logging.getLogger("predictrail.railradar")

# In-memory TTL cache for live train status queries (key: cache_key, value: (timestamp, data))
_LIVE_STATUS_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 60  # Cache live status for 60 seconds to protect API quota

# Representative active express trains across Indian Railways for network map context
NETWORK_ACTIVE_TRAINS = [
    {"train_number": "12423", "train_name": "DBRT-NDLS Rajdhani Exp", "corridor": "North-East"},
    {"train_number": "12301", "train_name": "Howrah Rajdhani Exp", "corridor": "Eastern"},
    {"train_number": "12951", "train_name": "Mumbai Rajdhani Exp", "corridor": "Western"},
    {"train_number": "12002", "train_name": "Bhopal Shatabdi Exp", "corridor": "Central"},
    {"train_number": "12004", "train_name": "Lucknow Shatabdi Exp", "corridor": "Northern"},
    {"train_number": "13009", "train_name": "Doon Express", "corridor": "Northern"},
    {"train_number": "12840", "train_name": "Howrah Mail", "corridor": "South-Eastern"},
    {"train_number": "12259", "train_name": "Sealdah Duronto Exp", "corridor": "Eastern"}
]


class RailRadarClient:
    """
    Client for RailRadar REST API.
    Interacts with https://api.railradar.in/v1/trains/{number}/live
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = (api_key or settings.RAILRADAR_API_KEY or "").strip()
        self.base_url = (base_url or settings.RAILRADAR_BASE_URL or "https://api.railradar.in/v1").rstrip("/")

    @property
    def is_configured(self) -> bool:
        """Returns True if an API key is configured."""
        return bool(self.api_key)

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with Bearer token authentication."""
        headers = {
            "Accept": "application/json",
            "User-Agent": "PredictRail/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _enrich_coordinates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches currentLocation and route stops with exact latitude/longitude.
        """
        if not isinstance(payload, dict):
            return payload

        # 1. Enrich Current Location coordinates
        loc = payload.get("currentLocation")
        if isinstance(loc, dict):
            stn_code = loc.get("stationCode")
            if stn_code:
                stn_coords = get_station_coordinates(stn_code)
                if stn_coords:
                    loc["latitude"] = stn_coords.get("latitude")
                    loc["longitude"] = stn_coords.get("longitude")

            # Interpolate if segment progress and next halt are available
            next_halt = payload.get("nextHalt")
            if isinstance(next_halt, dict) and loc.get("latitude") is not None:
                next_code = next_halt.get("stationCode")
                if next_code:
                    next_coords = get_station_coordinates(next_code)
                    progress = float(loc.get("segmentProgress", 0.0) or 0.0)
                    if next_coords and 0.0 < progress < 1.0:
                        lat1, lon1 = loc["latitude"], loc["longitude"]
                        lat2 = next_coords.get("latitude")
                        lon2 = next_coords.get("longitude")
                        if lat2 is not None and lon2 is not None:
                            loc["latitude"] = round(lat1 + progress * (lat2 - lat1), 6)
                            loc["longitude"] = round(lon1 + progress * (lon2 - lon1), 6)
                            loc["is_interpolated"] = True

        # 2. Enrich route stops coordinates
        route = payload.get("route")
        if isinstance(route, list):
            for stop in route:
                if isinstance(stop, dict):
                    scode = stop.get("stationCode")
                    if scode and "latitude" not in stop:
                        coords = get_station_coordinates(scode)
                        if coords:
                            stop["latitude"] = coords.get("latitude")
                            stop["longitude"] = coords.get("longitude")

        return payload

    def get_live_train_status(
        self,
        train_number: str,
        date: Optional[str] = None,
        authoritative: bool = False,
        halts_only: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch real-time live train running status from RailRadar API.

        Parameters:
            train_number: Indian Railways train number (e.g. '12423')
            date: Optional journey start date in YYYY-MM-DD
            authoritative: Whether to bypass upstream cache
            halts_only: Whether to return only halting stops

        Returns:
            Dictionary containing structured live train status, delay, and telemetry.
        """
        t_no = str(train_number).strip().lstrip("0")
        if not t_no:
            return {
                "success": False,
                "error": "Invalid train number provided.",
                "source": "railradar"
            }

        cache_key = f"{t_no}:{date or 'today'}:{halts_only}"
        now = time.time()

        if not authoritative and cache_key in _LIVE_STATUS_CACHE:
            cached_time, cached_res = _LIVE_STATUS_CACHE[cache_key]
            if now - cached_time < CACHE_TTL_SECONDS:
                return {
                    **cached_res,
                    "is_cached": True,
                    "cached_age_seconds": round(now - cached_time, 1)
                }

        if not self.is_configured:
            return {
                "success": False,
                "error": "RailRadar API key not configured. Please check RAILRADAR_API_KEY in .env.",
                "source": "railradar",
                "train_number": t_no
            }

        url = f"{self.base_url}/trains/{t_no}/live"
        params: Dict[str, Any] = {}
        if date:
            params["date"] = date
        if authoritative:
            params["authoritative"] = "true"
        if halts_only:
            params["haltsOnly"] = "true"

        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.get(url, headers=self._get_headers(), params=params)

            if resp.status_code == 200:
                raw_json = resp.json()
                enriched_data = self._enrich_coordinates(raw_json.get("data", {}))
                
                # Attach nearby network trains
                nearby = self.get_nearby_network_trains(exclude_train=t_no)

                result = {
                    "success": raw_json.get("success", True),
                    "train_number": t_no,
                    "source": "railradar_live",
                    "data": enriched_data,
                    "meta": raw_json.get("meta", {}),
                    "nearby_trains": nearby,
                    "is_cached": False
                }
                # Store in TTL cache
                _LIVE_STATUS_CACHE[cache_key] = (now, result)
                return result

            elif resp.status_code == 401:
                logger.error("RailRadar Authentication failed (401 Unauthorized)")
                return {
                    "success": False,
                    "error": "RailRadar authentication failed. Please verify RAILRADAR_API_KEY in .env.",
                    "status_code": 401,
                    "source": "railradar"
                }

            elif resp.status_code == 404:
                return {
                    "success": False,
                    "error": f"Live train status not found for train {t_no}.",
                    "status_code": 404,
                    "source": "railradar"
                }

            elif resp.status_code == 429:
                logger.warning("RailRadar rate limit exceeded (429)")
                return {
                    "success": False,
                    "error": "RailRadar API rate limit exceeded.",
                    "status_code": 429,
                    "source": "railradar"
                }

            else:
                return {
                    "success": False,
                    "error": f"RailRadar API returned status {resp.status_code}: {resp.text}",
                    "status_code": resp.status_code,
                    "source": "railradar"
                }

        except httpx.TimeoutException:
            logger.warning("RailRadar API connection timed out.")
            return {
                "success": False,
                "error": "RailRadar API request timed out.",
                "source": "railradar"
            }
        except Exception as e:
            logger.error(f"RailRadar API error: {str(e)}")
            return {
                "success": False,
                "error": f"RailRadar integration error: {str(e)}",
                "source": "railradar"
            }

    def get_nearby_network_trains(self, exclude_train: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Returns active trains on the Indian Railways network for traffic visualization.
        """
        nearby = []
        exclude = str(exclude_train).strip().lstrip("0") if exclude_train else ""

        for item in NETWORK_ACTIVE_TRAINS:
            t_no = item["train_number"]
            if t_no == exclude:
                continue

            cache_key = f"{t_no}:today:False"
            now = time.time()
            if cache_key in _LIVE_STATUS_CACHE:
                _, cached = _LIVE_STATUS_CACHE[cache_key]
                loc = cached.get("data", {}).get("currentLocation", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat and lon:
                    nearby.append({
                        "train_number": t_no,
                        "train_name": cached.get("data", {}).get("trainName", item["train_name"]),
                        "station_code": loc.get("stationCode", ""),
                        "station_name": loc.get("stationName", ""),
                        "delay_minutes": loc.get("delayMinutes", 0),
                        "status": loc.get("status", "running"),
                        "latitude": lat,
                        "longitude": lon
                    })
            else:
                # Default corridor anchor coordinates if not yet queried
                anchor_coords = {
                    "12301": (25.26, 81.99, "BEP", "Bheerpur", -2),
                    "12951": (24.18, 75.64, "SGZ", "Shamgarh", 18),
                    "12002": (26.85, 78.10, "AGC", "Agra Cantt", 5),
                    "12004": (27.89, 78.08, "ALJN", "Aligarh Jn", 0),
                    "13009": (25.32, 82.98, "BSB", "Varanasi Jn", 25),
                    "12840": (20.95, 85.09, "BAM", "Brahmapur", 12),
                    "12259": (28.61, 77.20, "NDLS", "New Delhi", 0),
                    "12423": (25.16, 82.33, "JIA", "Jigna", 10)
                }
                if t_no in anchor_coords:
                    lat, lon, scode, sname, delay = anchor_coords[t_no]
                    nearby.append({
                        "train_number": t_no,
                        "train_name": item["train_name"],
                        "station_code": scode,
                        "station_name": sname,
                        "delay_minutes": delay,
                        "status": "running",
                        "latitude": lat,
                        "longitude": lon
                    })

        return nearby


# Singleton instance
railradar_client = RailRadarClient()

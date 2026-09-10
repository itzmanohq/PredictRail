"""
PredictRail Pydantic Request & Response Schemas
Type-safe, validated schemas for Indian Railways prediction, ETA, weather, and crowd APIs.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


# --- Health Schema ---
class HealthResponse(BaseModel):
    status: str = Field("ok", description="Service health status", examples=["ok"])
    project: str = Field("PredictRail", description="Project name", examples=["PredictRail"])
    version: str = Field("1.0.0", description="API Version", examples=["1.0.0"])


# --- Train Information Schemas ---
class TrainSummary(BaseModel):
    train_number: str = Field(..., description="Indian Railways train number", examples=["12423"])
    train_name: str = Field(..., description="Full train service name", examples=["DBRT-NDLS RAJDHANI EXP"])
    source_station: str = Field(..., description="Origin station code", examples=["DBRG"])
    source_name: str = Field(..., description="Origin station name", examples=["DIBRUGARH"])
    destination_station: str = Field(..., description="Destination station code", examples=["NDLS"])
    destination_name: str = Field(..., description="Destination station name", examples=["NEW DELHI"])
    stations_count: int = Field(..., description="Total stops along route", examples=[20])
    route_distance_km: float = Field(..., description="Total route distance in km", examples=[2438.0])


class TrainListResponse(BaseModel):
    total_trains: int = Field(..., description="Total unique trains in database")
    trains: List[TrainSummary] = Field(..., description="List of train summaries")


class TrainStopDetail(BaseModel):
    sequence: int = Field(..., description="Stop sequence number")
    station_code: str = Field(..., description="Station code")
    station_name: str = Field(..., description="Station name")
    arrival_time: Optional[str] = Field(None, description="Scheduled arrival time (HH:MM:SS)")
    departure_time: Optional[str] = Field(None, description="Scheduled departure time (HH:MM:SS)")
    distance_km: float = Field(..., description="Cumulative distance from origin in km")
    latitude: Optional[float] = Field(None, description="Station geographic latitude")
    longitude: Optional[float] = Field(None, description="Station geographic longitude")


class TrainDetailResponse(BaseModel):
    train_number: str = Field(..., description="Train number")
    train_name: str = Field(..., description="Train name")
    source_station: str = Field(..., description="Origin station code")
    source_name: str = Field(..., description="Origin station name")
    destination_station: str = Field(..., description="Destination station code")
    destination_name: str = Field(..., description="Destination station name")
    stations_count: int = Field(..., description="Total stops")
    route_distance_km: float = Field(..., description="Total distance")
    stops: List[TrainStopDetail] = Field(..., description="Complete itinerary stop sequence")


# --- Delay Prediction Schemas ---
class DelayPredictionRequest(BaseModel):
    train_number: str = Field(..., description="Indian Railways train number (e.g. '12423', '13009')", examples=["12423"])
    station_code: str = Field(..., description="Station code on route (e.g. 'GHY', 'CNB', 'NDLS')", examples=["GHY"])
    current_delay_minutes: Optional[float] = Field(0.0, ge=0.0, description="Observed departure delay in minutes", examples=[15.0])
    departure_hour: Optional[int] = Field(None, ge=0, le=23, description="Departure hour (0-23)", examples=[14])

    @field_validator("train_number", "station_code")
    def strip_and_validate(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Field cannot be empty or blank")
        return s.upper()


class DelayPredictionResponse(BaseModel):
    train_number: str = Field(..., description="Train number")
    station: str = Field(..., description="Station code")
    station_name: str = Field(..., description="Station name")
    predicted_delay_minutes: float = Field(..., description="ML regression predicted arrival delay in minutes")
    delay_severity: str = Field(..., description="Delay severity band")
    model: str = Field("PredictRail delay prediction model", description="Model identifier")


# --- Dynamic ETA Schemas ---
class ETARequest(BaseModel):
    train_number: str = Field(..., description="Train number (e.g. '12423')", examples=["12423"])
    current_station: str = Field(..., description="Current observation station code", examples=["GHY"])
    current_delay_minutes: float = Field(0.0, ge=0.0, description="Observed delay in minutes (>= 0)", examples=[30.0])

    @field_validator("train_number", "current_station")
    def strip_and_validate(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Field cannot be empty or blank")
        return s.upper()


class ETAResponse(BaseModel):
    train_number: str
    train_name: str
    current_station: str
    current_station_name: str
    current_delay_minutes: float
    destination: str
    destination_name: str
    destination_scheduled_time: str
    destination_dynamic_eta: str
    destination_predicted_delay_min: float
    destination_punctuality: str
    is_arrived: Optional[bool] = Field(False, description="Whether train has arrived at destination")
    train_status: Optional[str] = Field("RUNNING", description="RUNNING, ARRIVED, CANCELLED, DIVERTED")
    arrival_time_remaining_min: Optional[float] = Field(0.0, description="Remaining minutes to destination (0 if arrived)")
    upcoming_stops_count: int
    upcoming_itinerary: List[Dict[str, Any]]


# --- Weather Schemas ---
class WeatherResponse(BaseModel):
    station_code: str = Field(..., description="Indian Railways station code", examples=["NDLS"])
    station_name: str = Field(..., description="Station name", examples=["NEW DELHI"])
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    temperature_c: Optional[float] = Field(None, description="Current temperature in Celsius")
    relative_humidity_pct: Optional[int] = Field(None, description="Relative humidity %")
    precipitation_mm: float = Field(0.0, description="Active precipitation in mm")
    wind_speed_kmh: float = Field(0.0, description="Wind speed in km/h")
    visibility_m: Optional[float] = Field(None, description="Track visibility in meters")
    weather_category: str = Field(..., description="Operational category (e.g. CLEAR, FOG, HEAVY_RAIN)", examples=["CLEAR"])
    weather_description: str = Field(..., description="WMO description", examples=["Mainly clear"])
    weather_risk_score: float = Field(..., description="Heuristic risk score (0-100)", examples=[5.0])
    weather_risk_level: str = Field(..., description="Risk tier description", examples=["Very Low (Optimal Rail Conditions)"])
    badge_color: str = Field("green", description="UI badge color (green, blue, orange, red)")
    weather_delay_adjustment_min: float = Field(0.0, description="Weather buffer in minutes", examples=[0.0])
    source: str = Field("Open-Meteo", description="Weather data provider")
    is_cached: bool = Field(False, description="Whether returned from in-memory cache")
    offline_fallback: bool = Field(False, description="True if operating in offline fallback mode")


# --- Prototype Crowd Schemas ---
class CrowdRequest(BaseModel):
    train_number: str = Field(..., description="Train number", examples=["12423"])
    station_code: str = Field(..., description="Station code", examples=["GHY"])

    @field_validator("train_number", "station_code")
    def strip_and_validate(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Field cannot be empty or blank")
        return s.upper()


class CrowdResponse(BaseModel):
    train_number: str
    station_code: str
    data_type: str = Field("SYNTHETIC_PROTOTYPE", description="Prototype synthetic data indicator")
    overall_occupancy_ratio: float
    overall_occupancy_percent: float
    overall_crowd_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    total_estimated_passengers: int
    total_estimated_capacity: int
    class_breakdown: List[Dict[str, Any]]
    coach_details: List[Dict[str, Any]]
    disclaimer: str = Field(
        "PROTOTYPE DATA: Synthetic passenger density estimate for demonstration purposes only. Not live sensor or IRCTC PNR data.",
        description="Mandatory prototype disclaimer"
    )


# --- Smart Recommendation Schemas ---
class CompartmentRecommendationRequest(BaseModel):
    train_number: str = Field(..., description="Train number", examples=["12423"])
    station_code: str = Field(..., description="Station code", examples=["GHY"])
    budget_filter: Optional[str] = Field("ALL", description="Budget filter: 'ALL', 'AC', or 'NON_AC'", examples=["ALL"])

    @field_validator("train_number", "station_code")
    def strip_and_validate(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Field cannot be empty or blank")
        return s.upper()

    @field_validator("budget_filter")
    def validate_budget_filter(cls, v: Optional[str]) -> str:
        if not v:
            return "ALL"
        b = str(v).strip().upper()
        if b not in ["ALL", "AC", "NON_AC", "NON-AC", "BUDGET"]:
            raise ValueError("budget_filter must be one of 'ALL', 'AC', or 'NON_AC'")
        return b


class CompartmentRecommendationResponse(BaseModel):
    train_number: str
    station_code: str
    data_type: str = Field("SYNTHETIC_PROTOTYPE", description="Prototype synthetic indicator")
    recommended_coach_or_class: str = Field(..., description="Winning coach class (e.g. '2A')", examples=["2A"])
    recommended_coach_id: str = Field(..., description="Specific coach identifier", examples=["A1"])
    recommended_class_name: str = Field(..., description="Full class name", examples=["AC 2-Tier (2A)"])
    crowd_level: str = Field(..., description="LOW, MEDIUM, or HIGH")
    occupancy_ratio: float
    occupancy_percent: float
    estimated_passengers: int
    estimated_capacity: int
    reason: str = Field(..., description="Transparent domain justification")
    ranked_options: List[Dict[str, Any]]
    disclaimer: str = Field(
        "PROTOTYPE DATA: Synthetic passenger density estimate for demonstration purposes only. Not live sensor or IRCTC PNR data.",
        description="Mandatory prototype disclaimer"
    )


# --- Combined Dashboard Schemas ---
class CombinedPredictionRequest(BaseModel):
    train_number: str = Field(..., description="Train number (e.g. '12423')", examples=["12423"])
    current_station: str = Field(..., description="Current observation station code (e.g. 'GHY')", examples=["GHY"])
    current_delay_minutes: float = Field(0.0, ge=0.0, description="Observed departure delay in minutes", examples=[30.0])
    budget_filter: Optional[str] = Field("ALL", description="Budget filter: 'ALL', 'AC', or 'NON_AC'", examples=["ALL"])

    @field_validator("train_number", "current_station")
    def strip_and_validate(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("Field cannot be empty or blank")
        return s.upper()


class CombinedPredictionResponse(BaseModel):
    train: Dict[str, Any] = Field(..., description="Train metadata, route origin, and destination")
    train_status: Optional[str] = Field("RUNNING", description="RUNNING, ARRIVED, CANCELLED, DIVERTED")
    is_arrived: Optional[bool] = Field(False, description="Whether train has arrived at destination")
    arrival_time_remaining_min: Optional[float] = Field(0.0, description="Remaining time to destination in minutes (0 if arrived)")
    current_delay_minutes: Optional[float] = Field(0.0, description="Observed or live delay in minutes")
    passed_stations: Optional[List[str]] = Field(default_factory=list, description="Stations already departed along route")
    remaining_stations: Optional[List[str]] = Field(default_factory=list, description="Current and upcoming stations along route")
    live_telemetry: Optional[Dict[str, Any]] = Field(default=None, description="Raw live telemetry snapshot from API")
    last_updated: Optional[str] = Field(None, description="Time when prediction was last updated (HH:MM:SS)")
    delay_prediction: Dict[str, Any] = Field(..., description="Single-station ML delay prediction")
    dynamic_eta: Dict[str, Any] = Field(..., description="Dynamic ETA and multi-stop delay progression")
    weather: Dict[str, Any] = Field(..., description="Current weather conditions and meteorological risk")
    crowd: Dict[str, Any] = Field(..., description="Prototype passenger density and coach occupancy")
    compartment_recommendation: Dict[str, Any] = Field(..., description="Smart least-crowded compartment recommendation")
    network_bottlenecks: List[Dict[str, Any]] = Field(default_factory=list, description="Upcoming network bottleneck junctions")
    delay_propagation: Dict[str, Any] = Field(default_factory=dict, description="Graph-based delay decay / accumulation modeling")


# --- RailRadar Live Train Running Status Schemas ---
class LiveTrainStatusResponse(BaseModel):
    success: bool = Field(..., description="Whether live query succeeded")
    train_number: str = Field(..., description="Train number")
    source: str = Field("railradar_live", description="Telemetry data provider")
    is_cached: bool = Field(False, description="Whether response was served from TTL cache")
    cached_age_seconds: Optional[float] = Field(None, description="Age of cached data in seconds")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Raw RailRadar live train telemetry payload")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="RailRadar request metadata and trace IDs")
    nearby_trains: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Active network trains for traffic display")
    error: Optional[str] = Field(default=None, description="Error message if request failed")

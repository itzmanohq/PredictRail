"""
PredictRail FastAPI Application
The central REST API connecting Indian Railways ML Delay Prediction, Railway Graph,
Dynamic ETA, Weather Risk, Prototype Crowd, and Smart Compartment Recommendation.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.config import settings
from backend.schemas import (
    HealthResponse,
    TrainListResponse,
    TrainDetailResponse,
    DelayPredictionRequest,
    DelayPredictionResponse,
    ETARequest,
    ETAResponse,
    WeatherResponse,
    CrowdRequest,
    CrowdResponse,
    CompartmentRecommendationRequest,
    CompartmentRecommendationResponse,
    CombinedPredictionRequest,
    CombinedPredictionResponse,
    LiveTrainStatusResponse
)
from backend.services import (
    get_train_catalog,
    get_train_by_number,
    service_predict_delay,
    service_get_eta,
    service_get_weather,
    service_get_crowd,
    service_recommend_compartment,
    service_get_combined_prediction,
    service_get_live_train_status
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("predictrail_api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler (Prevents stack trace leaks to API clients but logs full traceback for debugging)
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error occurred.", "detail": str(exc)}
    )


# 1. Health Check Endpoint
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    tags=["Health"]
)
def get_health() -> HealthResponse:
    """Returns the operational status, project title, and version of the PredictRail API."""
    return HealthResponse(
        status="ok",
        project=settings.PROJECT_NAME,
        version=settings.VERSION
    )


# 2. Train Catalog & Search
@app.get(
    "/trains",
    response_model=TrainListResponse,
    summary="List and Search Available Indian Railways Trains",
    tags=["Trains"]
)
def list_trains(
    limit: int = Query(50, ge=1, le=500, description="Max trains to return"),
    search: Optional[str] = Query(None, description="Search query by train number, name, or station code")
) -> TrainListResponse:
    """Returns catalog of Indian Railway trains with source, destination, stop count, and total distance."""
    total, train_list = get_train_catalog(limit=limit, search=search)
    return TrainListResponse(total_trains=total, trains=train_list)


# 3. Train Itinerary & Route Stops
@app.get(
    "/trains/{train_number}",
    response_model=TrainDetailResponse,
    summary="Get Detailed Route Itinerary for a Specific Train",
    tags=["Trains"]
)
def get_train_detail(train_number: str) -> TrainDetailResponse:
    """Returns the complete timetable, stop sequence, arrival/departure schedule, and distances for a train."""
    train_data = get_train_by_number(train_number)
    if not train_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train number '{train_number}' not found in database."
        )
    return TrainDetailResponse(**train_data)


# 4. ML Delay Prediction Endpoint
@app.post(
    "/predict-delay",
    response_model=DelayPredictionResponse,
    summary="Predict Station Arrival Delay using Machine Learning",
    tags=["Delay Prediction"]
)
def predict_delay_endpoint(req: DelayPredictionRequest) -> DelayPredictionResponse:
    """Evaluates the trained PredictRail HistGradientBoostingRegressor model to predict delay in minutes."""
    try:
        res = service_predict_delay(
            train_number=req.train_number,
            station_code=req.station_code,
            current_delay_minutes=req.current_delay_minutes or 0.0,
            departure_hour=req.departure_hour
        )
        return DelayPredictionResponse(**res)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# 5. Dynamic ETA Endpoint
@app.post(
    "/eta",
    response_model=ETAResponse,
    summary="Calculate Dynamic ETA and Route Propagation",
    tags=["Dynamic ETA"]
)
def dynamic_eta_endpoint(req: ETARequest) -> ETAResponse:
    """Calculates Dynamic ETA with calendar accumulation, midnight rollover, and graph delay propagation."""
    res = service_get_eta(
        train_number=req.train_number,
        current_station=req.current_station,
        current_delay_minutes=req.current_delay_minutes
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("error", "Dynamic ETA calculation failed.")
        )
    return ETAResponse(
        train_number=res["train_number"],
        train_name=res["train_name"],
        current_station=res["current_station"],
        current_station_name=res["current_station_name"],
        current_delay_minutes=res["current_delay_minutes"],
        destination=res["destination_station"],
        destination_name=res["destination_name"],
        destination_scheduled_time=res["destination_scheduled_time"],
        destination_dynamic_eta=res["destination_dynamic_eta"],
        destination_predicted_delay_min=res["destination_predicted_delay_min"],
        destination_punctuality=res["destination_punctuality"],
        upcoming_stops_count=res["upcoming_stops_count"],
        upcoming_itinerary=res["upcoming_itinerary"]
    )


# 6. Weather & Meteorological Risk Endpoint
@app.get(
    "/weather/{station_code}",
    response_model=WeatherResponse,
    summary="Get Station Weather and Delay Risk Score",
    tags=["Weather"]
)
def weather_endpoint(station_code: str) -> WeatherResponse:
    """Fetches real-time / forecast weather for an Indian station via Open-Meteo and returns risk score."""
    stn = str(station_code).strip().upper()
    res = service_get_weather(stn)
    return WeatherResponse(**res)


# 7. Prototype Crowd Estimation Endpoint
@app.post(
    "/crowd",
    response_model=CrowdResponse,
    summary="Get Synthetic Prototype Crowd Density & Coach Occupancy",
    tags=["Crowd Advisory"]
)
def crowd_endpoint(req: CrowdRequest) -> CrowdResponse:
    """Returns synthetic prototype passenger counts and crowd level classifications for each coach."""
    res = service_get_crowd(train_number=req.train_number, station_code=req.station_code)
    return CrowdResponse(
        train_number=res["train_number"],
        station_code=res["station_code"],
        data_type=res.get("data_type", "SYNTHETIC_PROTOTYPE"),
        overall_occupancy_ratio=res["overall_occupancy_ratio"],
        overall_occupancy_percent=res["overall_occupancy_percent"],
        overall_crowd_level=res["overall_crowd_level"],
        total_estimated_passengers=res["total_estimated_passengers"],
        total_estimated_capacity=res["total_estimated_capacity"],
        class_breakdown=res["class_breakdown"],
        coach_details=res["coach_details"],
        disclaimer=res.get("disclaimer", "PROTOTYPE DATA")
    )


# 8. Smart Compartment Recommendation Endpoint
@app.post(
    "/recommend-compartment",
    response_model=CompartmentRecommendationResponse,
    summary="Recommend Least-Crowded Travel Class with Domain Justification",
    tags=["Crowd Advisory"]
)
def recommend_compartment_endpoint(req: CompartmentRecommendationRequest) -> CompartmentRecommendationResponse:
    """Evaluates available coach classes and recommends the option with the lowest crowd density."""
    res = service_recommend_compartment(
        train_number=req.train_number,
        station_code=req.station_code,
        budget_filter=req.budget_filter
    )
    if not res.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=res.get("error", "Failed to generate compartment recommendation.")
        )
    return CompartmentRecommendationResponse(**res)


# 9. Combined PredictRail Dashboard Endpoint
@app.post(
    "/predict",
    response_model=CombinedPredictionResponse,
    summary="Unified PredictRail Master Intelligence Endpoint",
    tags=["Unified Intelligence"]
)
def combined_predict_endpoint(req: CombinedPredictionRequest) -> CombinedPredictionResponse:
    """
    Blends ML delay prediction, NetworkX graph bottlenecks, Dynamic ETA,
    Weather risk layering, Prototype Crowd, and Smart Compartment recommendations
    into a single unified payload for the passenger dashboard.
    """
    try:
        combined = service_get_combined_prediction(
            train_number=req.train_number,
            current_station=req.current_station,
            current_delay_minutes=req.current_delay_minutes,
            budget_filter=req.budget_filter
        )
        return CombinedPredictionResponse(**combined)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# 10. Live Train Running Status (RailRadar Integration)
@app.get(
    "/trains/{train_number}/live",
    response_model=LiveTrainStatusResponse,
    summary="Get Real-Time Live Train Running Status from RailRadar",
    tags=["Live Telemetry"]
)
def live_train_status_endpoint(
    train_number: str,
    date: Optional[str] = Query(None, description="Journey start date in YYYY-MM-DD format (defaults to current run)"),
    authoritative: bool = Query(False, description="Whether to force upstream live telemetry refresh bypassing cache"),
    halts_only: bool = Query(False, description="Whether to include only halting stops in route")
) -> LiveTrainStatusResponse:
    """
    Fetches official real-time live train running status, GPS coordinates,
    current speed, delay in minutes, next halting station, and upcoming stops via RailRadar.
    """
    res = service_get_live_train_status(
        train_number=train_number,
        date=date,
        authoritative=authoritative,
        halts_only=halts_only
    )
    if not res.get("success") and res.get("status_code") in [401, 404, 429]:
        raise HTTPException(
            status_code=res.get("status_code", status.HTTP_502_BAD_GATEWAY),
            detail=res.get("error", "RailRadar API request failed.")
        )
    return LiveTrainStatusResponse(**res)


if __name__ == "__main__":
    import uvicorn
    print(f"Starting {settings.PROJECT_NAME} API on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

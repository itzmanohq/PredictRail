"""
PredictRail Backend Configuration & Environment Settings
"""
import os
from typing import List

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings:
    PROJECT_NAME: str = "PredictRail"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Intelligent Indian Railways Delay Prediction, Dynamic ETA, Network Congestion, Weather Risk, and Prototype Crowd Advisory API"
    ENVIRONMENT: str = os.getenv("PREDICTRAIL_ENV", "development")
    
    # RailRadar Live Train Telemetry API
    RAILRADAR_API_KEY: str = os.getenv("RAILRADAR_API_KEY", "")
    RAILRADAR_BASE_URL: str = os.getenv("RAILRADAR_BASE_URL", "https://api.railradar.in/v1")
    
    # CORS Origins for frontend development and production deployment
    _cors_env = os.getenv("CORS_ORIGINS", "")
    _custom_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] if _cors_env else []

    CORS_ORIGINS: List[str] = [
        "https://predict-rail.vercel.app",
        "https://predictrail-backend.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ] + _custom_origins
    
    # Server Defaults
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = ENVIRONMENT == "development"

settings = Settings()

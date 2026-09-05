import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Union, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "predictrail_delay_model.joblib")

_LOADED_MODEL = None

def get_model():
    """Lazy loader for the serialized PredictRail pipeline."""
    global _LOADED_MODEL
    if _LOADED_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model not found at {MODEL_PATH}. Please train the model first by running 'python ml/train.py'."
            )
        _LOADED_MODEL = joblib.load(MODEL_PATH)
    return _LOADED_MODEL

def predict_delay(input_data: Union[Dict[str, Any], List[Dict[str, Any]], pd.DataFrame]) -> Dict[str, Any]:
    """
    Predicts arrival delay in minutes for Indian Railways train-station stops.
    
    Expected Feature Keys:
      - train_type: 'Mail_Express', 'Superfast', or 'Premium_Superfast'
      - station_sequence: int (e.g. 1, 10, 48)
      - distance_km: float (cumulative distance in km)
      - total_route_distance_km: float (total corridor distance)
      - total_route_stops: int (total stops on route)
      - route_distance_progress: float (0.0 to 1.0)
      - route_stop_progress: float (0.0 to 1.0)
      - scheduled_halt_duration_min: float (dwell time in min)
      - departure_hour: int (0 to 23)
      - departure_minute: int (0 to 59)
      - time_of_day: 'Morning_Peak', 'Midday', 'Evening_Peak', 'Night'
      - station_network_density: int (total trains servicing station)
      - corridor_train_density: int (trains sharing this route)
    
    Returns:
      Dict with predicted_delay_min, delay_severity_category, on_time_probability_heuristic, etc.
    """
    model = get_model()
    
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        df = pd.DataFrame(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise ValueError("Input must be a dict, list of dicts, or pandas DataFrame.")
        
    # Required feature check & default imputation
    defaults = {
        'train_type': 'Mail_Express',
        'station_sequence': 1,
        'distance_km': 0.0,
        'total_route_distance_km': 1000.0,
        'total_route_stops': 30,
        'route_distance_progress': 0.1,
        'route_stop_progress': 0.1,
        'scheduled_halt_duration_min': 2.0,
        'departure_hour': 12,
        'departure_minute': 0,
        'time_of_day': 'Midday',
        'station_network_density': 10,
        'corridor_train_density': 5
    }
    
    for k, v in defaults.items():
        if k not in df.columns:
            df[k] = v
        else:
            df[k] = df[k].fillna(v)

    # Generate predictions via the serialized Pipeline
    raw_preds = model.predict(df)
    
    # Apply technical non-negative constraint
    clipped_preds = np.clip(raw_preds, a_min=0.0, a_max=None)
    
    results = []
    for p in clipped_preds:
        p_val = round(float(p), 1)
        if p_val <= 15.0:
            sev = "On-Time / Minor (<= 15 min)"
            sev_code = 0
        elif p_val <= 60.0:
            sev = "Moderate Delay (15 - 60 min)"
            sev_code = 1
        else:
            sev = "Severe Delay (> 60 min)"
            sev_code = 2
            
        results.append({
            "predicted_delay_min": p_val,
            "delay_severity_category": sev,
            "delay_severity_code": sev_code,
            "is_delayed": bool(p_val > 15.0),
            "punctuality_status": "Delayed" if p_val > 15.0 else "On-Time"
        })
        
    if isinstance(input_data, dict):
        return results[0]
    return {"predictions": results, "count": len(results)}

if __name__ == "__main__":
    print("Testing PredictRail Prediction Functionality...")
    sample_input = {
        "train_type": "Superfast",
        "station_sequence": 25,
        "distance_km": 750.0,
        "total_route_distance_km": 1500.0,
        "total_route_stops": 40,
        "route_distance_progress": 0.50,
        "route_stop_progress": 0.625,
        "scheduled_halt_duration_min": 5.0,
        "departure_hour": 18,
        "departure_minute": 30,
        "time_of_day": "Evening_Peak",
        "station_network_density": 45,
        "corridor_train_density": 12
    }
    try:
        res = predict_delay(sample_input)
        print("Sample Prediction Output:")
        print(res)
    except Exception as e:
        print(f"Prediction error (model may need training first): {e}")

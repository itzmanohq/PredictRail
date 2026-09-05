# PredictRail Weather Integration & Operational Risk Report

## 1. Executive Summary & Architecture Overview

The **PredictRail Weather Integration Module** (`weather/`) enriches Indian Railways delay predictions and dynamic ETA calculations with real-time meteorological observations. Severe weather conditions—including heavy monsoon downpours, thick northern fog (dense rime fog), tropical thunderstorms, and extreme gale winds—represent major sources of operational disruptions across Indian Railways' 68,000+ km network.

### Zero-Cost & Policy Adherence
- **Zero Paid APIs / Subscriptions:** Integrates exclusively with the **Open-Meteo Free Forecast API** (`https://api.open-meteo.com/v1/forecast`), which requires **no API key**, no credit card, and no authentication tokens.
- **Dedicated to Indian Railways:** Station geocoding is powered by `data/raw/stations.json` containing **8,990** Indian railway stations across all 18 railway zones.
- **Strict Anti-Leakage Guarantee:** Weather observations and forecasts are locked strictly to the train's scheduled observation timestamp. Future actual train delays and future unobserved weather data are never used as model inputs.
- **Non-Destructive Layering:** The weather risk model operates as an independent, transparent additive adjustment layer over the core ML prediction and NetworkX delay propagation models without mutating or corrupting the base model weights.

---

## 2. Station Geocoding Pipeline

Indian Railways stations are identified by alphanumeric station codes (e.g., `NDLS` for New Delhi, `HWH` for Howrah, `CNB` for Kanpur Central, `GHY` for Guwahati). 

### Geocoding Strategy
1. **Source:** `data/raw/stations.json` (DataMeet open-access Indian Railways GeoJSON).
2. **Parsing & Indexing:** `load_station_coordinates()` indexes 8,990 stations into an in-memory hash table mapping uppercase station codes to:
   - `latitude` (WGS-84 float)
   - `longitude` (WGS-84 float)
   - `station_name`
   - `state`
   - `zone` (e.g., NR, ER, WR, CR, NFR)
3. **Data Quality & Handling:**
   - **Missing/Null Coordinates:** Flagged with `success=False` and gracefully returns an `UNKNOWN` category rather than causing runtime crashes.
   - **Duplicate Station Names:** Resolved cleanly via unique station code keys (`code`).
   - **Invalid Codes:** Handled with a standard error response dictionary.

---

## 3. Open-Meteo Integration & Meteorological Variables

### API Request Specifications
- **Endpoint:** `https://api.open-meteo.com/v1/forecast`
- **Coordinate Precision:** 4 decimal places (~11 meters resolution).
- **Timezone:** `Asia/Kolkata` (IST, UTC+05:30).

### Meteorological Variables Collected
| Variable | Open-Meteo Parameter | Unit | Operational Significance in Indian Railways |
|---|---|---|---|
| **Temperature** | `temperature_2m` | °C | Track thermal expansion / rail fracture risk during peak summer/winter. |
| **Relative Humidity** | `relative_humidity_2m` | % | Moisture saturation and condensation monitoring. |
| **Precipitation** | `precipitation` | mm | Track flooding, waterlogging, and switch gear disruption. |
| **Rainfall** | `rain` | mm | Active rainfall intensity. |
| **Snowfall** | `snowfall` | cm | Track clearance issues in Northern/Himalayan rail corridors (e.g. Kashmir). |
| **Weather Code** | `weather_code` | WMO int | Standard WMO meteorological condition code (0–99). |
| **Wind Speed** | `wind_speed_10m` | km/h | Gale / cyclone speed restrictions over railway bridges (e.g. Pamban bridge). |
| **Visibility** | `visibility` | meters | Locomotive headlight visibility range and mandatory fog speed limits. |

---

## 4. WMO Weather Classification & Operational Categories

PredictRail maps international WMO weather codes into operational disruption categories tailored to Indian Railways operating procedures:

```
+---------------+------------------------+-------------------------------------------------------+
| Category      | WMO Codes / Triggers   | Indian Railways Operational Context                   |
+---------------+------------------------+-------------------------------------------------------+
| CLEAR         | 0, 1, 2, 3             | Normal track visibility and track speed               |
| LIGHT_RAIN    | 51-57, 61-63, 80       | Slight dampness; minor braking distance buffer        |
| HEAVY_RAIN    | 65-67, 81, 82          | Monsoon waterlogging risk; track speed caution order  |
| FOG           | 45, 48, or vis < 500m  | Mandatory fog speed restrictions (max 60-75 km/h)     |
| SNOW          | 71-77, 85, 86          | Track de-icing and snowplow operational delays        |
| THUNDERSTORM  | 95, 96, 99             | Overhead electrification (OHE) tripping & signal trips|
| STRONG_WIND   | wind_speed >= 45 km/h  | Coastal bridge restrictions and speed reductions      |
| UNKNOWN       | -1, unmapped, offline  | Default neutral baseline                              |
+---------------+------------------------+-------------------------------------------------------+
```

---

## 5. Weather Risk Scoring & Delay Buffer Calculation

### Rule-Based Heuristic Framework (0–100 Scale)
To ensure transparency and interpretability (and avoid unverified black-box predictions), the risk score uses domain-driven heuristics based on Indian Railways operating safety manuals:

1. **Base Risk Weight:**
   - `CLEAR`: 5.0
   - `LIGHT_RAIN`: 20.0
   - `STRONG_WIND`: 50.0
   - `HEAVY_RAIN`: 65.0
   - `SNOW`: 70.0
   - `FOG`: 80.0
   - `THUNDERSTORM`: 85.0
   - `UNKNOWN`: 10.0

2. **Continuous Variable Penalties:**
   - **Low Visibility Penalty:** If visibility $< 500$m, $+15.0$ risk penalty; if visibility $< 1000$m, $+8.0$ risk penalty.
   - **Precipitation Intensity Penalty:** $+1.2 \times \text{precipitation\_mm}$ (capped at $+15.0$).

3. **Total Risk Score Calculation:**
   $$\text{Total Risk Score} = \min\left(100.0, \, \max\left(0.0, \, \text{Base Risk} + \text{Vis Penalty} + \text{Precip Penalty}\right)\right)$$

4. **Estimated Weather Delay Buffer ($\Delta t_{\text{weather}}$):**
   $$\Delta t_{\text{weather}} = \begin{cases} 0.0 \text{ min}, & \text{if Category} = \text{CLEAR} \\ \text{Base Delay} + \max(0.0, \, (\text{Risk Score} - 20) \times 0.20), & \text{otherwise} \end{cases}$$

### Risk Level Tiers & UI Badging
- **0.0 – 15.0:** `Very Low (Optimal Rail Conditions)` (Green)
- **15.1 – 40.0:** `Low Risk (Minor Precipitation)` (Blue)
- **40.1 – 65.0:** `Moderate Risk (Caution Required)` (Orange)
- **65.1 – 100.0:** `High Risk (Severe Disruption Expected)` (Red)

> [!IMPORTANT]
> **Heuristic Disclaimer:** Weather risk scores and delay buffer adjustments are derived from railway operating safety guidelines and heuristic domain rules, NOT from machine learning coefficients. They are intentionally kept transparent and modular.

---

## 6. Integration with Dynamic ETA Engine

The weather module provides `apply_weather_adjustment_to_eta()`, which consumes the structured output of `eta.dynamic_eta.get_dynamic_eta()` and enriches each station stop in the itinerary.

### Separation of Concerns
The engine strictly preserves the visibility of all independent delay components:
1. **`base_predicted_delay_min`:** ML regression delay + NetworkX graph propagation delay.
2. **`weather_risk_score`:** Continuous meteorological risk metric (0–100).
3. **`weather_delay_adjustment_min`:** Non-linear weather buffer in minutes.
4. **`final_weather_adjusted_delay_min`:** $\text{Base Delay} + \Delta t_{\text{weather}}$.

```mermaid
graph LR
    A[Train Schedule Timetable] --> D[Dynamic ETA Engine]
    B[ML Delay Model (HistGBR)] --> D
    C[NetworkX Graph Propagation] --> D
    D --> E[Base Dynamic ETA]
    F[Open-Meteo Weather API] --> G[Weather Risk Scoring]
    E --> H[Weather-Adjusted Dynamic ETA]
    G --> H
    H --> I[Final Enriched Itinerary with Separate Components]
```

---

## 7. Caching & Fault Tolerance

### In-Memory Geocache & TTL Strategy
- **Coordinate Rounding:** API query coordinates are rounded to 2 decimal places ($\approx 1.1$ km), ensuring that stations in the same urban agglomeration (e.g. NDLS and NZM in Delhi, or HWH and SDAH in Kolkata) share weather cache entries.
- **Cache TTL:** $1,800$ seconds ($30$ minutes) TTL.
- **Rate Limit Protection:** Avoids flooding Open-Meteo's public servers during bulk itinerary lookups.

### Robust Error Handling
- **Timeouts & Connection Failures:** Caught gracefully using `requests.exceptions.Timeout` and `ConnectionError`, returning structured fallback responses (`category="UNKNOWN"`, `weather_delay_adjustment_min=0.0`).
- **HTTP 429 (Rate Limiting):** Handled with fallback warning without terminating the ETA pipeline.
- **Malformed JSON / Non-200 Status:** Logged and converted to neutral fallback.

---

## 8. Anti-Leakage Compliance

1. **Prediction Time Temporal Boundary:** The weather layer queries current conditions matching the observation time.
2. **No Future Actuals:** Future actual delay records from the test set are never provided to the weather module.
3. **Additive Separation:** Because the ML model was trained on pure operational features (departure delay, distance, dwell time, station degree), the weather layer does not distort existing model feature weights.

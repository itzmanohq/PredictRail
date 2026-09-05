# PredictRail 🚆 (Indian Railways Edition)
**AI-Powered Indian Railway Delay Forecasting, Network Congestion Modeling, and Dynamic ETA Platform**

---

## 📌 Project Overview

**PredictRail** is an intelligent decision-support system built specifically for the **Indian Railways** network. While traditional railway apps only display static timetables or past historical delay occurrences, PredictRail proactively forecasts downstream arrival delays, simulates network-wide delay propagation through busy railway junctions, calculates dynamic calendar-aware ETAs, integrates real-time meteorological risk factors, and provides prototype coach density advisories.

> [!IMPORTANT]
> **Research & Prototype Transparency Notice:**
> PredictRail is a research/prototype system and its delay predictions, weather adjustments, and crowd estimates are not guaranteed real-world operational values.

---

## 🌟 Key Features

1. **Indian Railway ML Delay Prediction:**
   - Evaluates trained histogram gradient boosting regressors (`HistGradientBoostingRegressor`) to forecast station arrival delays based on departure momentum, route distance, halt slack, and temporal patterns.
2. **Railway Network Graph & Bottleneck Detection:**
   - NetworkX topological graph modeling 8,151 stations and 28,194 track edges.
   - Computes static junction centrality and identifies 2,378 high-congestion railway bottlenecks across India.
3. **Dynamic Multi-Day ETA Engine:**
   - Station-by-station delay decay and accumulation calculation.
   - Handles multi-day calendar rollover (Day 1, Day 2, Day 3) across transcontinental Indian routes.
4. **Live Meteorological Risk Layering:**
   - Fetches live weather observations (temperature, precipitation, wind speed, track visibility) via the keyless **Open-Meteo API**.
   - Computes a 0–100 meteorological risk score and isolates weather buffers (+0m to +35m) without biasing baseline ML weights.
5. **Prototype Crowd Estimation & Smart Compartment Recommendation:**
   - Simulated coach-by-coach passenger density across Indian Railways travel classes (1A, 2A, 3A, 3E, SL, 2S, GEN).
   - Dynamic class recommendation engine with budget filtering (`ALL`, `AC`, `NON-AC / BUDGET`) and transparent domain justifications.
6. **FastAPI Backend Gateway:**
   - High-performance asynchronous REST API with Pydantic v2 schemas and isolated subsystem fault-tolerance.
7. **Modern React / Vite Dashboard:**
   - Responsive dark-mode interface with live train searching, instant filter reactivity, progression timelines, and zero UI placeholders.

---

## 🏗️ Architecture & Technology Stack

```
                                  +-----------------------------+
                                  |    React 18 + Vite UI       |
                                  | (Dashboard, Live Filters)   |
                                  +--------------+--------------+
                                                 | REST HTTP
                                                 v
                                  +-----------------------------+
                                  |     FastAPI Backend API     |
                                  | (Pydantic v2 Validation)    |
                                  +--------------+--------------+
                                                 |
         +--------------------+------------------+-------------------+--------------------+
         |                    |                                      |                    |
         v                    v                                      v                    v
+-----------------+  +-----------------+                    +-----------------+  +-----------------+
| ML Delay Engine |  | Railway Graph & |                    | Weather Risk    |  | Prototype Crowd |
| (HistGradBoost, |  | Delay Prop.     |                    | Layer (Open-    |  | & Smart Class   |
| Scikit-Learn)   |  | (NetworkX)      |                    | Meteo API)      |  | Advisory Engine |
+-----------------+  +-----------------+                    +-----------------+  +-----------------+
```

### Core Technologies:
- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic v2, HTTPX, Joblib.
- **Machine Learning & Graph:** Scikit-Learn, NumPy, Pandas, NetworkX.
- **Weather Provider:** Open-Meteo API (100% Free, Keyless).
- **Frontend:** React 18, Vite 5, Vanilla CSS Design System with CSS Variables.
- **Testing:** Pytest, FastAPI TestClient (47/47 passing tests).

---

## 📊 Dataset Information

PredictRail is trained and calibrated exclusively on genuine **Indian Railways** datasets sourced from open-access railway archives and DataMeet:
- **`indian_railway_schedules.csv`**: Complete schedule timetables for **11,113 trains**, 8,151 stations, and 186,000+ stop entries.
- **`stations.json`**: Official geographic coordinates, station codes, zones, and division boundaries.
- **`predictrail_training_data.csv`**: 59,201 preprocessed operational delay records with chronological train/val/test partitions (70% / 15% / 15%).

---

## 🤖 ML Model Evaluation

- **Model Type:** `HistGradientBoostingRegressor` with `StandardScaler` and `OneHotEncoder` preprocessing.
- **Evaluation on Unseen Indian Railways Holdout Data:**
  - **Validation MAE:** 39.72 min (vs. 49.75 min baseline — **20.2% improvement**).
  - **Test MAE:** 39.90 min.
  - **Within $\pm 10$ Minutes:** **30.43%** accuracy.
  - **Within $\pm 30$ Minutes:** **65.06%** accuracy.
- **Inference Speed:** Sub-50ms inference time with zero runtime retraining.

---

## ⚠️ Prototype Data & External Service Disclaimers

1. **Synthetic Crowd Disclaimer:**
   - Coach passenger counts, seat occupancy percentages, and crowd level classifications are **SYNTHETIC PROTOTYPE DATA**.
   - PredictRail does not claim access to live IRCTC PNR ticket reservations, CCTV cameras, or hardware coach sensors.
2. **Weather Attribution:**
   - Weather observations and forecasts are powered by the **Open-Meteo API**.
   - Subsystem isolation ensures that if Open-Meteo is offline, the system safely falls back without interrupting predictions.

---

## 🚀 Quickstart & Startup Guide

### 1. Environment Setup
```bash
# Clone and navigate to project root
cd PredictRail

# Activate Python virtual environment (Windows)
.\.venv\Scripts\activate

# Install dependencies if needed
pip install -r requirements.txt
```

### 2. Start FastAPI Backend Server
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 3. Start React Frontend Dashboard
```bash
# In a new terminal
cd frontend
npm run dev
```
- Access Dashboard: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Running Automated Tests

Run the complete 47-test automated verification suite:
```bash
pytest -q
```
Expected output:
```
47 passed in ~48s
```

---

## 🎬 Recommended Jury Demo Scenario

1. Open the dashboard at `http://localhost:5173`.
2. Select **Train 12423** (Dibrugarh Rajdhani Express).
3. Select observation station **Guwahati (GHY)**.
4. Enter current observed delay: **30 minutes**.
5. Click **ANALYZE TRAIN**.
6. Review the resulting **ML Delay Forecast**, **Dynamic Multi-Day ETA** (reaching New Delhi on Day 3), **Open-Meteo Weather Risk**, **Synthetic Prototype Crowd Breakdown**, and **Smart Class Recommendation** (toggle between `ALL`, `AC`, and `NON-AC / BUDGET`).

---

## 📋 Documentation Directory
- `docs/demo_script.md`: 3–5 minute hackathon jury presentation script.
- `docs/jury_faq.md`: 21 technical jury questions with comprehensive, honest answers.
- `docs/model_evaluation.md`: Detailed ML training metrics and feature importance.
- `docs/dataset_report.md`: Exploratory data analysis and feature engineering summary.

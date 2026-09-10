# PredictRail V1 — ML Architecture Quick Reference

**System:** PredictRail V1 (AI-Powered Indian Railways Delay Engine)  
**Primary Model:** `sklearn.ensemble.HistGradientBoostingRegressor`  
**Dataset:** 59,201 Matched Indian Railways Station Stops (2,733 Trains, 2,972 Stations)  
**Target:** `arrival_delay_min` (Continuous Non-Negative Minutes, $\ge 0.0m$)  

---

## 1. Quick Technical Specifications

| Parameter | Value / Ground-Truth Detail |
| :--- | :--- |
| **Model Class** | `sklearn.ensemble.HistGradientBoostingRegressor` |
| **Hyperparameters** | `max_iter=200`, `learning_rate=0.08`, `max_leaf_nodes=31`, `min_samples_leaf=20`, `random_state=42` |
| **Benchmark Model** | `sklearn.ensemble.RandomForestRegressor` (`n_estimators=100`, `max_depth=16`, `random_state=42`) |
| **Baseline Model** | Naive Train Mean Delay Predictor ($\bar{y}_{\text{train}} = 48.24\text{ min}$) |
| **Training Dataset** | `data/processed/predictrail_training_data.csv` (59,201 records, 0 nulls) |
| **Data Partitioning** | **Grouped Split by Train Number:** 70% Train (41,435), 15% Val (8,642), 15% Test (9,124) |
| **Preprocessing** | `OneHotEncoder(handle_unknown='ignore')` + `StandardScaler()` in `ColumnTransformer` |
| **Training Speed** | **0.75 seconds** on 41,435 records |
| **Inference Speed** | **< 1.0 millisecond** per station query |

---

## 2. The 13 Verified Production ML Features

```
1.  train_type                  (Categorical: Premium_Superfast / Superfast / Mail_Express)
2.  station_sequence            (Numeric: Monotonically increasing halt index 1, 2, 3...)
3.  distance_km                 (Numeric: Track distance from origin in kilometers)
4.  total_route_distance_km     (Numeric: Total route corridor span in kilometers)
5.  total_route_stops           (Numeric: Total scheduled halts along the full journey)
6.  route_distance_progress     (Numeric: distance_km / total_route_distance_km, 0.0 to 1.0)
7.  route_stop_progress         (Numeric: station_sequence / total_route_stops, 0.0 to 1.0)
8.  scheduled_halt_duration_min (Numeric: Scheduled platform dwell buffer in minutes)
9.  departure_hour              (Numeric: Departure hour from station, 0 to 23)
10. departure_minute            (Numeric: Departure minute within the hour, 0 to 59)
11. time_of_day                 (Categorical: Morning_Peak / Midday / Evening_Peak / Night)
12. station_network_density     (Numeric: Total trains calling at station across national timetable)
13. corridor_train_density      (Numeric: Total train services sharing origin-destination corridor)
```

---

## 3. Verified Evaluation Metrics

| Metric | Naive Baseline | RandomForest Benchmark | HistGradientBoosting (Production) |
| :--- | :---: | :---: | :---: |
| **Validation MAE** | 49.75 min | 39.96 min | **39.72 min** (Best) |
| **Validation RMSE** | 86.14 min | 70.09 min | **69.77 min** (Best) |
| **Validation $R^2$** | -0.0002 | 0.3378 | **0.3439** (Best) |
| **Validation MedAE** | 36.00 min | 20.62 min | **19.88 min** (Best) |
| **Test MAE** | 46.87 min | **38.63 min** | **39.90 min** |
| **Test RMSE** | 78.31 min | **72.67 min** | **74.77 min** |
| **Test $R^2$** | -0.0010 | **0.1381** | **0.0874** |
| **Test MedAE** | 36.00 min | **18.96 min** | **19.06 min** |
| **Test Within $\pm 10$ Min** | 10.58% | **31.42%** | **30.43%** |
| **Test Within $\pm 30$ Min** | 39.38% | **65.38%** | **65.06%** |

---

## 4. Ranked Permutation Feature Importance

| Rank | Feature Name | Importance Score | Operational Significance |
| :---: | :--- | :---: | :--- |
| **1** | `corridor_train_density` | **0.4247** | Primary driver: Line-haul trunk corridor traffic saturation. |
| **2** | `total_route_distance_km` | **0.2647** | Intercity corridor span and multi-zonal boundary crossings. |
| **3** | `distance_km` | **0.2430** | Physical cumulative distance traversed from trip origin. |
| **4** | `total_route_stops` | **0.1439** | Number of intermediate station halts and platform events. |
| **5** | `train_type` | **0.0799** | Track priority hierarchy (Superfast vs. Mail/Express). |
| **6** | `route_stop_progress` | **0.0269** | Fraction of scheduled halts completed. |
| **7** | `station_network_density` | **0.0258** | Station junction crossing load and platform congestion. |
| **8** | `scheduled_halt_duration_min` | **0.0112** | Dwell recovery slack buffer at platform. |
| **9** | `station_sequence` | **0.0076** | Stop position index along the route. |
| **10** | `departure_hour` | **0.0058** | Diurnal peak suburban commuter congestion window. |
| **11** | `time_of_day` | **0.0025** | Peak vs. off-peak traffic category. |
| **12** | `route_distance_progress` | **0.0000** | Collinear with absolute distance. |
| **13** | `departure_minute` | **0.0000** | Fine-grained minute offset. |

---

## 5. Serialized Model Artifacts

| Artifact Path | Size | Description |
| :--- | :---: | :--- |
| `models/predictrail_delay_model.joblib` | 747 KB | Production Scikit-Learn `Pipeline` (Preprocessor + Regressor). |
| `models/predictrail_preprocessor.joblib` | 3.6 KB | Fitted standalone `ColumnTransformer` (OHE + Scaler). |
| `models/metrics.json` | 2.4 KB | Full machine-readable evaluation metrics payload. |
| `models/feature_importance.json` | 423 B | Ranked permutation feature importance dictionary. |

---

## 6. What Is Implemented vs. What Is Planned

### Verified in Current Implementation (V1)
- 13 verified timetable, spatial, and topological density features.
- `HistGradientBoostingRegressor` with non-negative clipping ($\ge 0.0m$).
- Live telemetry ingestion from RailRadar with 35s polling and dynamic re-inference.
- Destination arrived state handling (`Status: ARRIVED`, `Arrival: 0 min`).
- Heuristic weather risk layering from Open-Meteo API.
- NetworkX 2,972-node railway graph bottleneck analysis.

### Planned for Future Releases (V2 Roadmap)
- Ingesting continuous time-series historical telemetry inside the ML feature matrix.
- Spatio-temporal multi-station historical weather alignment.
- Locomotive telematics and maintenance history features.
- Real-time PRS passenger crowd feeds.
- Freight vs. passenger track conflict prediction.
- End-to-end Spatio-Temporal Graph Neural Network (GNN).

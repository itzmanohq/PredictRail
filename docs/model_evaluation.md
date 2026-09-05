# PredictRail Indian Railways Model Training & Evaluation Report

**Document Version:** 1.0.0  
**Project:** PredictRail (Indian Railways AI Delay Engine)  
**Trained Model Artifact:** [models/predictrail_delay_model.joblib](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/models/predictrail_delay_model.joblib)  
**Metrics JSON:** [models/metrics.json](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/models/metrics.json)  
**Feature Importance JSON:** [models/feature_importance.json](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/models/feature_importance.json)  

---

## 1. Dataset & Scope

- **Dataset:** [data/processed/predictrail_training_data.csv](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/data/processed/predictrail_training_data.csv)
- **Geographic Domain:** Indian Railways Nationwide Network
- **Total Operational Records:** **59,201 station stops**
- **Unique Indian Trains:** 2,733 trains
- **Unique Indian Stations:** 2,972 stations

---

## 2. Partition Sizes (Grouped by Indian Train Number)

To ensure the model is evaluated on its ability to generalize to unseen train services without route-memorization leakage, a grouped split by Train Number was utilized:

| Partition | Share | Unique Trains | Operational Stops | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Training Set** | 70.0% | 1,913 trains | **41,435 records** | Used strictly for model fitting & weight optimization. |
| **Validation Set** | 14.6% | 410 trains | **8,642 records** | Used for hyperparameter tuning & candidate model selection. |
| **Holdout Test Set** | 15.4% | 410 trains | **9,124 records** | Completely unseen test evaluation partition. |

---

## 3. Features & Target Variable

### Safe Input Features (13 Features):
- **Categorical (2):** `train_type` (*Mail_Express, Superfast, Premium_Superfast*), `time_of_day` (*Morning_Peak, Midday, Evening_Peak, Night*)
- **Continuous / Numerical (11):** `station_sequence`, `distance_km`, `total_route_distance_km`, `total_route_stops`, `route_distance_progress`, `route_stop_progress`, `scheduled_halt_duration_min`, `departure_hour`, `departure_minute`, `station_network_density`, `corridor_train_density`

### Target Variable:
- **`arrival_delay_min`:** Non-negative continuous delay in minutes at the station stop.

---

## 4. Benchmark Performance & Model Comparison

All metrics were computed strictly from local execution:

| Model / Baseline | Val MAE (min) | Val RMSE (min) | Val $R^2$ | Test MAE (min) | Test RMSE (min) | Test $R^2$ | Within $\pm 10$m (%) | Within $\pm 30$m (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Naive Baseline (Train Mean: 48.24m)** | 49.75 | 86.14 | -0.0002 | 46.87 | 78.31 | -0.0010 | 10.58% | 39.38% |
| **RandomForestRegressor (100 Trees)** | 39.96 | 70.09 | 0.3378 | **38.63** | **72.67** | **0.1381** | 31.42% | **65.38%** |
| **HistGradientBoostingRegressor (Selected)** | **39.72** | **69.77** | **0.3439** | 39.90 | 74.77 | 0.0874 | 30.43% | 65.06% |

### Key Observations:
- **Significant Error Reduction:** Both machine learning models outperform the naive baseline, reducing validation MAE from **49.75 minutes down to 39.72 minutes** ($\sim 20.2\%$ error reduction).
- **Practical Accuracy:** Over **65.0% of test predictions** fall within $\pm 30$ minutes of actual arrival on unseen Indian railway routes.
- **Fast Execution:** `HistGradientBoostingRegressor` trains in under 1 second on 41,435 records and evaluates in milliseconds.

---

## 5. Feature Importance Analysis (Permutation Importance)

Permutation importance evaluated on the validation partition identified the primary physical and topological drivers of train delays across the Indian Railways network:

```
Rank  Feature                       Importance Score  Impact
-----------------------------------------------------------------------------------------
1.    corridor_train_density        0.4247            Corridor traffic congestion & train frequency
2.    total_route_distance_km       0.2647            Overall journey corridor length
3.    distance_km                   0.2430            Cumulative distance covered so far
4.    total_route_stops             0.1439            Number of intermediate junction stops
5.    train_type                    0.0799            Train priority (Superfast vs Mail/Express)
6.    route_stop_progress           0.0269            Fraction of stops completed
7.    station_network_density       0.0258            Junction hub complexity & track crossing load
8.    scheduled_halt_duration_min   0.0112            Scheduled dwell buffer
9.    departure_hour                0.0058            Departure hour diurnal cycle
10.   station_sequence              0.0076            Stop index along the route
11.   time_of_day                   0.0025            Peak vs Off-peak operational window
```

---

## 6. Sample Test Predictions (Unseen Trains)

```
Train    Train Name           Station  Seq  Actual Delay   Predicted Delay  Abs Error
-----------------------------------------------------------------------------------------
13010    DOON EXPRESS         ACND     30   212.0m         67.7m            144.3m
13307    GANGASUTLEJ          ACND     31   69.0m          49.7m            19.3m
13023    HOWRAH GAYA          AHA      21   23.0m          28.4m            5.4m
13120    DLI SDAH EXP         AHA      51   80.0m          173.1m           93.1m
13134    BSB SDAH EXP         AHA      44   6.0m           27.7m            21.7m
13423    BGP-AII WKLY         AHA      3    51.0m          17.9m            33.1m
```

---

## 7. Model Ownership & Authenticity Statement

> [!IMPORTANT]
> **PredictRail Model Ownership:**  
> - PredictRail does **NOT** claim to have invented the underlying Gradient Boosting or Random Forest mathematical algorithms.  
> - PredictRail **DOES** own the custom-trained prediction model: fitted locally on 41,435 Indian Railways operational records with project-specific feature engineering (`corridor_train_density`, `route_distance_progress`, `station_network_density`).  
> - No third-party pre-trained railway weights or hosted LLM prediction APIs were used.

---

## 8. Limitations

1. **Extreme Outliers:** Long-distance Indian trains occasionally suffer extreme delays ($>4$ hours) due to localized signal failures or fog; tree-based regressors conservatively predict closer to the route median.
2. **Weather Integration (Upcoming):** Weather inputs (Open-Meteo) will further enhance delay forecasting in subsequent stages.

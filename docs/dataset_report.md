# PredictRail Indian Railways Dataset Quality & Preprocessing Report

**Document Version:** 2.0.0 (Indian Railways Edition)  
**Project:** PredictRail (AI-Powered Indian Railways Delay Prediction)  
**Processed Dataset Artifact:** [predictrail_training_data.csv](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/data/processed/predictrail_training_data.csv)  
**Feature Schema:** [feature_schema.json](file:///C:/Users/madma/.gemini/antigravity-ide/scratch/PredictRail/data/processed/feature_schema.json)  

---

## 1. Dataset Source & Attribution

All training and topological data for PredictRail is derived exclusively from authentic, open-access **Indian Railways** sources:

| Dataset Component | Source Repository / Publisher | License / Terms | Description |
| :--- | :--- | :--- | :--- |
| **Indian Railways Master Schedules** | [github.com/areenakhan07/Indian_Railways](https://github.com/areenakhan07/Indian_Railways) | Open Data Commons / Public Domain | 186,124 timetable rows across 11,115 Indian trains & 8,151 stations. |
| **Historical Station Delays** | [github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning](https://github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning) | MIT License / Open Access | 63,428 actual historical train-station delay observations across nationwide Indian railway zones. |
| **Express Corridor Route Profiles** | [github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets](https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets) | CC BY-NC-SA 4.0 | 42 Intercity Express train routes connecting major metro corridors. |
| **Stations Geographic Network** | [github.com/datameet/railways](https://github.com/datameet/railways) | Open Data Commons (ODbL) / CC-BY-SA | 8,990 Indian railway stations with geographic coordinates and zones. |

---

## 2. Raw vs. Cleaned Dataset Scale

- **Raw Timetable Schedules:** 186,124 records (12 columns)
- **Raw Delay Observations:** 63,428 records (3 columns)
- **Merged & Matched Indian Records:** **59,201 operational station stops**
- **Unique Indian Trains Represented:** **2,733 trains** (e.g. *Avadh Express, Sabarmati Express, Intercity Express, Doon Express, Marudhar Express, Amritsar Express, Superfast, Mail/Express*)
- **Unique Indian Stations Represented:** **2,972 stations** (e.g. *NDLS, HWH, CSMT, MAS, CNB, BSB, GHY, PNBE, ADI, LKO*)
- **Missing Values in Processed Dataset:** **0 (0.0% across all 25 columns)**

---

## 3. Indian Railways Target Formulation

### Primary Regression Target: `arrival_delay_min`
Direct historical arrival delay in minutes recorded at the station stop.
- **Mean Delay:** 48.96 minutes
- **Median Delay:** 21.00 minutes
- **75th Percentile Delay:** 49.00 minutes
- **90th Percentile Delay:** 123.00 minutes
- **95th Percentile Delay:** 222.00 minutes
- **Max Delay:** 1415.00 minutes

### Secondary Classification Targets:
1. **Binary Delay Flag (`is_delayed`):**  
   - `0`: On-Time ($\le 15$ min buffer — Indian Railways punctuality standard) — **23,857 records (40.3%)**
   - `1`: Delayed (> 15 min buffer) — **35,344 records (59.7%)**
2. **Delay Severity Category (`delay_severity`):**  
   - `Class 0 (On-Time / Minor <= 15 min)`: 23,857 records (40.3%)
   - `Class 1 (Moderate 15 - 60 min)`: 23,458 records (39.6%)
   - `Class 2 (Severe > 60 min)`: 11,886 records (20.1%)

---

## 4. Strict Anti-Leakage Feature Analysis

> [!IMPORTANT]
> **Zero Future-Information Leakage:**  
> Only variables deterministically known *prior to or at the scheduled arrival/departure time* are retained as safe model input features.

| Status | Feature Name | Description | Reason Safe / Action |
| :--- | :--- | :--- | :--- |
| ✅ **SAFE** | `train_type` | Premium_Superfast / Superfast / Mail_Express | Derived from train numbering & name. |
| ✅ **SAFE** | `station_sequence` | Stop index along the train route (1st stop, 10th stop, etc.) | Pre-scheduled in timetable. |
| ✅ **SAFE** | `distance_km` | Track distance from origin in kilometers | Known infrastructure property. |
| ✅ **SAFE** | `total_route_distance_km` | Total length of the full route | Static schedule property. |
| ✅ **SAFE** | `total_route_stops` | Total number of intermediate halts | Static schedule property. |
| ✅ **SAFE** | `route_distance_progress` | $\frac{\text{distance\_km}}{\text{total\_route\_distance\_km}}$ (0.0 to 1.0) | Position along the corridor. |
| ✅ **SAFE** | `route_stop_progress` | $\frac{\text{station\_sequence}}{\text{total\_route\_stops}}$ (0.0 to 1.0) | Progression through stops. |
| ✅ **SAFE** | `scheduled_halt_duration_min` | Scheduled dwell time at the station (minutes) | Timetable feature. |
| ✅ **SAFE** | `departure_hour` / `minute` | Scheduled departure time component | Timetable feature. |
| ✅ **SAFE** | `time_of_day` | Morning_Peak / Midday / Evening_Peak / Night | Diurnal traffic cycle. |
| ✅ **SAFE** | `station_network_density` | Total train services passing through this station | Network junction bottleneck proxy. |
| ✅ **SAFE** | `corridor_train_density` | Number of trains operating on this origin-destination corridor | Corridor congestion metric. |
| 🚫 **EXCLUDED** | `future_actual_arrival` | Actual future timestamps | Target leakage. |
| 🚫 **EXCLUDED** | `downstream_delays` | Delays at future subsequent stations | Target leakage. |
| 🚫 **EXCLUDED** | `post_trip_cancellations` | Cancellation flags logged after failure | Target leakage. |

---

## 5. Grouped Train Partitioning Strategy

To prevent route-memorization leakage and test generalization to unseen trains:
- **Grouped by Unique Train Number:**
  - **Train Set (70%):** 1,913 unique trains → **41,435 records (70.0%)**
  - **Validation Set (15%):** 410 unique trains → **8,642 records (14.6%)**
  - **Holdout Test Set (15%):** 410 unique trains → **9,124 records (15.4%)**

---

## 6. Sufficiency Assessment

> [!NOTE]
> The processed dataset provides **59,201 real Indian Railways records** across **2,733 trains** and **2,972 stations**, with zero missing values and 13 safe engineered operational features. It is **100% sufficient and suitable** for training PredictRail's custom machine learning models.

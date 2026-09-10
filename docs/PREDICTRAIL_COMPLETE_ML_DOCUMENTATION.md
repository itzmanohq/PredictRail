# PredictRail V1 — Complete Machine Learning Model, Dataset, Features, Training Pipeline and Prediction System Documentation

**Project Title:** PredictRail (AI-Powered Indian Railways Delay Prediction & Operational Master Intelligence)  
**System Version:** PredictRail V1 (Indian Railways Production Architecture)  
**Release Date / Document Timestamp:** September 2026  
**Repository:** [itzmanohq/PredictRail](https://github.com/itzmanohq/PredictRail)  
**Target Audience:** Project Engineers, Data Scientists, Academic Mentors, Hackathon Jurors, Viva Reviewers  
**Document Classification:** Ground-Truth Technical Architecture Specification  

---

> [!IMPORTANT]
> **Ground-Truth Integrity Guarantee:**  
> This document details the **actual, executable, and verified implementation** of PredictRail V1. Every metric, dataset scale, algorithm hyperparameter, feature formula, and architectural interaction documented herein is directly extracted and validated from the active codebase and saved model artifacts.  
> - Features and modules operating in production are labeled **`CURRENTLY IMPLEMENTED & VERIFIED`**.  
> - Heuristic or post-inference auxiliary layers are labeled **`EXISTS IN PROJECT BUT NOT USED AS A TRAINING FEATURE`**.  
> - Theoretical enhancements and upcoming additions are explicitly labeled **`PLANNED / NOT CURRENTLY IMPLEMENTED`**.

---

# Table of Contents
1. [Part 1 — Executive Summary](#part-1--executive-summary)
2. [Part 2 — Machine Learning Model Details](#part-2--machine-learning-model-details)
3. [Part 3 — Scikit-Learn Ecosystem & Architecture](#part-3--scikit-learn-ecosystem--architecture)
4. [Part 4 — Dataset Architecture & Physical Scale](#part-4--dataset-architecture--physical-scale)
5. [Part 5 — Data Sources & Open-Source Attribution](#part-5--data-sources--open-source-attribution)
6. [Part 6 — Complete Data Schema (Training Pipeline)](#part-6--complete-data-schema-training-pipeline)
7. [Part 7 — Target Variable Formulation & Mathematical Mechanics](#part-7--target-variable-formulation--mathematical-mechanics)
8. [Part 8 — The 13 Production ML Features (In-Depth Analysis)](#part-8--the-13-production-ml-features-in-depth-analysis)
9. [Part 9 — Feature Engineering & Transformation Pipeline](#part-9--feature-engineering--transformation-pipeline)
10. [Part 10 — Data Preprocessing & Serialization](#part-10--data-preprocessing--serialization)
11. [Part 11 — Data Leakage Prevention Architecture](#part-11--data-leakage-prevention-architecture)
12. [Part 12 — Grouped Train / Validation / Test Partitioning Strategy](#part-12--grouped-train--validation--test-partitioning-strategy)
13. [Part 13 — Model Training Workflow & Hyperparameters](#part-13--model-training-workflow--hyperparameters)
14. [Part 14 — Candidate Model Comparison & Benchmark Analysis](#part-14--candidate-model-comparison--benchmark-analysis)
15. [Part 15 — Model Performance Metrics & Interpretation](#part-15--model-performance-metrics--interpretation)
16. [Part 16 — Naive Baseline Model Evaluation](#part-16--naive-baseline-model-evaluation)
17. [Part 17 — Feature Importance (Permutation Analysis)](#part-17--feature-importance-permutation-analysis)
18. [Part 18 — Serialized Model Artifacts & File Registry](#part-18--serialized-model-artifacts--file-registry)
19. [Part 19 — Real-Time Inference Pipeline](#part-19--real-time-inference-pipeline)
20. [Part 20 — Model Output Schema & Severity Classification](#part-20--model-output-schema--severity-classification)
21. [Part 21 — Real-Time Telemetry Integration (RailRadar)](#part-21--real-time-telemetry-integration-railradar)
22. [Part 22 — Architectural Gap: Current Model vs. Planned Richer Model](#part-22--architectural-gap-current-model-vs-planned-richer-model)
23. [Part 23 — Locomotive Telemetry & Engineering Features](#part-23--locomotive-telemetry--engineering-features)
24. [Part 24 — Meteorological Risk & Future Multi-Station Weather Modeling](#part-24--meteorological-risk--future-multi-station-weather-modeling)
25. [Part 25 — Dynamic Reaction to Sudden Live Operational Changes](#part-25--dynamic-reaction-to-sudden-live-operational-changes)
26. [Part 26 — Terminus & Destination Arrival Logic](#part-26--terminus--destination-arrival-logic)
27. [Part 27 — Search Workflow & Active Corridor Bounds](#part-27--search-workflow--active-corridor-bounds)
28. [Part 28 — Network Congestion & Topological Density Features](#part-28--network-congestion--topological-density-features)
29. [Part 29 — Mixed Freight and Passenger Interaction Dynamics](#part-29--mixed-freight-and-passenger-interaction-dynamics)
30. [Part 30 — Predictive Train Conflict Modeling](#part-30--predictive-train-conflict-modeling)
31. [Part 31 — Network Delay Propagation Engine](#part-31--network-delay-propagation-engine)
32. [Part 32 — Graph AI & Graph Neural Networks (GNN) vs. Tabular ML](#part-32--graph-ai--graph-neural-networks-gnn-vs-tabular-ml)
33. [Part 33 — Dynamic ETA Engine & Time Accumulation Mathematics](#part-33--dynamic-eta-engine--time-accumulation-mathematics)
34. [Part 34 — Prototype Crowd Density & Compartment Recommendation](#part-34--prototype-crowd-density--compartment-recommendation)
35. [Part 35 — Honest Model Limitations & Vulnerabilities](#part-35--honest-model-limitations--vulnerabilities)
36. [Part 36 — Why HistGradientBoostingRegressor is Scientifically Valid](#part-36--why-histgradientboostingregressor-is-scientifically-valid)
37. [Part 37 — Why Generative AI is Inappropriate for Numerical Delay Estimation](#part-37--why-generative-ai-is-inappropriate-for-numerical-delay-estimation)
38. [Part 38 — PredictRail ML Evolution Roadmap](#part-38--predictrail-ml-evolution-roadmap)
39. [Part 39 — Recommended Future Enterprise Dataset Specification](#part-39--recommended-future-enterprise-dataset-specification)
40. [Part 40 — Training Data vs. Live Inference Data Compatibility Matrix](#part-40--training-data-vs-live-inference-data-compatibility-matrix)
41. [Part 41 — Data Freshness, Caching & Stale Telemetry Handling](#part-41--data-freshness-caching--stale-telemetry-handling)
42. [Part 42 — Model Robustness, Edge Cases & Fault Tolerance](#part-42--model-robustness-edge-cases--fault-tolerance)
43. [Part 43 — Security, Data Privacy & API Protection](#part-43--security-data-privacy--api-protection)
44. [Part 44 — Full End-to-End Technical System Architecture](#part-44--full-end-to-end-technical-system-architecture)
45. [Part 45 — File-by-File Repository Mapping](#part-45--file-by-file-repository-mapping)
46. [Part 46 — Beginner & Viva-Style Conceptual Explanations](#part-46--beginner--viva-style-conceptual-explanations)
47. [Part 47 — Hackathon Jury & Technical Reviewer Q&A (35 Questions)](#part-47--hackathon-jury--technical-reviewer-qa-35-questions)
48. [Part 48 — Comprehensive Technical Glossary](#part-48--comprehensive-technical-glossary)
49. [Part 49 — Final Current-State Component Summary](#part-49--final-current-state-component-summary)
50. [Part 50 — Final Truth Check: Verified Facts vs. Planned Roadmap](#part-50--final-truth-check-verified-facts-vs-planned-roadmap)

---

# Part 1 — Executive Summary

### What PredictRail Is
**PredictRail** is an intelligent, multi-layered railway delay prediction, dynamic ETA calculation, and passenger advisory system built specifically for the **Indian Railways (IR)** network. It replaces static timetable guesswork with machine learning inference, topological graph analysis, real-time live telemetry ingestion, meteorological risk assessment, and coach occupancy guidance.

### What Problem It Solves
Indian Railways operates one of the world's most complex and heavily loaded railway networks, moving over 23 million passengers and 3 million tonnes of freight daily across 68,000+ route kilometers. Trains frequently suffer cascade delays caused by network congestion, single-track bottlenecks, junction crossing conflicts, weather disruptions, and locomotive constraints. Official legacy systems (e.g. NTES) merely show *where the train was last reported*; they do **not** predict how downstream network congestion and corridor characteristics will alter the train's future arrival delay. PredictRail provides passengers and operators with actionable, ahead-of-time delay forecasts.

### Why Railway Delay Prediction Is Difficult
1. **Network Interdependency:** Trains share track segments, platforms, and junctions. A delay in one express train cascades to subsequent express and local trains.
2. **Asymmetric Cumulative Delays:** Delays compound non-linearly over long journey corridors (e.g., 2,500+ km routes such as Dibrugarh to New Delhi).
3. **Multi-Scale Factors:** Delays stem from timetable structure, train priority hierarchies, diurnal traffic peaks, track topology, weather, and real-time dispatching.
4. **Data Disparity:** Historical telemetry is sparse, requiring strict anti-leakage feature engineering to prevent artificial over-optimism during training.

### What the ML Model Predicts
The primary machine learning model predicts the **Continuous Arrival Delay in Minutes (`arrival_delay_min`)** expected when a specific train reaches a specific destination/intermediate station stop along its route.

### Target Type & Problem Formulation
- **ML Formulation:** Supervised Tabular Continuous Regression.
- **Algorithm:** Histogram-Based Gradient Boosted Decision Trees (`HistGradientBoostingRegressor`).
- **Input Feature Vector:** 13 engineered features capturing train class, spatial distance, route progress, scheduled dwell, departure diurnal time, station junction density, and corridor traffic.

### How Prediction Flows: High-Level Pipeline
```
┌────────────────────────────────────────────────────────┐
│  Indian Railways Timetables & Historical Delay Logs    │
│  (186k Schedule Rows + 63k Historical Delay Records)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Data Cleaning, Key Normalization & Merging            │
│  (59,201 Matched Operational Records, 0 Nulls)         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Feature Engineering (13 Safe Non-Leaking Features)    │
│  & Train-Level Grouped Split (70% / 15% / 15%)         │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Preprocessing Pipeline (OneHotEncoder + StandardScaler)│
│  Serialized to models/predictrail_preprocessor.joblib  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  HistGradientBoostingRegressor Model Training          │
│  Evaluated on 9,124 Unseen Test Records (MAE: 39.90m)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Real-Time Inference Engine (ml/predict.py)            │
│  Blended with Live Telemetry + Dynamic ETA + Weather   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│  Passenger Dashboard (Vite React + FastAPI REST API)   │
│  Dynamic Delay, Live ETA, Risk & Coach Insights        │
└────────────────────────────────────────────────────────┘
```

### What the Model Currently Does
- Ingests 13 timetable, spatial, progress, temporal, and topological density features.
- Predicts expected station arrival delay in minutes without negative values ($\ge 0.0$ min).
- Categorizes delay severity into On-Time ($\le 15$m), Moderate (15–60m), and Severe ($>60$m).
- Generalizes across 2,733 unique Indian Railways trains and 2,972 stations.
- Serves sub-millisecond predictions during live inference.

### What the Model Currently DOES NOT Do
- It does **not** take raw text or natural language prompts as input (it is strict tabular ML).
- It does **not** use real-time live GPS telemetry directly inside the static 13-feature scikit-learn matrix (live delay is blended in the service layer).
- It does **not** directly ingest live weather as a training matrix column (weather is layered via a dedicated heuristic risk engine).
- It does **not** directly ingest locomotive sensor telematics or live CCTV crowd feeds (these are architectural prototypes/future roadmap items).

---

# Part 2 — Machine Learning Model Details

### Exact Current Model Identification
- **Model Name:** Histogram-Based Gradient Boosting Regressor
- **Full Scikit-Learn Class:** `sklearn.ensemble.HistGradientBoostingRegressor`
- **Model Paradigm:** Supervised Learning / Gradient Boosted Decision Trees (GBDT)
- **Problem Type:** Continuous Non-Negative Regression
- **Target Variable:** `arrival_delay_min`
- **Target Data Type:** `float64` / Continuous Numeric
- **Target Measurement Unit:** Minutes ($m$)
- **Output Constraint:** Post-processed with `np.clip(a_min=0.0, a_max=None)` to enforce physical non-negativity.

### Why Regression Is Used
Railway train delay is fundamentally a **continuous physical quantity** representing time variance ($t_{\text{actual}} - t_{\text{scheduled}}$). Classification (e.g., predicting merely "Delayed" vs. "On-Time") discards crucial magnitude information. A passenger needs to know whether a train is 12 minutes late (tolerable) or 180 minutes late (missed connection). Regression outputs exact minutes, which can subsequently be mapped to any discrete severity classification.

### Technical Mechanics of HistGradientBoostingRegressor
`HistGradientBoostingRegressor` is Scikit-learn's optimized implementation of gradient boosted trees, inspired by Microsoft's LightGBM algorithm.

```
                  ┌───────────────────────────────┐
                  │ Target Residuals $r_0 = y - \bar{y}$│
                  └───────────────┬───────────────┘
                                  │
                                  ▼
 ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
 │ Tree 1: Fit  │ ───►     │ Tree 2: Fit  │ ───►     │ Tree M: Fit  │
 │ Residual $r_0$│ Update   │ Residual $r_1$│ Update   │ Residual $r_{M-1}$
 └──────────────┘          └──────────────┘          └──────────────┘
                                  │
                                  ▼
             $\hat{y} = \bar{y} + \eta \sum_{m=1}^{M} f_m(x)$
```

1. **Weak Learners (Decision Trees):** The model constructs an ensemble of shallow decision trees ($M=200$). Each individual tree has limited depth (`max_leaf_nodes=31`), preventing single-tree overfitting.
2. **Sequential Gradient Boosting:** Rather than training independent trees in parallel (like Random Forest), gradient boosting trains trees **sequentially**. Each successive tree fits the negative gradient (the residual error) of the combined ensemble before it.
3. **Histogram-Based Binning:** Continuous numerical features are quantized into 256 discrete integer bins (typically `uint8`). Splitting points are evaluated on histogram bins rather than sorting raw floating-point values at every node. This reduces tree construction time complexity from $\mathcal{O}(N_{\text{samples}} \times N_{\text{features}})$ to $\mathcal{O}(N_{\text{bins}} \times N_{\text{features}})$.
4. **Suitability for Tabular Railway Data:** Railway records feature non-linear interactions (e.g. long distance + evening peak = exponentially higher delay risk). Tree-based histogram models handle non-linearities, mixed categorical/numerical feature spaces, and tabular scale far better than linear models or unregularized deep networks.

### Advantages and Disadvantages
| Advantages | Disadvantages |
| :--- | :--- |
| **Blazing Fast Training:** Fits 41,435 records in **0.75 seconds**. | **No Spatial Extrapolation:** Cannot extrapolate trends beyond minimum/maximum values seen in training trees. |
| **Memory Efficient:** Operates on 256-bin histograms. | **Tabular Only:** Cannot natively process image, raw text, or audio streams. |
| **Robust to Outliers:** Leaf partitioning isolates extreme delays (e.g., 600m fog delays) without distorting global splits. | **Permutation Importance Needed:** Does not output simple linear coefficient weights. |

### Tested Candidate Models
During development, the training pipeline (`ml/train.py`) evaluated two candidate architectures against a naive baseline:
1. `HistGradientBoostingRegressor` (Selected as production model due to superior validation MAE of **39.72m** and 4x faster training speed of **0.75s**).
2. `RandomForestRegressor` (Evaluated as benchmark: Validation MAE **39.96m**, Test MAE **38.63m**, training time **2.96s**).

---

# Part 3 — Scikit-Learn Ecosystem & Architecture

Scikit-learn (`sklearn`) is the core machine learning library powering PredictRail V1. Every data transformation, normalization step, regressor fitting, and metric validation utilizes official Scikit-learn APIs.

### Exact Scikit-Learn Components in Code

| Component Name | Full Python Module / Class | Project File Where Used | Exact Input | Exact Output | Architectural Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ColumnTransformer`** | `sklearn.compose.ColumnTransformer` | `ml/train.py` | Heterogeneous DataFrame containing categorical and numerical columns | Consolidated NumPy 2D array | Applies distinct transformations (OHE vs. Scaling) to specific column subsets simultaneously. |
| **`OneHotEncoder`** | `sklearn.preprocessing.OneHotEncoder` | `ml/train.py` | Categorical strings (`train_type`, `time_of_day`) | Sparse/Dense binary one-hot matrix | Converts string classes into numerical binary dummy variables with `handle_unknown='ignore'`. |
| **`StandardScaler`** | `sklearn.preprocessing.StandardScaler` | `ml/train.py` | 11 continuous numerical feature columns | Standardized features ($\mu=0, \sigma=1$) | Removes mean and scales features to unit variance for stable gradient descent and distance metrics. |
| **`Pipeline`** | `sklearn.pipeline.Pipeline` | `ml/train.py`, `ml/predict.py` | Raw feature DataFrame | Model prediction array | Chained container bundling the preprocessor and regressor into an atomic serialized artifact. |
| **`HistGradientBoostingRegressor`** | `sklearn.ensemble.HistGradientBoostingRegressor` | `ml/train.py` | Preprocessed feature matrix (41,435, $D$) | Continuous delay predictions $\hat{y}$ | Primary regression engine fitted on gradient residuals. |
| **`RandomForestRegressor`** | `sklearn.ensemble.RandomForestRegressor` | `ml/train.py` | Preprocessed feature matrix | Continuous delay predictions $\hat{y}$ | Secondary benchmark comparison ensemble model. |
| **`mean_absolute_error`** | `sklearn.metrics.mean_absolute_error` | `ml/train.py` | Ground truth $y_{\text{true}}$, Predictions $\hat{y}$ | Scalar float (MAE in minutes) | Primary metric measuring average absolute delay error. |
| **`mean_squared_error`** | `sklearn.metrics.mean_squared_error` | `ml/train.py` | Ground truth $y_{\text{true}}$, Predictions $\hat{y}$ | Scalar float (MSE in $\text{min}^2$) | Penalizes large outlier errors; square root gives RMSE. |
| **`r2_score`** | `sklearn.metrics.r2_score` | `ml/train.py` | Ground truth $y_{\text{true}}$, Predictions $\hat{y}$ | Scalar float ($R^2$ coefficient) | Measures proportion of variance explained by model over naive mean. |
| **`median_absolute_error`** | `sklearn.metrics.median_absolute_error` | `ml/train.py` | Ground truth $y_{\text{true}}$, Predictions $\hat{y}$ | Scalar float (MedAE in minutes) | Robust median error unskewed by extreme outliers. |
| **`permutation_importance`** | `sklearn.inspection.permutation_importance` | `ml/train.py` | Fitted Pipeline, $X_{\text{val}}, y_{\text{val}}$ | Array of mean importance scores per feature | Evaluates validation error increase when individual features are randomly shuffled. |

---

# Part 4 — Dataset Architecture & Physical Scale

PredictRail V1 is built on authentic Indian Railways timetable and historical station delay data.

```
                      RAW DATASETS (data/raw/)
                      
┌────────────────────────────────────────┐   ┌────────────────────────────────────────┐
│ indian_railway_schedules.csv          │   │ indian_train_delays.csv                │
│ • 186,124 schedule rows               │   │ • 63,428 delay records                 │
│ • 11,115 Indian trains                 │   │ • Station Code, Train No, Delay        │
│ • 8,151 Indian stations                │   │ • Historical operational logs          │
└───────────────────┬────────────────────┘   └───────────────────┬────────────────────┘
                    │                                            │
                    └─────────────────────┬──────────────────────┘
                                          │ Inner Key Merge on
                                          │ [Train_No_Clean, Station_Code_Clean]
                                          ▼
                      PROCESSED TRAINING DATASET (data/processed/)
                      
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ predictrail_training_data.csv                                                       │
│ • 59,201 Matched Operational Station Stops                                          │
│ • 2,733 Unique Indian Railways Trains                                               │
│ • 2,972 Unique Indian Railways Stations                                             │
│ • 25 Total Columns (13 Features, 3 Targets, 9 Metadata)                             │
│ • 0 Missing Values (100% Complete)                                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Verified Dataset Metrics Table
| Metric / Attribute | Value Verified in Code / Dataset | Description & Verification Source |
| :--- | :--- | :--- |
| **Processed File Path** | `data/processed/predictrail_training_data.csv` | Master training CSV generated by `ml/preprocessing.py`. |
| **Total Operational Records** | **59,201 rows** | Total matched station-stop observations. |
| **Total Columns** | **25 columns** | 13 features + 3 target variations + 9 metadata/split fields. |
| **Unique Train Numbers** | **2,733 trains** | Indian Railways Express, Superfast, Mail, and Passenger services. |
| **Unique Station Codes** | **2,972 stations** | Verified against national station dictionary (NDLS, HWH, CSMT, MAS, etc.). |
| **Missing Values (Nulls)** | **0 (0.00%)** | Zero null values across all 25 columns after imputation. |
| **Duplicate Records** | **0** | Deduplicated on `['Train_No_Clean', 'Station_Code_Clean']`. |
| **Invalid Records Filtered** | **4,227 unmatched rows** | Records lacking corresponding timetable coordinates or valid station keys. |
| **Target Distribution (Mean)** | **48.96 minutes** | Mean historical arrival delay across all matched records. |
| **Target Distribution (Median)**| **21.00 minutes** | Median delay across all matched records. |
| **Target 75th Percentile** | **49.00 minutes** | 75% of train stops experienced $\le 49$ minutes delay. |
| **Target 95th Percentile** | **222.00 minutes** | Extreme tail delays reaching 3.7 hours. |
| **Maximum Recorded Delay** | **1,415.00 minutes** | Major nationwide operational disruption (~23.5 hours). |

---

# Part 5 — Data Sources & Open-Source Attribution

All datasets used in PredictRail V1 originate from open-access Indian Railways repositories:

| Dataset Name | Filename / Path | Publisher / Source URL | License | Role in PredictRail V1 | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Indian Railways Schedules** | `data/raw/indian_railway_schedules.csv` | [github.com/areenakhan07/Indian_Railways](https://github.com/areenakhan07/Indian_Railways) | Open Data Commons / Public Domain | Timetable sequences, scheduled arrival/departure, distances, source/destination. | **REAL DATA (STATIC)** |
| **Historical Station Delays** | `data/raw/indian_train_delays.csv` | [github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning](https://github.com/DeekshithRajBasa/Train-time-delay-prediction-using-machine-learning) | MIT License | Historical recorded station arrival delay observations in minutes. | **REAL DATA (HISTORICAL)** |
| **Express Train Catalog** | `data/raw/Train_List.csv` | [github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets](https://github.com/ankitaanand28/DA323_IndianRailwayTrainDelayDatasets) | CC BY-NC-SA 4.0 | Metro corridor express train metadata and cross-validation reference. | **REAL DATA (STATIC)** |
| **Stations Geographic DB** | `data/raw/stations.json` | [github.com/datameet/railways](https://github.com/datameet/railways) | Open Data Commons (ODbL) / CC-BY-SA | 8,990 Indian railway stations with geographic coordinates (lat/lon) & zones. | **REAL DATA (STATIC REFERENCE)** |
| **Open-Meteo Weather API** | Live REST Endpoint | [open-meteo.com](https://open-meteo.com) | Open Access / CC-BY 4.0 | Real-time temperature, wind speed, precipitation, visibility, and weather codes. | **REAL DATA (LIVE API)** |
| **RailRadar Telemetry API** | Live REST Endpoint | [api.railradar.in](https://api.railradar.in) | Developer API / Proprietary | Live train GPS position, delay minutes, speed, and next halting station. | **REAL DATA (LIVE API)** |
| **Prototype Crowd Dataset** | `data/synthetic/crowd_data.csv` | Internal Generator (`crowd/generate_synthetic.py`) | Project Proprietary / Academic Prototype | Synthetic coach-by-coach passenger counts for UI architectural demonstration. | **SYNTHETIC DATA (PROTOTYPE)** |

---

# Part 6 — Complete Data Schema (Training Pipeline)

The following table details **every single column** present in the master processed dataset (`predictrail_training_data.csv`):

| Column Name | Data Type | Meaning / Definition | Source | Used for ML? | Column Role | Leakage Risk | Notes |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| `train_number` | `string` | Indian Railways 5-digit Train Number (e.g. `12423`) | Schedule CSV | ❌ No | Metadata / Grouping Key | None | Used for Grouped Train Train/Val/Test split. |
| `train_name` | `string` | Official Train Name (e.g. `RAJDHANI EXP`) | Schedule CSV | ❌ No | Metadata / Display | None | Used in preprocessing to classify `train_type`. |
| `station_code` | `string` | IRCTC Station Code (e.g. `NDLS`, `CNB`) | Schedule CSV | ❌ No | Metadata / Indexing | None | High-cardinality ID; converted to density features. |
| `station_name` | `string` | Full Station Name (e.g. `New Delhi`) | Schedule CSV | ❌ No | Metadata / Display | None | User-facing display text. |
| `source_station` | `string` | Train Origin Station Code | Schedule CSV | ❌ No | Metadata | None | Used to compute `corridor_train_density`. |
| `destination_station` | `string` | Train Terminus Station Code | Schedule CSV | ❌ No | Metadata | None | Used to compute `corridor_train_density`. |
| `scheduled_arrival_time` | `string` | Scheduled Arrival Time (`HH:MM:SS`) | Schedule CSV | ❌ No | Timetable Reference | None | Parsed into minute offsets and dwell buffers. |
| `scheduled_departure_time`| `string` | Scheduled Departure Time (`HH:MM:SS`) | Schedule CSV | ❌ No | Timetable Reference | None | Parsed to extract `departure_hour` & `minute`. |
| `split` | `string` | Data Partition (`train`, `val`, `test`) | Pipeline | ❌ No | Partition Tag | None | Deterministic grouped assignment column. |
| `train_type` | `category` | Train Hierarchy Classification | Derived | ✅ **YES** | **Categorical Feature 1** | None | `Premium_Superfast`, `Superfast`, `Mail_Express`. |
| `station_sequence` | `int64` | Stop index along the route ($1, 2, \dots$) | Schedule CSV | ✅ **YES** | **Numeric Feature 1** | None | Monotonically increasing halt index. |
| `distance_km` | `float64` | Cumulative track distance from origin | Schedule CSV | ✅ **YES** | **Numeric Feature 2** | None | Physical track distance in kilometers. |
| `total_route_distance_km` | `float64` | Total route corridor length | Schedule CSV | ✅ **YES** | **Numeric Feature 3** | None | Overall route span from source to destination. |
| `total_route_stops` | `int64` | Total scheduled halts on entire route | Schedule CSV | ✅ **YES** | **Numeric Feature 4** | None | Total station halts planned for this service. |
| `route_distance_progress` | `float64` | $\frac{\text{distance\_km}}{\text{total\_route\_distance\_km}}$ ($0.0 \dots 1.0$) | Derived | ✅ **YES** | **Numeric Feature 5** | None | Normalized spatial fraction of route completed. |
| `route_stop_progress` | `float64` | $\frac{\text{station\_sequence}}{\text{total\_route\_stops}}$ ($0.0 \dots 1.0$) | Derived | ✅ **YES** | **Numeric Feature 6** | None | Normalized sequential fraction of stops completed. |
| `scheduled_halt_duration_min`| `float64` | Scheduled dwell buffer time in minutes | Derived | ✅ **YES** | **Numeric Feature 7** | None | Dwell time: $\text{Dep} - \text{Arr}$ (clipped to $0\dots60m$). |
| `departure_hour` | `int64` | Scheduled departure hour ($0 \dots 23$) | Derived | ✅ **YES** | **Numeric Feature 8** | None | Captures diurnal peak congestion windows. |
| `departure_minute` | `int64` | Scheduled departure minute ($0 \dots 59$) | Derived | ✅ **YES** | **Numeric Feature 9** | None | Fine-grained minute offset within the hour. |
| `time_of_day` | `category` | Diurnal Traffic Window Category | Derived | ✅ **YES** | **Categorical Feature 2** | None | `Morning_Peak`, `Midday`, `Evening_Peak`, `Night`. |
| `station_network_density`| `int64` | Total network services calling at station | Derived | ✅ **YES** | **Numeric Feature 10** | None | Topological junction load & platform bottleneck proxy. |
| `corridor_train_density` | `int64` | Total services sharing source-destination | Derived | ✅ **YES** | **Numeric Feature 11** | None | Line-haul corridor congestion & track frequency. |
| `arrival_delay_min` | `float64` | Actual recorded arrival delay in minutes | Delays CSV | 🎯 **TARGET** | **Primary Regression Target**| N/A | Ground-truth historical delay ($\ge 0.0$ min). |
| `is_delayed` | `int64` | Binary delay flag ($1$ if delay $> 15$m) | Derived | 🎯 Secondary | Auxiliary Binary Target | N/A | Indian Railways official punctuality benchmark. |
| `delay_severity` | `int64` | Multiclass severity ($0$: On-time, $1$: Moderate, $2$: Severe) | Derived | 🎯 Secondary | Auxiliary Multiclass Target | N/A | Discrete classification bucket. |

---

# Part 7 — Target Variable Formulation & Mathematical Mechanics

### Exact Primary Target
$$\text{Target} = \mathbf{\text{arrival\_delay\_min}} \in [0.0, \infty)$$

### Target Definition & Mathematical Construction
The primary target variable represents the **non-negative physical time difference (in minutes)** between the actual timestamp at which a train arrived at a station platform and its scheduled timetable arrival timestamp:

$$\text{Arrival Delay} = \max\left(0.0, \;\; T_{\text{actual\_arrival}} - T_{\text{scheduled\_arrival}}\right)$$

Where $T$ is expressed in minutes from midnight.

### Key Characteristics:
1. **Physical Meaning:** Direct minutes lost on the corridor due to operational, infrastructural, or dispatching constraints.
2. **Non-Negative Bound:** Trains arriving ahead of schedule (early arrivals) are clipped to `0.0` minutes. In railway operations, an early-arriving train is held until its scheduled departure time; early arrivals do not carry "negative delays" to downstream stations.
3. **Missing Target Handling:** Any delay record with invalid or non-numeric entries was filtered out during inner-key merging (`errors='coerce'`). 100% of the 59,201 rows have verified numeric delay values.

### Distinction: Scheduled vs. Actual vs. Predicted vs. Dynamic ETA
- **Scheduled Arrival Time ($T_{\text{sched}}$):** Fixed timetable time published in the official Indian Railways schedule.
- **Actual Arrival Time ($T_{\text{actual}}$):** Historical recorded timestamp when the train physically arrived.
- **Historical Arrival Delay ($D_{\text{actual}}$):** Ground-truth target ($T_{\text{actual}} - T_{\text{sched}}$).
- **Predicted Arrival Delay ($\hat{D}_{\text{ML}}$):** Machine learning output estimating the expected delay minutes.
- **Predicted Dynamic ETA ($\text{ETA}_{\text{dynamic}}$):** The dynamically calculated projected arrival clock timestamp:
$$\text{ETA}_{\text{dynamic}} = T_{\text{sched}} + \hat{D}_{\text{ML}} + \Delta_{\text{propagation}} + \Delta_{\text{weather}}$$

---

# Part 8 — The 13 Production ML Features (In-Depth Analysis)

Every one of the 13 verified features is documented below with its exact derivation, physical meaning, preprocessing, and role:

---

### Feature 1: `train_type`
- **Data Type:** Categorical String
- **Classes:** `Premium_Superfast`, `Superfast`, `Mail_Express`, `Passenger_Local`, `Special`
- **Derivation / Formula:** Derived in `ml/preprocessing.py` using official Indian Railways train numbering and naming conventions:
  - If name contains `RAJDHANI`, `SHATABDI`, `DURONTO`, `VANDE BHARAT`, `TEJAS`, `GARIB RATH` $\rightarrow$ `Premium_Superfast`.
  - If train number starts with `12` or `22`, or name contains `SF`/`SUPERFAST` $\rightarrow$ `Superfast`.
  - Else $\rightarrow$ `Mail_Express`.
- **Operational Rationale:** Indian Railways operates a strict track-priority hierarchy. Premium trains (Rajdhani, Vande Bharat) receive immediate green signals and platform priority over standard Mail/Express trains, resulting in lower delay propagation.
- **Preprocessing:** One-Hot Encoded (`OneHotEncoder(handle_unknown='ignore')`).
- **Feature Importance Rank:** **Rank 5 (Importance Score: 0.0799)**.

---

### Feature 2: `station_sequence`
- **Data Type:** Integer (`int64`)
- **Example Value:** `18` (18th station halt on route)
- **Derivation:** Direct from timetable `SEQ` column.
- **Operational Rationale:** Represents the number of previous opportunities for delay accumulation. Higher sequence stops carry higher probability of compounded dispatch delays.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 9 (Importance Score: 0.0076)**.

---

### Feature 3: `distance_km`
- **Data Type:** Float (`float64`)
- **Example Value:** `1448.5` km
- **Derivation:** Direct from timetable `Distance` column (track distance from origin).
- **Operational Rationale:** Physical travel distance directly correlates with exposure to speed restrictions, signal checks, and track maintenance blocks.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 3 (Importance Score: 0.2430)**.

---

### Feature 4: `total_route_distance_km`
- **Data Type:** Float (`float64`)
- **Example Value:** `2421.4` km (e.g. Dibrugarh to New Delhi)
- **Derivation:** `train_max_dist = merged.groupby('train_number')['distance_km'].transform('max')`.
- **Operational Rationale:** Long-distance intercity trains operate on tighter slack margins and cross multiple zonal railway boundaries, making them significantly more delay-prone than short-distance shuttles.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 2 (Importance Score: 0.2647)**.

---

### Feature 5: `total_route_stops`
- **Data Type:** Integer (`int64`)
- **Example Value:** `38` halts
- **Derivation:** `train_max_stops = merged.groupby('train_number')['station_sequence'].transform('max')`.
- **Operational Rationale:** Each scheduled halt introduces potential passenger boarding delays, luggage loading delays, and locomotive acceleration/deceleration losses.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 4 (Importance Score: 0.1439)**.

---

### Feature 6: `route_distance_progress`
- **Data Type:** Float (`float64`, normalized $0.0 \dots 1.0$)
- **Example Value:** `0.6542` (65.42% of total distance completed)
- **Formula:** 
$$\text{route\_distance\_progress} = \text{clip}\left(\frac{\text{distance\_km}}{\text{total\_route\_distance\_km}}, \; 0.0, \; 1.0\right)$$
- **Operational Rationale:** Captures the relative spatial progression through the corridor independently of absolute kilometers.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 12 (Importance Score: 0.0000)** *(Captures collinear information with distance_km)*.

---

### Feature 7: `route_stop_progress`
- **Data Type:** Float (`float64`, normalized $0.0 \dots 1.0$)
- **Example Value:** `0.7250` (72.5% of total stops completed)
- **Formula:** 
$$\text{route\_stop\_progress} = \text{clip}\left(\frac{\text{station\_sequence}}{\text{total\_route\_stops}}, \; 0.0, \; 1.0\right)$$
- **Operational Rationale:** Captures progress through the sequence of intermediate junctions.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 6 (Importance Score: 0.0269)**.

---

### Feature 8: `scheduled_halt_duration_min`
- **Data Type:** Float (`float64`)
- **Example Value:** `5.0` minutes
- **Formula:** 
$$\text{scheduled\_halt\_duration\_min} = \text{clip}\left(T_{\text{sched\_dep}} - T_{\text{sched\_arr}}, \; 0.0, \; 60.0\right)$$
*(Terminus stations or missing times default to standard 2.0 min buffer)*.
- **Operational Rationale:** Major junctions with 15–20 minute scheduled halts provide operational recovery buffer to make up lost time, whereas 2-minute halts leave zero recovery room.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 8 (Importance Score: 0.0112)**.

---

### Feature 9: `departure_hour`
- **Data Type:** Integer (`int64`, $0 \dots 23$)
- **Example Value:** `18` (6:00 PM departure)
- **Formula:** `(dep_minutes // 60) % 24`
- **Operational Rationale:** Captures time-of-day suburban commuter traffic peaks (08:00–10:00 and 17:00–20:00) which choke mainline tracks entering metro hubs.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 10 (Importance Score: 0.0058)**.

---

### Feature 10: `departure_minute`
- **Data Type:** Integer (`int64`, $0 \dots 59$)
- **Example Value:** `30`
- **Formula:** `dep_minutes % 60`
- **Operational Rationale:** Fine-grained minute offset within the departure slot.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 13 (Importance Score: 0.0000)**.

---

### Feature 11: `time_of_day`
- **Data Type:** Categorical String
- **Classes:** `Morning_Peak` (06:00–10:00), `Midday` (10:00–16:00), `Evening_Peak` (16:00–20:00), `Night` (20:00–06:00)
- **Operational Rationale:** Categorical binning of diurnal operational load, capturing track maintenance windows (typically night) and peak passenger loading times.
- **Preprocessing:** One-Hot Encoded (`OneHotEncoder(handle_unknown='ignore')`).
- **Feature Importance Rank:** **Rank 11 (Importance Score: 0.0025)**.

---

### Feature 12: `station_network_density`
- **Data Type:** Integer (`int64`)
- **Example Value:** `142` (142 total train services call at this station)
- **Formula:** Calculated as the global frequency count of `Station_Code` across the entire Indian Railways master schedule database.
- **Operational Rationale:** Major railway hubs (e.g. Kanpur Central `CNB`, Mughalsarai/Pt. Deen Dayal Upadhyaya `DDU`, Howrah `HWH`) suffer heavy platform and signal congestion. High-density stations act as primary delay multipliers.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 7 (Importance Score: 0.0258)**.

---

### Feature 13: `corridor_train_density`
- **Data Type:** Integer (`int64`)
- **Example Value:** `48` (48 trains operate on this specific origin-destination corridor)
- **Formula:** Frequency count of `(Source_Station, Destination_Station)` pairs across the master schedule.
- **Operational Rationale:** Heavily trafficked trunk corridors (e.g., Delhi–Kolkata, Delhi–Mumbai) experience severe line-haul section saturation, reducing dispatch flexibility when any single train is delayed.
- **Preprocessing:** Standardized (`StandardScaler()`).
- **Feature Importance Rank:** **Rank 1 (Importance Score: 0.4247 — Most Important Feature)**.

---

# Part 9 — Feature Engineering & Transformation Pipeline

```
┌────────────────────────────────────────────────────────┐
│ Raw Railway Record: (Train No, Station, Distance, Time)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Normalization & String Cleaning                │
│ • Strip whitespace, remove leading zeros               │
│ • Upper-case station codes and train names             │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Route Aggregations & Progress Computation      │
│ • Calculate train_max_dist and train_max_stops         │
│ • Compute route_distance_progress & stop_progress      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Operational Time & Dwell Engineering           │
│ • Parse HH:MM:SS to minutes from midnight              │
│ • Compute scheduled_halt_duration_min (clipped 0-60m)  │
│ • Extract departure_hour, departure_minute, time_of_day│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Network & Corridor Density Mapping             │
│ • Map station_network_density via global station load  │
│ • Map corridor_train_density via origin-dest load      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Anti-Leakage Pruning & Validation              │
│ • Drop all actual future arrival/departure columns     │
│ • Verify zero target leakage columns exist             │
└────────────────────────────────────────────────────────┘
```

---

# Part 10 — Data Preprocessing & Serialization

### Preprocessor Architecture
Preprocessing is implemented via Scikit-learn's `ColumnTransformer` inside `ml/train.py`:

```python
preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['train_type', 'time_of_day']),
        ('num', StandardScaler(), [
            'station_sequence', 'distance_km', 'total_route_distance_km',
            'total_route_stops', 'route_distance_progress', 'route_stop_progress',
            'scheduled_halt_duration_min', 'departure_hour', 'departure_minute',
            'station_network_density', 'corridor_train_density'
        ])
    ]
)
```

### Preprocessor Role & Artifact
- **Saved Artifact:** `models/predictrail_preprocessor.joblib` (3.6 KB)
- **Pipeline Role:** The preprocessor stores the exact fitted mean ($\mu$) and standard deviation ($\sigma$) of the 11 continuous features, as well as the exact one-hot category dictionaries of `train_type` and `time_of_day`.
- **Inference Guarantee:** When the backend receives a real-time user query, the preprocessor transforms the query features using the **exact training distribution parameters**, preventing training-serving skew.

---

# Part 11 — Data Leakage Prevention Architecture

### What Is Data Leakage in Railway Delay Modeling?
Data leakage occurs when information that is **physically or temporally impossible to know at prediction time** is inadvertently included in the training feature matrix. If a model is trained using future information, it will achieve near-perfect metrics during evaluation but fail completely in real-world deployment.

### Excluded Leakage Columns
The following columns were explicitly audited and purged from the training dataset:

| Excluded Column | Why It Constitutes Data Leakage | Action Taken |
| :--- | :--- | :---: |
| `future_actual_arrival` | Contains actual timestamps recorded after the train reached downstream stations. | 🚫 **Strictly Excluded** |
| `future_actual_departure`| Contains actual timestamps recorded when the train departed downstream stations. | 🚫 **Strictly Excluded** |
| `downstream_delays` | Contains delay values recorded at subsequent stations along the trip. | 🚫 **Strictly Excluded** |
| `post_trip_cancellations`| Contains cancellation and termination flags recorded after journey failure. | 🚫 **Strictly Excluded** |
| `actual_halt_duration` | Actual platform dwell time is only known after the train departs. | 🚫 **Strictly Excluded** |

### Leakage Verification in Pipeline
`ml/train.py` executes an automated assertion check before fitting:
```python
leakage_cols = ["future_actual_arrival", "future_actual_departure", "downstream_delays", "post_trip_cancellation_flags"]
for lc in leakage_cols:
    if lc in df.columns:
        raise ValueError(f"FATAL: Target leakage detected! Column '{lc}' present in training data.")
```

---

# Part 12 — Grouped Train / Validation / Test Partitioning Strategy

### The Danger of Random Splitting in Railway Data
In standard random splitting (`train_test_split`), rows from the **same train journey** would appear in both the training set and the test set. Because a single train service has correlated spatial and schedule characteristics across its 40 stops, a model evaluated on random row splits would simply "memorize" specific train schedules, inflating performance metrics.

### Grouped Split by Train Number
To measure true out-of-sample generalization to **completely unseen train services**, PredictRail V1 partitions data by **Unique Indian Railways Train Number**:

```
                       ALL UNIQUE TRAIN NUMBERS (2,733 Trains)
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                                         ▼
         70% Unique Trains                         15% Unique Trains & 15% Unique Trains
     (1,913 Trains / 41,435 Rows)                 (410 Trains / 8,642 Rows & 410 Trains / 9,124 Rows)
                 │                                         │
                 ▼                                         ▼
         TRAINING PARTITION                       VALIDATION & TEST HOLDOUTS
```

### Partition Distribution Table
| Partition | Target Share | Unique Trains | Record Count | Realized Share | Purpose |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Train Set** | 70.0% | 1,913 trains | **41,435 records** | 70.0% | Parameter optimization and gradient tree fitting. |
| **Validation Set**| 15.0% | 410 trains | **8,642 records** | 14.6% | Model selection and permutation feature importance. |
| **Holdout Test Set**| 15.0% | 410 trains | **9,124 records** | 15.4% | Final unpolluted benchmark generalization assessment. |

---

# Part 13 — Model Training Workflow & Hyperparameters

### Training Execution Workflow
1. **Load Artifacts:** Load `predictrail_training_data.csv` and `feature_schema.json`.
2. **Partition:** Separate $X$ and $y$ along the pre-assigned `split` column.
3. **Fit Preprocessor:** Compute one-hot encodings and standard scaling on $X_{\text{train}}$.
4. **Fit Regressor:** Fit `HistGradientBoostingRegressor` on preprocessed $X_{\text{train}}$.
5. **Evaluate:** Generate predictions on $X_{\text{val}}$ and $X_{\text{test}}$, apply `np.clip(a_min=0.0)`.
6. **Permutation Importance:** Compute validation permutation importance across 5 random seeds.
7. **Serialize:** Export pipeline to `models/predictrail_delay_model.joblib` and metrics to `models/metrics.json`.

### Exact Model Hyperparameters

| Hyperparameter | Value Configured | Mathematical / Operational Meaning |
| :--- | :---: | :--- |
| `max_iter` | `200` | Total number of boosting iterations (sequential trees built). |
| `learning_rate` ($\eta$) | `0.08` | Shrinkage multiplier scaling the contribution of each new tree. |
| `max_leaf_nodes` | `31` | Maximum number of terminal leaves per decision tree (controls tree complexity). |
| `min_samples_leaf` | `20` | Minimum training samples required in a terminal leaf node (prevents overfitting). |
| `random_state` | `42` | Deterministic seed ensuring 100% reproducible training runs. |
| `loss` | `'squared_error'` | Optimizes mean squared error gradient for robust conditional expectation. |

---

# Part 14 — Candidate Model Comparison & Benchmark Analysis

Both candidate models were evaluated on identical train/validation/test partitions:

| Evaluation Metric | Naive Baseline (Train Mean) | RandomForestRegressor (100 Trees) | HistGradientBoostingRegressor (Selected) |
| :--- | :---: | :---: | :---: |
| **Validation MAE** | 49.75 min | 39.96 min | **39.72 min** (Best) |
| **Validation RMSE** | 86.14 min | 70.09 min | **69.77 min** (Best) |
| **Validation $R^2$** | -0.0002 | 0.3378 | **0.3439** (Best) |
| **Validation MedAE** | 36.00 min | 20.62 min | **19.88 min** (Best) |
| **Validation Within $\pm 30$m** | 38.87% | 62.07% | **64.04%** (Best) |
| **Test MAE** | 46.87 min | **38.63 min** | 39.90 min |
| **Test RMSE** | 78.31 min | **72.67 min** | 74.77 min |
| **Test $R^2$** | -0.0010 | **0.1381** | 0.0874 |
| **Test MedAE** | 36.00 min | **18.96 min** | 19.06 min |
| **Test Within $\pm 10$m** | 10.58% | **31.42%** | 30.43% |
| **Test Within $\pm 30$m** | 39.38% | **65.38%** | 65.06% |
| **Training Speed** | < 0.01 sec | 2.96 sec | **0.75 sec** (4x Faster) |
| **Selected for Production?** | ❌ No | ❌ Benchmark Only | ✅ **YES (Production Model)** |

### Why HistGradientBoostingRegressor Was Selected
1. **Best Validation Generalization:** Achieved the lowest Validation MAE (**39.72 min**) and highest Validation $R^2$ (**0.3439**).
2. **Computational Speed:** Fits in **0.75 seconds**, enabling rapid model updates.
3. **Compact Serialization:** Serializes into a lightweight artifact (**746 KB**) suitable for serverless and low-memory edge deployments.

---

# Part 15 — Model Performance Metrics & Interpretation

### Exact Verified Test Metrics (HistGradientBoostingRegressor)
- **Test Mean Absolute Error (MAE):** **39.90 minutes**
- **Test Root Mean Squared Error (RMSE):** **74.77 minutes**
- **Test Coefficient of Determination ($R^2$):** **0.0874**
- **Test Median Absolute Error (MedAE):** **19.06 minutes**
- **Predictions within $\pm 10$ Minutes:** **30.43%**
- **Predictions within $\pm 30$ Minutes:** **65.06%**

### Explanation of Metrics
1. **MAE (39.90 min):** On average, the model's delay prediction is within ~40 minutes of actual arrival across unseen national routes spanning up to 3,000 km.
2. **MedAE (19.06 min):** For 50% of all train stops, the absolute prediction error is **under 19.1 minutes**. The median error is significantly lower than the MAE because extreme disruption events (e.g. 10-hour fog delays) inflate the arithmetic mean.
3. **RMSE (74.77 min):** Higher than MAE due to quadratic penalization of extreme delay tails.
4. **$R^2$ (0.0874 on Holdout Test vs. 0.3439 on Validation):** The drop in $R^2$ reflects the high stochastic variance of real-world railway operations when testing on completely unseen train routes with long corridors.

### Critical Distinction: "65.06% Within $\pm 30$ Minutes" is NOT "65% Accuracy"
> [!WARNING]
> In technical and jury presentations, **never describe "65.06% within $\pm 30$ minutes" as "65% accuracy"**.  
> - "Accuracy" is a metric strictly defined for classification ($\frac{\text{Correct}}{\text{Total}}$).  
> - In continuous regression, "65.06% within $\pm 30$ minutes" is a **Punctuality Tolerance Window**. It means that for 65 out of 100 unseen train stops, the predicted arrival time is within a practical 30-minute operational window of reality.

---

# Part 16 — Naive Baseline Model Evaluation

### What the Baseline Predicts
The baseline model computes the simple scalar **arithmetic mean of all delays in the training set**:
$$\hat{y}_{\text{baseline}} = \bar{y}_{\text{train}} = 48.24 \text{ minutes}$$
It outputs 48.24 minutes for every single query regardless of train class, distance, or station.

### Why the Baseline is Necessary
A machine learning model has zero scientific value unless it provably outperforms a naive heuristic.

### ML Model vs. Baseline Comparison
- **Baseline Test MAE:** 46.87 minutes
- **ML Model Test MAE:** 39.90 minutes
- **Improvement:** The ML model achieves a **~15% reduction in absolute prediction error** on the test set and a **~20% reduction on the validation set** over the baseline. Furthermore, the ML model nearly doubles the proportion of predictions within $\pm 10$ minutes (from 10.58% to 30.43%).

---

# Part 17 — Feature Importance (Permutation Analysis)

Feature importance was calculated via **Permutation Feature Importance** on the validation partition across 5 repetitions (`models/feature_importance.json`):

```
Rank  Feature                       Importance Score  Operational Impact
──────────────────────────────────────────────────────────────────────────────────────────
1.    corridor_train_density        0.4247            Corridor line-haul saturation & frequency
2.    total_route_distance_km       0.2647            Overall corridor span & zonal crossings
3.    distance_km                   0.2430            Track distance covered so far
4.    total_route_stops             0.1439            Number of intermediate halts & platform events
5.    train_type                    0.0799            Train hierarchy & track dispatch priority
6.    route_stop_progress           0.0269            Fraction of stops completed
7.    station_network_density       0.0258            Junction complexity & track crossing load
8.    scheduled_halt_duration_min   0.0112            Recovery dwell buffer at platform
9.    station_sequence              0.0076            Stop index along route
10.   departure_hour                0.0058            Diurnal peak congestion window
11.   time_of_day                   0.0025            Diurnal peak traffic category
12.   route_distance_progress       0.0000            Collinear with distance_km
13.   departure_minute              0.0000            Fine-grained minute offset
```

### What Feature Importance Means
Permutation importance measures the increase in model prediction error when a specific feature's values are randomly shuffled, breaking its relationship with the target. A high score (e.g. 0.4247 for `corridor_train_density`) indicates that corridor traffic density is the single strongest structural predictor of delay magnitude.

### What Feature Importance DOES NOT Mean
Feature importance **does not prove direct physical causation**. It indicates statistical predictive power within the tree ensemble, not that adding a single train directly causes exactly 0.42 minutes of delay.

---

# Part 18 — Serialized Model Artifacts & File Registry

The `models/` directory contains 4 production artifacts generated by `ml/train.py`:

| Filename | File Size | Format | Generated By | Loaded By | Architectural Role |
| :--- | :---: | :---: | :--- | :--- | :--- |
| `predictrail_delay_model.joblib` | 747 KB | Joblib Binary | `ml/train.py` | `ml/predict.py` | Complete Scikit-Learn `Pipeline` containing fitted preprocessor and trained `HistGradientBoostingRegressor`. |
| `predictrail_preprocessor.joblib` | 3.6 KB | Joblib Binary | `ml/train.py` | `ml/train.py` | Standalone `ColumnTransformer` containing fitted scaler and encoder parameters. |
| `feature_importance.json` | 423 B | JSON | `ml/train.py` | Analytics / Docs | Machine-readable dictionary of ranked permutation feature importance scores. |
| `metrics.json` | 2.4 KB | JSON | `ml/train.py` | Dashboard API / Docs | Full machine-readable evaluation report containing train/val/test metrics and candidate comparisons. |

---

# Part 19 — Real-Time Inference Pipeline

Inference is executed by `ml/predict.py` and wrapped by `backend/services.py`:

```
User Queries Train #12423 & Station CNB
                  │
                  ▼
FastAPI Route /predict Receives JSON Request
                  │
                  ▼
Service Layer Looks Up Timetable Metadata for Stop (SEQ, Distance, Route Stops)
                  │
                  ▼
Graph Module Injects Station Density (station_network_density = 142)
                  │
                  ▼
Feature Vector Assembled (13 Features) with Default Imputation Fallbacks
                  │
                  ▼
Lazy-Loaded Pipeline (predictrail_delay_model.joblib) Transforms Features & Predicts
                  │
                  ▼
np.clip(a_min=0.0) Enforces Physical Non-Negativity
                  │
                  ▼
Delay Severity Classification & Dynamic Momentum Blending (if Live Delay > 0)
                  │
                  ▼
JSON Response Returned to React UI in < 15ms
```

### Key Engineering Features in Inference
1. **Lazy Loading:** `get_model()` loads the serialized joblib file into global memory on first call and reuses the cached object across all subsequent HTTP requests.
2. **Default Imputation:** If any feature key is missing in the payload, `predict.py` automatically injects safe default values (e.g. `scheduled_halt_duration_min=2.0`).
3. **Momentum Blending:** When a significant live delay is reported upstream ($D_{\text{live}} > 0$), `service_predict_delay()` blends the live delay momentum with the ML structural prediction:
$$\hat{D}_{\text{blended}} = 0.70 \times D_{\text{live}} + 0.30 \times \hat{D}_{\text{ML}}$$

---

# Part 20 — Model Output Schema & Severity Classification

The inference engine produces the following structured output payload:

```json
{
  "predicted_delay_min": 28.4,
  "delay_severity_category": "Moderate Delay (15 - 60 min)",
  "delay_severity_code": 1,
  "is_delayed": true,
  "punctuality_status": "Delayed"
}
```

### Severity Classification Thresholds

| Severity Class | Code | Delay Range | Operational Status | UI Badge Color |
| :--- | :---: | :---: | :--- | :---: |
| **On-Time / Minor** | `0` | $\le 15.0$ minutes | Within Indian Railways official punctuality buffer. | Green |
| **Moderate Delay** | `1` | $15.1 \dots 60.0$ minutes | Moderate schedule deviation; connection caution. | Amber |
| **Severe Delay** | `2` | $> 60.0$ minutes | Critical delay; high probability of missed connecting services. | Red |

---

# Part 21 — Real-Time Telemetry Integration (RailRadar)

Real-time train running status is integrated via `backend/railradar_client.py`:

```
┌────────────────────────────────────────────────────────────────────────┐
│ RailRadar REST API: https://api.railradar.in/v1/trains/{number}/live    │
│ Headers: Authorization: Bearer <API_KEY>, Accept: application/json    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
        API Key Configured                    Offline / No Key
                  │                                   │
                  ▼                                   ▼
        Live Upstream Fetch               Timetable Schedule Fallback
        • Live GPS Coordinates            • Generates schedule-grounded
        • Current Delay (Minutes)           telemetry from internal DB
        • Next Halting Station            • Realistic speed & position
        • Passed & Remaining Stops        • 100% testable without key
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    │
                                    ▼
       In-Memory TTL Cache (30s) & Coordinate Enrichment via stations.json
```

### Live Telemetry Fields & Usage Matrix

| Live Telemetry Field | Directly Enters ML Training Matrix? | Used in Service Layer? | Used in Dynamic ETA? | Used in React UI? | Architectural Role |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `current_delay_minutes` | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | Injected into dynamic ETA propagation and momentum blending. |
| `current_station_code` | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | Filters out departed stations from dropdown. |
| `latitude` / `longitude` | ❌ No | ❌ No | ❌ No | ✅ Yes | Renders live pulsating train marker on Leaflet map. |
| `speed_kmph` | ❌ No | ❌ No | ❌ No | ✅ Yes | Displays live speed telemetry in header card. |
| `passed_stations` | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | Defines route bounds for remaining-journey analysis. |
| `is_arrived` | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes | Triggers completed journey state (`Arrival: 0 min`). |

---

# Part 22 — Architectural Gap: Current Model vs. Planned Richer Model

| Feature / Domain | Current ML Model (V1 Verified) | Next Evolution (Planned V2) | Why Not in Current Model Matrix? |
| :--- | :---: | :---: | :--- |
| **13 Static Timetable Features** | ✅ **Included** | ✅ **Included** | Core foundation verified from timetable dataset. |
| **Live Upstream Delay** | ⚠️ *Service Blended Only* | 🔲 *Direct ML Feature* | Historical training dataset lacked continuous live GPS timestamp streams. |
| **Previous Station Delay** | ❌ Excluded | 🔲 *Direct ML Feature* | Requires sequential time-series logs per trip. |
| **Meteorological Risk (Weather)** | ⚠️ *Heuristic Layer Only* | 🔲 *Direct ML Feature* | Requires historical weather archives merged by timestamp and station coordinates. |
| **Locomotive Telemetry / Health** | ❌ Excluded | 🔲 *Direct ML Feature* | Locomotive maintenance records are not publicly exposed by Indian Railways. |
| **Real Passenger Crowd Feeds** | ⚠️ *Synthetic Prototype Only*| 🔲 *Direct ML Feature* | IRCTC ticketing and PRS reservation data is restricted/confidential. |
| **Graph Delay Propagation** | ⚠️ *NetworkX Heuristic* | 🔲 *Graph Neural Network* | GNN requires dynamic edge-flow training infrastructure. |
| **Freight Train Conflicts** | ❌ Excluded | 🔲 *Direct ML Feature* | Freight movement data (FOIS) is operational and non-public. |

---

# Part 23 — Locomotive Telemetry & Engineering Features

### Proposed Future Locomotive Feature Schema
In future versions, locomotive telemetry can provide critical failure risk indicators. A train may change locomotives mid-journey (e.g. diesel to electric changeover at junction hubs).

### Required Time-Aligned Locomotive Assignment Schema
```
train_id:             12423
service_date:         2026-09-10
loco_id:              WAP-7 #30245
loco_type:            Electric (6,000 HP)
loco_assigned_at:     GHY (Guwahati, Stop #4)
loco_removed_at:      NDLS (New Delhi, Stop #38)
distance_since_poh:   14,280 km (Periodic Overhaul)
reliability_score:    0.982
```

> [!IMPORTANT]
> **Authenticity Rule:** PredictRail V1 does **not** generate fake locomotive health scores. Locomotive features are documented as an architectural specification for future enterprise integration when Indian Railways exposes locomotive telematics.

---

# Part 24 — Meteorological Risk & Future Multi-Station Weather Modeling

### Current Weather Implementation (`weather/`)
PredictRail V1 integrates real-time meteorological data from **Open-Meteo API**:
- Fetches real-time temperature, wind speed, precipitation, visibility, and WMO weather codes using station coordinates from `stations.json`.
- `calculate_weather_risk()` computes a transparent rule-based risk score ($0 \dots 100$):
  - `FOG` / Visibility $< 200m \rightarrow$ Risk Score 80, Delay Buffer $+30$ min.
  - `THUNDERSTORM` $\rightarrow$ Risk Score 85, Delay Buffer $+25$ min.
  - `HEAVY_RAIN` $\rightarrow$ Risk Score 65, Delay Buffer $+18$ min.
  - `CLEAR` $\rightarrow$ Risk Score 5, Delay Buffer $+0$ min.

```
                      PLANNED MULTI-STATION ROUTE WEATHER
                      
   Station 1 (HWH)         Station 2 (BWN)         Station 3 (ASN)         Station 4 (DHN)
   ETA: 10:00 AM           ETA: 11:15 AM           ETA: 12:30 PM           ETA: 01:45 PM
   Weather: Clear          Weather: Light Rain     Weather: Heavy Rain     Weather: Fog
   Risk: 5/100             Risk: 20/100            Risk: 65/100            Risk: 80/100
   Buffer: +0m             Buffer: +3m             Buffer: +18m            Buffer: +30m
```

---

# Part 25 — Dynamic Reaction to Sudden Live Operational Changes

PredictRail V1 reacts dynamically to real-time upstream telemetry updates:

```
Live RailRadar Telemetry Poll (Every 35s)
                  │
                  ▼
Detect Telemetry Delta (e.g. Current Delay Jumps 8m ──► 35m)
                  │
                  ▼
Re-compute Dynamic Feature Vector for Remaining Route Stops
                  │
                  ▼
Re-run Fast Model Inference (0.75ms Evaluation)
                  │
                  ▼
Re-calculate Dynamic ETA & Downstream Delay Propagation
                  │
                  ▼
Emit PREDICTION_UPDATED Event & Refresh Frontend Dashboard
```

> [!NOTE]
> **Inference vs. Retraining:** Reacting to live operational changes executes **rapid forward-pass inference**; it does **not** retrain model weights. Retraining occurs offline during scheduled pipeline runs.

---

# Part 26 — Terminus & Destination Arrival Logic

When a train completes its journey and arrives at its final scheduled terminus:
1. **Status Tag:** `Status: ARRIVED · Journey Completed`.
2. **Remaining Arrival Time:** Fixed to **`0.0 minutes`**.
3. **No Future Projections:** Suppresses future ETA clocks, downstream station forecasts, and upcoming weather queries.
4. **Historical Delay Preservation:** The actual recorded arrival delay at the terminus is preserved and displayed; it is never erased.

---

# Part 27 — Search Workflow & Active Corridor Bounds

```
User Searches Train Number (e.g. 12423)
                  │
                  ▼
System Retrieves Complete Route & Active Telemetry
                  │
                  ▼
Identify Passed vs. Current vs. Remaining Stations
• Passed Stations: [DBRG, DMV, LMG] ──► Excluded from Observation Selection
• Current Position: KLGR (Kalyanpur)
• Remaining Stations: [GHY, NCB, NJP, KIR, PNBE, CNB, NDLS] ──► Active Selection
                  │
                  ▼
Prediction Evaluated Strictly Across Remaining Corridor
```

---

# Part 28 — Network Congestion & Topological Density Features

### Verified Density Features in Current Model
1. **`station_network_density`:** Network-wide train service volume passing through the station. Stations like `CNB` (Kanpur Central) with density > 140 reflect high track-crossing conflict probabilities.
2. **`corridor_train_density`:** Trunk line-haul service density sharing the same origin-destination corridor.

---

# Part 29 — Mixed Freight and Passenger Interaction Dynamics

In the Indian Railways network, high-speed passenger trains share tracks with heavy freight rakes. Freight trains have longer stopping distances and slower acceleration, creating "moving bottlenecks" on double-track sections. In future releases, section block occupancy from freight movement logs will be integrated as dynamic corridor density features.

---

# Part 30 — Predictive Train Conflict Modeling

Future iterations will evaluate junction crossing conflicts:
$$\text{Conflict Probability} = f\left(\Delta t_{\text{arrival}}, \; \text{Track Topology}, \; \text{Priority Hierarchy}\right)$$
The system will predict expected waiting delays without issuing hardcoded control commands.

---

# Part 31 — Network Delay Propagation Engine

Implemented in `graph/delay_propagation.py`:
- Models the railway network as a directed topological graph using NetworkX.
- Propagates delay forward along downstream station nodes with an exponential decay/recovery factor ($\lambda = 0.94$) combined with junction bottleneck penalties:
$$D_{i+1} = \max\left(0, \; D_i \times \lambda + \Delta_{\text{bottleneck}} - \Delta_{\text{dwell\_buffer}}\right)$$

---

# Part 32 — Graph AI & Graph Neural Networks (GNN) vs. Tabular ML

| Dimension | Current Tabular ML (`HistGradientBoostingRegressor`) | Planned Future Graph Neural Network (GNN) |
| :--- | :--- | :--- |
| **Data Representation** | Flat 13-feature vector per station halt. | Graph with Node Features (stations) and Dynamic Edge Flows (trains). |
| **Topology Modeling** | Density aggregations (`station_network_density`). | Spatial graph convolution over NetworkX railway graph. |
| **Inference Speed** | Sub-millisecond ($< 1$ ms). | 10–50 ms. |
| **Implementation Status** | ✅ **CURRENT PRODUCTION MODEL** | 🔲 **FUTURE ENHANCEMENT (NOT IN V1)** |

---

# Part 33 — Dynamic ETA Engine & Time Accumulation Mathematics

Implemented in `eta/dynamic_eta.py` and `eta/eta_calculator.py`:
1. **Midnight Rollover Tracking:** Detects multi-day journeys when arrival minutes drop backwards ($T_{\text{arr}} < T_{\text{prev\_dep}} - 180m$), incrementing the journey calendar day index.
2. **Dynamic Timestamp Calculation:**
$$\text{ETA Timestamp} = \text{Datetime}_{\text{scheduled\_dep}} + \text{timedelta}\left(\text{minutes} = \hat{D}_{\text{blended}}\right)$$

---

# Part 34 — Prototype Crowd Density & Compartment Recommendation

### Implementation & Scope (`crowd/`)
- **Synthetic Prototype:** Generates realistic coach-by-coach passenger occupancy distributions across AC First (`1A`), AC 2-Tier (`2A`), AC 3-Tier (`3A`), Sleeper (`SL`), and General Unreserved (`GEN`).
- **Compartment Recommender (`recommend_smart_compartment`):** Evaluates available travel classes against passenger budget filters, recommending the least crowded coach class with domain justifications.
- **Academic Transparency:** Clearly marked as synthetic prototype data in all API schemas and UI disclaimers.

---

# Part 35 — Honest Model Limitations & Vulnerabilities

1. **Test MAE of 39.90 Minutes:** Inherent to long-distance Indian train operations; predictions represent expected trend rather than minute-exact guarantees.
2. **Low Test $R^2$ (0.0874):** Extreme tail disruptions (e.g. 10-hour fog delays) create massive variance in holdout test partitions.
3. **No Direct Live Delay in Training Matrix:** Model predicts baseline structural delay; live delay is currently blended at the service layer.
4. **Synthetic Crowd Layer:** Crowd data is prototype-only; not connected to live IRCTC PRS reservation counters.

---

# Part 36 — Why HistGradientBoostingRegressor is Scientifically Valid

1. **Tabular State-of-the-Art:** Gradient boosted decision trees consistently outperform deep neural networks on tabular datasets with mixed feature distributions.
2. **Rapid Deterministic Inference:** Evaluates in $< 1$ ms on CPU without requiring GPU acceleration.
3. **High Interpretability:** Permutation feature importance provides clear operational explanations to railway mentors and jurors.

---

# Part 37 — Why Generative AI is Inappropriate for Numerical Delay Estimation

> [!IMPORTANT]
> **Scientific Stance:** Large Language Models (Generative AI) are probabilistic text completion engines prone to numerical hallucinations. They cannot solve continuous physical delay regression. PredictRail uses **Scikit-learn GBDT regression** for rigorous numerical calculation, reserving LLMs strictly for natural-language advisory explanations.

---

# Part 38 — PredictRail ML Evolution Roadmap

```
Phase 1: Current V1 Tabular GBDT Baseline (HistGradientBoostingRegressor + 13 Features)  [DONE]
Phase 2: Historical Time-Series Live Delay Ingestion in Training Matrix                  [PLANNED]
Phase 3: Spatio-Temporal Historical Weather Alignment                                    [PLANNED]
Phase 4: Locomotive Telematics & Reliability Features                                    [PLANNED]
Phase 5: Real-World PRS Passenger Crowd Ingestion                                        [PLANNED]
Phase 6: Mixed Freight-Passenger Section Conflict Engine                                 [PLANNED]
Phase 7: End-to-End Spatio-Temporal Graph Neural Network (GNN) Deployment               [PLANNED]
```

---

# Part 39 — Recommended Future Enterprise Dataset Specification

```sql
CREATE TABLE predictrail_enterprise_v2 (
    trip_id VARCHAR(64) PRIMARY KEY,
    train_number VARCHAR(10) NOT NULL,
    service_date DATE NOT NULL,
    station_code VARCHAR(10) NOT NULL,
    station_sequence INT NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP NOT NULL,
    arrival_delay_min FLOAT NOT NULL,
    upstream_observed_delay_min FLOAT NOT NULL,
    locomotive_id VARCHAR(20),
    locomotive_health_score FLOAT,
    station_precipitation_mm FLOAT,
    station_visibility_meters FLOAT,
    section_freight_rake_count INT,
    coach_occupancy_ratio FLOAT
);
```

---

# Part 40 — Training Data vs. Live Inference Data Compatibility Matrix

| Domain Feature | Training Pipeline Representation | Live Inference Ingestion | Schema Compatibility |
| :--- | :--- | :--- | :---: |
| `train_type` | Derived string from train name/number | Auto-classified from timetable | 100% Compatible |
| `distance_km` | Timetable distance column | Timetable lookup | 100% Compatible |
| `station_network_density` | Pre-computed frequency map | Graph congestion lookup | 100% Compatible |
| `corridor_train_density` | Pre-computed pair frequency | Corridor dictionary lookup | 100% Compatible |
| `current_delay_minutes` | Not in static 13-feature matrix | Ingested via RailRadar API | Blended in Service Layer |
| `weather_risk` | Heuristic layer | Ingested via Open-Meteo API | Layered in Service Layer |

---

# Part 41 — Data Freshness, Caching & Stale Telemetry Handling

- **Live Telemetry TTL Cache:** 30 seconds (`_LIVE_STATUS_CACHE` in `railradar_client.py`).
- **Weather Cache:** In-memory caching per station code to respect Open-Meteo rate limits.
- **Frontend Auto-Polling:** 35-second background polling cycle in React dashboard.
- **Stale Fallback:** If upstream live API returns 502/timeout, backend seamlessly falls back to schedule-grounded timetable telemetry.

---

# Part 42 — Model Robustness, Edge Cases & Fault Tolerance

1. **Unknown Stations / Trains:** Gracefully caught with HTTP 404 and structured error messages.
2. **Missing Input Features:** Imputed with safe default dictionaries in `ml/predict.py`.
3. **Non-Negative Output Clipping:** `np.clip(a_min=0.0)` guarantees delay predictions never output negative numbers.
4. **Empty API Responses:** Falls back to internal schedule database with zero crash risk.

---

# Part 43 — Security, Data Privacy & API Protection

1. **Zero Secret Leaks:** API keys (`RAILRADAR_API_KEY`) are loaded strictly from server-side `.env` files and never exposed to the client bundle.
2. **CORS Configuration:** Configured to allow verified frontend origins and Vercel preview domains (`https://.*\.vercel\.app`).
3. **Input Validation:** Strict Pydantic schemas (`backend/schemas.py`) enforce type safety and reject malformed inputs.

---

# Part 44 — Full End-to-End Technical System Architecture

```
                    ┌──────────────────────────────────────┐
                    │      React Frontend (Vite V1)        │
                    │  • Interactive Leaflet Map           │
                    │  • Dynamic ETA & Delay Gauges        │
                    │  • Real-time Header Telemetry Badge  │
                    └──────────────────┬───────────────────┘
                                       │ HTTP / JSON REST
                                       ▼
                    ┌──────────────────────────────────────┐
                    │      FastAPI Backend Engine          │
                    │  • /predict, /eta, /weather, /crowd  │
                    │  • Pydantic Input/Output Validation  │
                    └──────────────────┬───────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
│ Machine Learning │          │ Network Topology │          │ External APIs    │
│ Pipeline         │          │ & Propagation    │          │ & Live Feeds     │
│ • HistGradBoost  │          │ • NetworkX Graph │          │ • RailRadar Live │
│ • 13 Features    │          │ • Bottlenecks    │          │ • Open-Meteo     │
│ • StandardScaler │          │ • Delay Decay    │          │ • GeoJSON Stns   │
└──────────────────┘          └──────────────────┘          └──────────────────┘
```

---

# Part 45 — File-by-File Repository Mapping

| File Path | Primary Purpose | ML / Architectural Role | Key Functions / Classes |
| :--- | :--- | :--- | :--- |
| `ml/train.py` | Model training & evaluation pipeline | Fits preprocessor, trains GBDT & RF models, exports metrics | `main()`, `verify_dataset()`, `evaluate_predictions()` |
| `ml/preprocessing.py` | Raw data cleaning & feature engineering | Merges raw schedules with delays, creates 13 features | `preprocess_indian_railway_data()`, `classify_train_type()` |
| `ml/predict.py` | Forward-pass inference module | Lazy-loads pipeline, imputes defaults, executes predictions | `predict_delay()`, `get_model()` |
| `backend/main.py` | FastAPI REST application | Defines REST endpoints, CORS, exception handlers | `predict_delay_endpoint()`, `combined_predict_endpoint()` |
| `backend/services.py` | Master service orchestration layer | Connects ML, graph, ETA, weather, and crowd modules | `service_predict_delay()`, `service_get_combined_prediction()` |
| `backend/schemas.py` | Pydantic data schemas | Defines strict input/output request and response models | `DelayPredictionResponse`, `CombinedPredictionResponse` |
| `backend/railradar_client.py`| Live API client & cache manager | Ingests real-time train telemetry with schedule fallback | `RailRadarClient`, `get_live_train_status()` |
| `eta/dynamic_eta.py` | Dynamic ETA calculation engine | Propagates delays, tracks midnight rollover, builds ETAs | `get_dynamic_eta()`, `compute_dynamic_eta_timestamp()` |
| `graph/congestion.py` | Network graph & bottleneck engine | Builds NetworkX railway graph, calculates centrality | `get_graph()`, `get_bottlenecks()`, `get_station_congestion()`|
| `graph/delay_propagation.py`| Delay decay & propagation module | Simulates downstream station delay propagation | `simulate_delay_propagation()` |
| `weather/open_meteo.py` | Meteorological API client | Fetches real-time weather from Open-Meteo | `fetch_station_weather()`, `get_station_coordinates()` |
| `weather/weather_risk.py` | Weather risk heuristic engine | Translates weather into risk scores and delay buffers | `calculate_weather_risk()`, `apply_weather_adjustment_to_eta()` |
| `crowd/crowd_detector.py` | Coach density detection | Estimates prototype passenger occupancy per coach | `estimate_station_crowd()`, `load_crowd_data()` |
| `crowd/recommendation.py` | Smart compartment recommender | Recommends least-crowded travel class by budget | `recommend_smart_compartment()` |

---

# Part 46 — Beginner & Viva-Style Conceptual Explanations

### Simple English Explanation
Imagine you are driving a car from New Delhi to Kolkata (1,500 km). If you ask: *"Will I reach on time?"*, you cannot just check your current speed. You have to consider:
1. Is it a high-speed express highway or a local road? (`train_type`)
2. How many busy city intersections must you pass through? (`total_route_stops`, `station_network_density`)
3. How many other vehicles share this highway? (`corridor_train_density`)
4. Are you driving during peak rush hour? (`departure_hour`, `time_of_day`)

PredictRail's machine learning model learned these relationships from **59,201 real train trips**. When you select a train, it analyzes these 13 conditions and predicts your expected delay in minutes.

### Tanglish Explanation (For College / Viva / Mentor Explanation)
> *"PredictRail enna pannudhu-na, Indian Railways-la oru train start aagi destination pora varaikkum, entha station-la evlo minutes delay aagum-nu ML model vechi predict pannudhu.*  
> *Idhula 59,201 real Indian Railway records use panni, `HistGradientBoostingRegressor` model train pannirukkom. Model-ku 13 safe features tharom — like train type, corridor traffic, station junction density, and travel distance. Future arrival time edhuvum kudukala, so zero data leakage.*  
> *Live train status maara maara, backend dynamically re-calculate panni exact dynamic ETA and weather risk dashboard-la render pannidum."*

---

# Part 47 — Hackathon Jury & Technical Reviewer Q&A (35 Questions)

1. **Q: What exact ML model is used in PredictRail?**  
   *A:* `sklearn.ensemble.HistGradientBoostingRegressor` (Histogram-based gradient boosted decision trees).
2. **Q: Why did you choose regression over classification?**  
   *A:* Delay is a continuous physical variable (minutes). Regression outputs exact minutes, which can be thresholded into severity classes.
3. **Q: Why not use Deep Learning / Neural Networks?**  
   *A:* Tabular tabular data with mixed categorical/numeric distributions is best modeled by gradient boosted trees. GBDT trains in 0.75s, uses minimal memory, and outperforms unregularized neural nets on tabular data.
4. **Q: Why not use Generative AI (LLMs) for ETA calculation?**  
   *A:* LLMs hallucinate numbers. Precise numerical delay prediction requires deterministic mathematical regression.
5. **Q: What dataset was used and how many records?**  
   *A:* 59,201 matched Indian Railways operational station stops across 2,733 unique trains and 2,972 stations.
6. **Q: How did you prevent data leakage?**  
   *A:* Purged all future-state columns (`future_actual_arrival`, `downstream_delays`) and used a Grouped Split by Train Number.
7. **Q: What is your Test MAE?**  
   *A:* 39.90 minutes on completely unseen holdout train routes.
8. **Q: What does "65.06% within $\pm 30$ minutes" mean?**  
   *A:* It is a punctuality tolerance metric: 65% of test predictions fall within 30 minutes of ground truth. It is not classification accuracy.
9. **Q: What is the single most important feature?**  
   *A:* `corridor_train_density` (Permutation Importance Score: 0.4247).
10. **Q: How does the model handle early arriving trains?**  
    *A:* Predictions and targets are clipped to non-negative values ($\ge 0.0$ min) via `np.clip(a_min=0.0)`.
11. **Q: Does the live API retrain the model?**  
    *A:* No. Live API updates execute rapid forward-pass inference in $< 1$ ms; model weights remain fixed.
12. **Q: What happens when a train reaches its destination?**  
    *A:* The system transitions to `Status: ARRIVED`, sets remaining time to 0, and halts future projections.
13. **Q: How is real-time weather integrated?**  
    *A:* Via Open-Meteo API as a heuristic risk layer ($0\dots100$) that adjusts the final dynamic ETA buffer.
14. **Q: Is the crowd data real Indian Railways data?**  
    *A:* No, it is a synthetic prototype dataset built for academic demonstration, as IRCTC PRS data is non-public.
15. **Q: What is the difference between your model and NTES?**  
    *A:* NTES shows where the train *was*; PredictRail uses ML and graph theory to forecast where and when it *will be*.
16. **Q: Why is your Test $R^2$ (0.0874) lower than Validation $R^2$ (0.3439)?**  
    *A:* Grouped splitting tests on unseen long corridors where stochastic operational disruptions cause high variance.
17. **Q: How do you handle missing values during inference?**  
    *A:* `ml/predict.py` contains pre-defined default fallback dictionaries for all 13 features.
18. **Q: What algorithm was used for benchmark comparison?**  
    *A:* `RandomForestRegressor` (100 trees), achieving Test MAE 38.63m.
19. **Q: How do you track multi-day midnight crossings?**  
    *A:* `dynamic_eta.py` detects when scheduled arrival minutes drop backwards while distance increases, incrementing day counters.
20. **Q: What is the role of NetworkX in PredictRail?**  
    *A:* It constructs the 2,972-node railway graph to compute station bottleneck scores and simulate delay propagation.
21. **Q: Is there a Graph Neural Network (GNN) currently running?**  
    *A:* No. GNN is an item on our future roadmap; V1 uses tabular GBDT + NetworkX heuristic propagation.
22. **Q: How are categorical features encoded?**  
    *A:* Via `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`.
23. **Q: How are numerical features scaled?**  
    *A:* Standardized to $\mu=0, \sigma=1$ using `StandardScaler`.
24. **Q: What is the training time of your production model?**  
    *A:* 0.75 seconds on 41,435 training records.
25. **Q: How many features does the model take?**  
    *A:* Exactly 13 safe features.
26. **Q: What are the two categorical features?**  
    *A:* `train_type` and `time_of_day`.
27. **Q: What is `station_network_density`?**  
    *A:* The total count of train services calling at a specific station across the national timetable.
28. **Q: How do you avoid train-route memorization?**  
    *A:* By splitting datasets strictly by unique Train Number groups (70/15/15).
29. **Q: What happens if the live RailRadar API key is missing?**  
    *A:* The backend automatically falls back to internal timetable schedules, ensuring 100% operational uptime.
30. **Q: What is the role of `models/predictrail_preprocessor.joblib`?**  
    *A:* Stores fitted scaling and encoding parameters to guarantee zero training-serving skew.
31. **Q: How fast is backend inference?**  
    *A:* Forward-pass prediction executes in under 1 millisecond.
32. **Q: Can the model predict delays for new, un-modeled stations?**  
    *A:* Yes, because it uses topological and spatial features rather than raw station ID strings.
33. **Q: How does the system handle sudden delay surges?**  
    *A:* Auto-polls telemetry every 35s, re-computes downstream features, and updates predictions dynamically.
34. **Q: What license applies to the raw schedules?**  
    *A:* Open Data Commons / Public Domain.
35. **Q: What is your primary planned future improvement?**  
    *A:* Ingesting historical time-series telemetry streams directly into the training feature matrix.

---

# Part 48 — Comprehensive Technical Glossary

- **GBDT (Gradient Boosted Decision Trees):** Ensemble learning method constructing trees sequentially to minimize residual loss.
- **HistGradientBoostingRegressor:** Scikit-learn's histogram-binned gradient boosting regressor.
- **Data Leakage:** Accidental inclusion of future or target-derived information in training features.
- **Grouped Split:** Partitioning datasets such that entire groups (train numbers) exist exclusively in one split.
- **Permutation Importance:** Evaluating feature importance by measuring error increase upon shuffling.
- **Dynamic ETA:** Estimated Time of Arrival updated continuously based on live delay, ML predictions, and weather.
- **MAE (Mean Absolute Error):** Average magnitude of absolute errors: $\frac{1}{N}\sum |y - \hat{y}|$.
- **MedAE (Median Absolute Error):** 50th percentile absolute error, robust against outlier skew.
- **$R^2$ (Coefficient of Determination):** Proportion of variance explained by model over the mean baseline.
- **Network Density:** Total number of intersecting train paths passing through a station or corridor.
- **Delay Propagation:** Downstream transmission of delay across shared tracks and junctions.
- **GNN (Graph Neural Network):** Deep learning architecture operating directly on graph topologies.

---

# Part 49 — Final Current-State Component Summary

| Architectural Component | Verified Status in PredictRail V1 | Technical Implementation |
| :--- | :---: | :--- |
| **Historical Training Data** | ✅ **VERIFIED REAL** | 59,201 matched Indian Railways records (`predictrail_training_data.csv`). |
| **Data Preprocessing** | ✅ **VERIFIED REAL** | Scikit-Learn `ColumnTransformer` (OHE + StandardScaler). |
| **ML Algorithm** | ✅ **VERIFIED REAL** | `sklearn.ensemble.HistGradientBoostingRegressor` (200 trees, $\eta=0.08$). |
| **Feature Vector** | ✅ **VERIFIED REAL** | Exactly 13 verified safe operational & topological features. |
| **Target Variable** | ✅ **VERIFIED REAL** | Continuous non-negative arrival delay in minutes (`arrival_delay_min`). |
| **Anti-Leakage Architecture** | ✅ **VERIFIED REAL** | 4 future columns purged + Grouped Split by Train Number. |
| **Live Telemetry API** | ✅ **VERIFIED REAL** | RailRadar REST integration with local schedule fallback. |
| **Dynamic Re-Inference** | ✅ **VERIFIED REAL** | Dynamic feature re-computation and momentum blending on telemetry delta. |
| **Weather Risk Layer** | ✅ **VERIFIED REAL** | Open-Meteo REST API + rule-based delay buffer heuristics. |
| **Graph Propagation** | ✅ **VERIFIED REAL** | NetworkX 2,972-node railway graph with bottleneck scoring. |
| **Passenger Crowd Module** | ⚠️ **SYNTHETIC PROTOTYPE**| Synthetic prototype dataset for academic demonstration. |
| **Graph Neural Network (GNN)**| 🔲 **PLANNED ROADMAP** | Future research direction; not in V1 production code. |
| **Locomotive Sensor Feeds** | 🔲 **PLANNED ROADMAP** | Future enterprise feature; schema specified. |
| **Freight Conflict Engine** | 🔲 **PLANNED ROADMAP** | Future section-occupancy feature; conceptual architecture. |

---

# Part 50 — Final Truth Check: Verified Facts vs. Planned Roadmap

### Verified Facts (Executable & Proven in Code)
1. **Model:** `HistGradientBoostingRegressor` saved at `models/predictrail_delay_model.joblib` (747 KB).
2. **Dataset:** 59,201 rows across 2,733 trains and 2,972 stations with 0 missing values.
3. **Features:** Exactly 13 features (`train_type`, `station_sequence`, `distance_km`, `total_route_distance_km`, `total_route_stops`, `route_distance_progress`, `route_stop_progress`, `scheduled_halt_duration_min`, `departure_hour`, `departure_minute`, `time_of_day`, `station_network_density`, `corridor_train_density`).
4. **Metrics:** Test MAE = 39.90m, Test RMSE = 74.77m, Test MedAE = 19.06m, 65.06% within $\pm 30$m.
5. **Top Feature:** `corridor_train_density` (Importance Score: 0.4247).
6. **Live Integration:** Ingests live delay from RailRadar API and re-predicts dynamically.
7. **Destination Logic:** Arrived trains cleanly show `Status: ARRIVED` and `Arrival: 0 min`.

### Planned Roadmap (Future Enhancements)
1. Ingestion of multi-timestamp historical telemetry directly inside the ML training matrix.
2. Spatio-temporal multi-station historical weather feature extraction.
3. Time-aware locomotive maintenance and reliability tracking.
4. Live IRCTC PRS crowd occupancy feed integration.
5. Mixed freight-passenger train conflict prediction.
6. End-to-end Spatio-Temporal Graph Neural Network (GNN) model replacement.

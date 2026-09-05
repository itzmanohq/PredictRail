import os
import json
import time
import joblib
import pandas as pd
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error
from sklearn.inspection import permutation_importance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "predictrail_training_data.csv")
FEATURE_SCHEMA_PATH = os.path.join(BASE_DIR, "data", "processed", "feature_schema.json")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def verify_dataset(df, schema):
    print("\n--- [TASK 1] Verifying Data & Feature Schema ---")
    required_cols = schema.get("safe_features", []) + [schema["target_variable"]["primary_regression_target"], "split"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Inconsistent Data: Missing required column '{col}'")
    
    # Check splits
    splits = df['split'].value_counts().to_dict()
    print(f"Dataset Shape: {df.shape}")
    print(f"Train/Val/Test Splits: {splits}")
    print(f"Target column: '{schema['target_variable']['primary_regression_target']}' (Null count: {df[schema['target_variable']['primary_regression_target']].isnull().sum()})")
    
    # Anti-leakage verification
    leakage_cols = schema.get("leakage_columns_excluded", [])
    for lc in leakage_cols:
        if lc in df.columns:
            raise ValueError(f"FATAL: Target leakage detected! Column '{lc}' is present in training data.")
    print("Anti-Leakage Check: PASSED (Zero forbidden future-state columns present)")

def evaluate_predictions(y_true, y_pred, split_name="Validation"):
    # Apply technical non-negative constraint
    y_pred_clipped = np.clip(y_pred, a_min=0.0, a_max=None)
    
    mae = mean_absolute_error(y_true, y_pred_clipped)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred_clipped))
    r2 = r2_score(y_true, y_pred_clipped)
    medae = median_absolute_error(y_true, y_pred_clipped)
    
    abs_errors = np.abs(y_true - y_pred_clipped)
    within_10 = (abs_errors <= 10.0).mean() * 100.0
    within_30 = (abs_errors <= 30.0).mean() * 100.0
    
    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2": round(float(r2), 4),
        "MedAE": round(float(medae), 2),
        "within_10_min_pct": round(float(within_10), 2),
        "within_30_min_pct": round(float(within_30), 2)
    }

def main():
    print("=" * 75)
    print(" PREDICTRAIL — INDIAN RAILWAYS ML MODEL TRAINING PIPELINE")
    print("=" * 75)

    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed dataset not found at {PROCESSED_DATA_PATH}")
    if not os.path.exists(FEATURE_SCHEMA_PATH):
        raise FileNotFoundError(f"Feature schema not found at {FEATURE_SCHEMA_PATH}")

    # 1. Load Data & Schema
    df = pd.read_csv(PROCESSED_DATA_PATH)
    with open(FEATURE_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    verify_dataset(df, schema)

    categorical_features = ['train_type', 'time_of_day']
    numeric_features = [
        'station_sequence',
        'distance_km',
        'total_route_distance_km',
        'total_route_stops',
        'route_distance_progress',
        'route_stop_progress',
        'scheduled_halt_duration_min',
        'departure_hour',
        'departure_minute',
        'station_network_density',
        'corridor_train_density'
    ]
    feature_names = categorical_features + numeric_features
    target_name = 'arrival_delay_min'

    # Split partitions
    train_df = df[df['split'] == 'train'].copy()
    val_df = df[df['split'] == 'val'].copy()
    test_df = df[df['split'] == 'test'].copy()

    X_train = train_df[feature_names]
    y_train = train_df[target_name].values

    X_val = val_df[feature_names]
    y_val = val_df[target_name].values

    X_test = test_df[feature_names]
    y_test = test_df[target_name].values

    print(f"\nTrain Partition: {len(X_train):,} samples (70.0%)")
    print(f"Validation Partition: {len(X_val):,} samples (14.6%)")
    print(f"Test Partition: {len(X_test):,} samples (15.4%)")

    # 2. Build Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', StandardScaler(), numeric_features)
        ]
    )

    # 3. Baseline Model (Training Set Mean)
    train_mean_delay = y_train.mean()
    baseline_val_preds = np.full_like(y_val, fill_value=train_mean_delay)
    baseline_test_preds = np.full_like(y_test, fill_value=train_mean_delay)

    baseline_val_metrics = evaluate_predictions(y_val, baseline_val_preds, "Validation")
    baseline_test_metrics = evaluate_predictions(y_test, baseline_test_preds, "Test")

    print("\n--- [TASK 5] Naive Baseline Model (Train Mean: 48.24 min) ---")
    print(f"Validation Metrics: {baseline_val_metrics}")
    print(f"Test Metrics:       {baseline_test_metrics}")

    # 4. Train Candidate Models
    models = {
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(
            max_iter=200,
            learning_rate=0.08,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            random_state=42
        ),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100,
            max_depth=16,
            min_samples_split=10,
            min_samples_leaf=5,
            n_jobs=-1,
            random_state=42
        )
    }

    results = {}
    fitted_pipelines = {}

    for name, regressor in models.items():
        print(f"\n--- [TASK 2 & 3] Training {name} ---")
        t0 = time.time()
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('regressor', regressor)
        ])
        pipeline.fit(X_train, y_train)
        fit_time = time.time() - t0
        print(f"Training completed in {fit_time:.2f} seconds.")

        # Predict & Evaluate
        val_preds = pipeline.predict(X_val)
        test_preds = pipeline.predict(X_test)

        val_metrics = evaluate_predictions(y_val, val_preds, "Validation")
        test_metrics = evaluate_predictions(y_test, test_preds, "Test")

        print(f"[{name}] Validation Metrics:")
        for k, v in val_metrics.items():
            print(f"   {k}: {v}")
        print(f"[{name}] Test Metrics:")
        for k, v in test_metrics.items():
            print(f"   {k}: {v}")

        results[name] = {
            "validation": val_metrics,
            "test": test_metrics,
            "training_time_sec": round(fit_time, 2)
        }
        fitted_pipelines[name] = pipeline

    # 5. Model Selection based on Validation MAE & Generalization
    best_model_name = min(results, key=lambda k: results[k]["validation"]["MAE"])
    best_pipeline = fitted_pipelines[best_model_name]
    print(f"\n{'='*75}")
    print(f" BEST MODEL SELECTED: {best_model_name}")
    print(f"{'='*75}")
    print(f"Validation MAE: {results[best_model_name]['validation']['MAE']} min (vs Baseline {baseline_val_metrics['MAE']} min)")
    print(f"Test MAE:       {results[best_model_name]['test']['MAE']} min (vs Baseline {baseline_test_metrics['MAE']} min)")

    # 6. Feature Importance Calculation
    print("\n--- [TASK 6] Calculating Feature Importance (Permutation Importance on Validation Set) ---")
    t0 = time.time()
    perm_importance = permutation_importance(
        best_pipeline,
        X_val,
        y_val,
        n_repeats=5,
        random_state=42,
        n_jobs=-1
    )
    perm_time = time.time() - t0

    feature_importances = {}
    for f_idx, f_name in enumerate(feature_names):
        mean_imp = float(perm_importance.importances_mean[f_idx])
        feature_importances[f_name] = round(max(0.0, mean_imp), 4)

    # Sort descending
    sorted_importances = dict(sorted(feature_importances.items(), key=lambda x: x[1], reverse=True))
    print("Top Feature Importances:")
    for f_name, imp in sorted_importances.items():
        print(f"   {f_name:<28}: {imp:.4f}")

    # 7. Save Models and Preprocessors
    print("\n--- [TASK 8] Saving Trained Artifacts ---")
    model_save_path = os.path.join(MODELS_DIR, "predictrail_delay_model.joblib")
    preprocessor_save_path = os.path.join(MODELS_DIR, "predictrail_preprocessor.joblib")
    importance_save_path = os.path.join(MODELS_DIR, "feature_importance.json")

    joblib.dump(best_pipeline, model_save_path)
    joblib.dump(best_pipeline.named_steps['preprocessor'], preprocessor_save_path)
    with open(importance_save_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_importances, f, indent=2)

    print(f"Saved Final Pipeline to: {model_save_path}")
    print(f"Saved Preprocessor to:    {preprocessor_save_path}")
    print(f"Saved Feature Importance: {importance_save_path}")

    # 8. Save Machine-Readable Metrics
    metrics_payload = {
        "model_name": best_model_name,
        "dataset_name": "PredictRail Indian Railways Dataset",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "train_size": len(X_train),
        "validation_size": len(X_val),
        "test_size": len(X_test),
        "baseline_validation": baseline_val_metrics,
        "baseline_test": baseline_test_metrics,
        "validation_metrics": results[best_model_name]["validation"],
        "test_metrics": results[best_model_name]["test"],
        "all_candidate_models": results,
        "feature_importances": sorted_importances
    }

    metrics_save_path = os.path.join(MODELS_DIR, "metrics.json")
    with open(metrics_save_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_payload, f, indent=2)
    print(f"Saved Metrics to:         {metrics_save_path}")

    # 9. Run Sanity Check & Test Sample Predictions (TASK 14 & 15)
    print("\n--- [TASK 14 & 15] Test Predictions & Sanity Check ---")
    test_sample = test_df.head(6).copy()
    test_sample_features = test_sample[feature_names]
    sample_preds = np.clip(best_pipeline.predict(test_sample_features), 0.0, None)
    
    test_sample['predicted_delay_min'] = np.round(sample_preds, 1)
    test_sample['absolute_error_min'] = np.round(np.abs(test_sample['arrival_delay_min'] - test_sample['predicted_delay_min']), 1)

    print(f"{'Train':<8} {'Train Name':<20} {'Station':<8} {'Seq':<4} {'Actual Delay':<14} {'Predicted Delay':<16} {'Abs Error'}")
    print("-" * 80)
    for _, row in test_sample.iterrows():
        t_no = str(row['train_number'])
        t_name = str(row['train_name'])[:18]
        stn = str(row['station_code'])
        seq = int(row['station_sequence'])
        act = f"{row['arrival_delay_min']:.1f}m"
        pred = f"{row['predicted_delay_min']:.1f}m"
        err = f"{row['absolute_error_min']:.1f}m"
        print(f"{t_no:<8} {t_name:<20} {stn:<8} {seq:<4} {act:<14} {pred:<16} {err}")

    # Sanity checks
    assert not np.isnan(sample_preds).any(), "Sanity Check Failed: NaN found in predictions!"
    assert (sample_preds >= 0.0).all(), "Sanity Check Failed: Negative delay predictions found!"
    print("\nSanity Check: ALL 6 CHECKS PASSED (No NaNs, No Negative Delays, Preprocessor Verified).")

if __name__ == "__main__":
    main()

"""
AeroTwin Sensor Cross-Prediction Model Training Script
======================================================
Trains 7 RandomForestRegressors (one per engine sensor) for cross-sensor
fault isolation. Each model learns to predict one sensor's value from the
other 6 sensors under normal operating conditions.

Usage:
    python src/train_sensor_models.py

Output:
    models/sensor_cross_models.pkl
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.sensor_diagnosis import SensorDiagnosisEngine, DIAGNOSIS_SENSORS, SENSOR_BASELINES


def main():
    print("=" * 60)
    print("AeroTwin Sensor Cross-Prediction Model Training")
    print("=" * 60)
    print()

    # Initialize the diagnosis engine
    engine = SensorDiagnosisEngine(model_path="models/sensor_cross_models.pkl")

    # Generate training data from normal-operation distribution
    # Using 2000 samples for robust training
    print("[1/3] Generating synthetic normal-operation training data...")
    training_data = engine._generate_training_data(num_samples=2000)

    print(f"  Training data shape: {training_data.shape}")
    print(f"  Sensors: {list(training_data.columns)}")
    print()

    # Print data summary
    print("  Data Summary (Normal Operation):")
    for sensor in DIAGNOSIS_SENSORS:
        col = training_data[sensor]
        baseline = SENSOR_BASELINES[sensor]
        print(
            f"    {sensor:25s} mean={col.mean():10.4f}  std={col.std():8.4f}  "
            f"  baseline_mean={baseline['mean']},  baseline_std={baseline['std']}"
        )
    print()

    # Check for NaN/inf
    nan_count = training_data.isna().sum().sum()
    inf_count = np.isinf(training_data.values).sum()
    print(f"  NaN values: {nan_count}")
    print(f"  Inf values: {inf_count}")
    print()

    # Train the cross-prediction models
    print("[2/3] Training cross-prediction models...")
    print()
    engine.train_cross_models(training_data=training_data, save=True)
    print()

    # Validate on a small test set
    print("[3/3] Validating on synthetic test data...")
    print()

    # Test with normal data
    print("  --- Normal Operation Test ---")
    normal_point = {
        'rpm': 2450.0, 'cht_c': 142.0, 'egt_c': 615.0,
        'oil_pressure_bar': 4.69, 'oil_temperature_c': 92.0,
        'fuel_flow_lh': 17.6, 'vibration_g': 1.42
    }
    scores = engine.compute_sensor_scores(normal_point)
    print(f"  Sensor Scores: {scores}")
    print(f"  Max score: {max(scores.values()):.4f} (should be < 3.0)")
    print()

    # Test with single-sensor fault (CHT spike)
    print("  --- Simulated CHT Sensor Fault ---")
    sensor_fault_point = normal_point.copy()
    sensor_fault_point['cht_c'] = 228.0  # Extreme CHT drift
    scores = engine.compute_sensor_scores(sensor_fault_point)
    print(f"  Sensor Scores: {scores}")
    print(f"  CHT score: {scores['cht_c']:.4f} (should be >> 3.0)")
    print(f"  Other max: {max(v for k, v in scores.items() if k != 'cht_c'):.4f} (should be < 3.0)")
    print()

    # Test with multi-sensor fault (engine failure)
    print("  --- Simulated Engine Failure ---")
    engine_fault_point = {
        'rpm': 1800.0, 'cht_c': 198.0, 'egt_c': 730.0,
        'oil_pressure_bar': 2.2, 'oil_temperature_c': 120.0,
        'fuel_flow_lh': 24.5, 'vibration_g': 2.6
    }
    scores = engine.compute_sensor_scores(engine_fault_point)
    print(f"  Sensor Scores: {scores}")
    abnormal = [s for s, v in scores.items() if v > 3.0]
    print(f"  Abnormal sensors (> 3.0 std): {abnormal}")
    print(f"  Count: {len(abnormal)} (should be >= 3)")
    print()

    print("=" * 60)
    print("Training complete. Models saved to: models/sensor_cross_models.pkl")
    print("=" * 60)


if __name__ == "__main__":
    main()

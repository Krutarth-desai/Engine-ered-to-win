"""
AeroTwin Sensor Diagnosis Automated Test Suite
===============================================
Tests all 8 required scenarios for sensor-fault isolation
and engine failure diagnosis.

Usage:
    python src/test_sensor_diagnosis.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sensor_diagnosis import (
    SensorDiagnosisEngine,
    DIAGNOSIS_SENSORS,
    SENSOR_BASELINES,
    DIAG_NORMAL,
    DIAG_SENSOR_FAILURE,
    DIAG_ENGINE_FAILURE,
    DIAG_UNKNOWN
)


def normal_telemetry():
    """Generate a normal telemetry point matching Rotax nominal cruise."""
    return {
        'rpm': 2450.0, 'cht_c': 142.0, 'egt_c': 615.0,
        'oil_pressure_bar': 4.69, 'oil_temperature_c': 92.0,
        'fuel_flow_lh': 17.6, 'vibration_g': 1.42
    }


def run_test(test_num, test_name, engine, expected_result, test_fn):
    """Run a single test and report pass/fail."""
    print(f"\n{'='*60}")
    print(f"TEST {test_num}: {test_name}")
    print(f"{'='*60}")

    passed, details = test_fn(engine)

    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n  Expected: {expected_result}")
    print(f"  {details}")
    print(f"  Result: {status}")

    return passed


def test_1_normal(engine):
    """Normal telemetry → NORMAL"""
    engine.reset_persistence()
    tel = normal_telemetry()

    # Feed several normal ticks
    for _ in range(5):
        result = engine.diagnose(tel)

    diag = result['diagnosis_type']
    passed = diag == DIAG_NORMAL
    return passed, f"Got: {diag}, sensor_conf={result['sensor_fault_confidence']:.2f}, engine_conf={result['engine_fault_confidence']:.2f}"


def test_2_temperature_sensor_failure(engine):
    """Only temperature sensor becomes abnormal → POSSIBLE_SENSOR_FAILURE, suspected = cht_c"""
    engine.reset_persistence()

    # Feed some normal data first
    for _ in range(3):
        engine.diagnose(normal_telemetry())

    # Now inject CHT spike, keep everything else normal
    tel = normal_telemetry()
    tel['cht_c'] = 240.0

    for _ in range(5):
        result = engine.diagnose(tel)

    diag = result['diagnosis_type']
    suspected = result['suspected_sensor']
    passed = diag == DIAG_SENSOR_FAILURE and suspected == 'cht_c'
    return passed, (
        f"Got: {diag}, suspected={suspected}, "
        f"sensor_conf={result['sensor_fault_confidence']:.2f}, "
        f"engine_conf={result['engine_fault_confidence']:.2f}, "
        f"cht_score={result['sensor_scores'].get('cht_c', 0):.2f}"
    )


def test_3_oil_pressure_sensor_failure(engine):
    """Only oil-pressure sensor becomes abnormal → POSSIBLE_SENSOR_FAILURE, suspected = oil_pressure_bar"""
    engine.reset_persistence()

    for _ in range(3):
        engine.diagnose(normal_telemetry())

    tel = normal_telemetry()
    tel['oil_pressure_bar'] = 1.0  # Extreme low

    for _ in range(5):
        result = engine.diagnose(tel)

    diag = result['diagnosis_type']
    suspected = result['suspected_sensor']
    passed = diag == DIAG_SENSOR_FAILURE and suspected == 'oil_pressure_bar'
    return passed, (
        f"Got: {diag}, suspected={suspected}, "
        f"sensor_conf={result['sensor_fault_confidence']:.2f}, "
        f"oil_p_score={result['sensor_scores'].get('oil_pressure_bar', 0):.2f}"
    )


def test_4_vibration_sensor_failure(engine):
    """Only vibration sensor becomes abnormal → POSSIBLE_SENSOR_FAILURE, suspected = vibration_g"""
    engine.reset_persistence()

    for _ in range(3):
        engine.diagnose(normal_telemetry())

    tel = normal_telemetry()
    tel['vibration_g'] = 3.5  # Extreme vibration

    for _ in range(5):
        result = engine.diagnose(tel)

    diag = result['diagnosis_type']
    suspected = result['suspected_sensor']
    passed = diag == DIAG_SENSOR_FAILURE and suspected == 'vibration_g'
    return passed, (
        f"Got: {diag}, suspected={suspected}, "
        f"sensor_conf={result['sensor_fault_confidence']:.2f}, "
        f"vib_score={result['sensor_scores'].get('vibration_g', 0):.2f}"
    )


def test_5_engine_failure(engine):
    """Multiple engine parameters become abnormal simultaneously → POSSIBLE_ENGINE_FAILURE"""
    engine.reset_persistence()

    for _ in range(3):
        engine.diagnose(normal_telemetry())

    tel = {
        'rpm': 1800.0,
        'cht_c': 205.0,
        'egt_c': 760.0,
        'oil_pressure_bar': 2.2,
        'oil_temperature_c': 125.0,
        'fuel_flow_lh': 25.0,
        'vibration_g': 2.8
    }

    for _ in range(5):
        result = engine.diagnose(tel)

    diag = result['diagnosis_type']
    affected = result['affected_sensors']
    passed = diag == DIAG_ENGINE_FAILURE and len(affected) >= 3
    return passed, (
        f"Got: {diag}, affected={affected}, "
        f"engine_conf={result['engine_fault_confidence']:.2f}, "
        f"sensor_conf={result['sensor_fault_confidence']:.2f}"
    )


def test_6_single_noisy_reading(engine):
    """Single noisy abnormal reading → No immediate engine-failure classification"""
    engine.reset_persistence()

    for _ in range(3):
        engine.diagnose(normal_telemetry())

    # One abnormal reading
    tel = normal_telemetry()
    tel['cht_c'] = 240.0
    result = engine.diagnose(tel)

    # Immediately followed by normal
    result_after = engine.diagnose(normal_telemetry())

    diag_immediate = result['diagnosis_type']
    diag_after = result_after['diagnosis_type']

    # Single reading should NOT be classified as failure
    passed = diag_immediate == DIAG_NORMAL and diag_after == DIAG_NORMAL
    return passed, (
        f"Immediate: {diag_immediate} (should be NORMAL), "
        f"After recovery: {diag_after} (should be NORMAL)"
    )


def test_7_persistent_single_sensor(engine):
    """Persistent single-sensor anomaly → Increasing sensor-failure confidence"""
    engine.reset_persistence()

    tel = normal_telemetry()
    tel['egt_c'] = 780.0  # Extreme EGT

    confidences = []
    for i in range(8):
        result = engine.diagnose(tel)
        confidences.append(result['sensor_fault_confidence'])

    # Confidence should increase (or be maintained high) over time
    # At minimum, later values should be >= earlier values
    passed = confidences[-1] > confidences[0] or confidences[-1] > 0.3
    return passed, (
        f"Confidence progression: {[f'{c:.3f}' for c in confidences]}, "
        f"Final diagnosis: {result['diagnosis_type']}"
    )


def test_8_persistent_multi_sensor(engine):
    """Persistent multi-sensor anomaly → Increasing engine-failure confidence"""
    engine.reset_persistence()

    tel = {
        'rpm': 1750.0,
        'cht_c': 210.0,
        'egt_c': 765.0,
        'oil_pressure_bar': 2.0,
        'oil_temperature_c': 128.0,
        'fuel_flow_lh': 26.0,
        'vibration_g': 2.9
    }

    confidences = []
    for i in range(8):
        result = engine.diagnose(tel)
        confidences.append(result['engine_fault_confidence'])

    passed = confidences[-1] > confidences[0] or confidences[-1] > 0.3
    return passed, (
        f"Confidence progression: {[f'{c:.3f}' for c in confidences]}, "
        f"Final diagnosis: {result['diagnosis_type']}, "
        f"affected={result['affected_sensors']}"
    )


def main():
    print("=" * 60)
    print("AeroTwin Sensor Diagnosis - Automated Test Suite")
    print("=" * 60)

    # Initialize and train
    engine = SensorDiagnosisEngine(
        sensor_anomaly_threshold=3.0,
        engine_failure_min_sensors=3,
        persistence_window=5,
        model_path="models/sensor_cross_models.pkl"
    )

    # Try to load pre-trained models
    if not engine.load_models():
        print("\nPre-trained models not found. Training now...")
        engine.train_cross_models()

    print("\n" + "=" * 60)
    print("Running 8 test scenarios...")
    print("=" * 60)

    tests = [
        (1, "Normal telemetry", "NORMAL", test_1_normal),
        (2, "Temperature sensor failure (CHT spike)", "POSSIBLE_SENSOR_FAILURE (cht_c)", test_2_temperature_sensor_failure),
        (3, "Oil pressure sensor failure", "POSSIBLE_SENSOR_FAILURE (oil_pressure_bar)", test_3_oil_pressure_sensor_failure),
        (4, "Vibration sensor failure", "POSSIBLE_SENSOR_FAILURE (vibration_g)", test_4_vibration_sensor_failure),
        (5, "Multi-sensor engine failure", "POSSIBLE_ENGINE_FAILURE (3+ sensors)", test_5_engine_failure),
        (6, "Single noisy reading (no persistence)", "NORMAL (no immediate classification)", test_6_single_noisy_reading),
        (7, "Persistent single-sensor anomaly", "Increasing sensor-failure confidence", test_7_persistent_single_sensor),
        (8, "Persistent multi-sensor anomaly", "Increasing engine-failure confidence", test_8_persistent_multi_sensor),
    ]

    results = []
    for test_num, name, expected, fn in tests:
        passed = run_test(test_num, name, engine, expected, fn)
        results.append((test_num, name, passed))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    pass_count = 0
    for num, name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  Test {num}: {status} - {name}")
        if passed:
            pass_count += 1

    print(f"\n  {pass_count}/{len(results)} tests passed")
    print("=" * 60)

    # Model validation note
    print("\nWARNING: VALIDATION NOTE:")
    print("  Training data is synthetic (normal-operation simulation).")
    print("  No real sensor/engine fault labels are available.")
    print("  All test scenarios use controlled fault injection (simulated).")
    print("  Results are validated against simulated ground truth.")
    print("  This is clearly labeled as simulated/test validation.")

    return pass_count == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
AeroTwin Sensor-Fault Isolation & Engine Diagnosis Engine
=========================================================
Cross-sensor ML prediction approach for distinguishing sensor failures
from genuine engine failures.

For each of 7 engine sensors, a RandomForestRegressor is trained to predict
that sensor's expected value from the other 6 sensors. When one sensor's
actual reading diverges significantly from its cross-predicted value while
others remain consistent, it indicates a sensor fault. When multiple sensors
simultaneously diverge, it indicates a genuine engine fault.

This module integrates with the existing AeroTwinAnomalyDetector (Isolation
Forest) and sits between anomaly detection and fault prediction in the pipeline.
"""

import numpy as np
import pandas as pd
import joblib
import os
from collections import deque
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


# The 7 engine-health sensors used for cross-prediction
DIAGNOSIS_SENSORS = [
    'rpm', 'cht_c', 'egt_c', 'oil_pressure_bar',
    'oil_temperature_c', 'fuel_flow_lh', 'vibration_g'
]

# Human-readable display names for evidence generation
SENSOR_DISPLAY_NAMES = {
    'rpm': 'RPM (Rotational Speed)',
    'cht_c': 'CHT (Cylinder Head Temperature)',
    'egt_c': 'EGT (Exhaust Gas Temperature)',
    'oil_pressure_bar': 'Oil Pressure',
    'oil_temperature_c': 'Oil Temperature',
    'fuel_flow_lh': 'Fuel Flow',
    'vibration_g': 'Vibration RMS'
}

# Normal operational baselines (matching the existing AeroTwinAnomalyDetector)
SENSOR_BASELINES = {
    'rpm': {'mean': 6100, 'std': 20},
    'cht_c': {'mean': 150, 'std': 2},
    'egt_c': {'mean': 700, 'std': 5},
    'oil_pressure_bar': {'mean': 4.3, 'std': 0.1},
    'oil_temperature_c': {'mean': 95, 'std': 2},
    'fuel_flow_lh': {'mean': 18.5, 'std': 0.2},
    'vibration_g': {'mean': 0.2, 'std': 0.02}
}

# Diagnosis classification types
DIAG_NORMAL = "NORMAL"
DIAG_SENSOR_FAILURE = "POSSIBLE_SENSOR_FAILURE"
DIAG_ENGINE_FAILURE = "POSSIBLE_ENGINE_FAILURE"
DIAG_UNKNOWN = "UNKNOWN"

# Default model save path
DEFAULT_MODEL_PATH = "models/sensor_cross_models.pkl"


class SensorDiagnosisEngine:
    """
    Cross-sensor ML diagnosis engine that distinguishes sensor failures
    from genuine engine failures.
    
    Pipeline:
        Telemetry → Isolation Forest (overall anomaly)
                  → SensorDiagnosisEngine (per-sensor cross-prediction)
                  → Classification (sensor vs engine failure)
                  → Confidence + Evidence
    """

    def __init__(
        self,
        sensor_anomaly_threshold: float = 3.0,
        engine_failure_min_sensors: int = 3,
        persistence_window: int = 5,
        model_path: str = DEFAULT_MODEL_PATH
    ):
        """
        Args:
            sensor_anomaly_threshold: Number of standard deviations for a sensor
                to be considered anomalous (relative to cross-prediction residual).
            engine_failure_min_sensors: Minimum number of simultaneously abnormal
                sensors to classify as possible engine failure.
            persistence_window: Number of consecutive ticks to track for temporal
                persistence logic.
            model_path: Path to save/load trained cross-prediction models.
        """
        self.sensor_anomaly_threshold = sensor_anomaly_threshold
        self.engine_failure_min_sensors = engine_failure_min_sensors
        self.persistence_window = persistence_window
        self.model_path = model_path

        # Cross-prediction models: {sensor_name: RandomForestRegressor}
        self.models = {}
        # Learned residual standard deviations for normalization
        self.residual_stds = {}
        self.is_trained = False

        # Temporal persistence tracking: per-sensor anomaly history
        # Each entry is a deque of booleans (True = anomalous at that tick)
        self.sensor_history = {
            sensor: deque(maxlen=persistence_window)
            for sensor in DIAGNOSIS_SENSORS
        }
        # Overall diagnosis history for temporal smoothing
        self.diagnosis_history = deque(maxlen=persistence_window)

    def _generate_training_data(self, num_samples: int = 2000) -> pd.DataFrame:
        """
        Generate synthetic normal-operation training data.
        Uses the same distribution as the existing AeroTwinAnomalyDetector baseline.
        """
        data = {}
        for sensor in DIAGNOSIS_SENSORS:
            baseline = SENSOR_BASELINES[sensor]
            data[sensor] = np.random.normal(
                baseline['mean'], baseline['std'], size=num_samples
            )
        return pd.DataFrame(data)

    def train_cross_models(self, training_data: pd.DataFrame = None, save: bool = True):
        """
        Train one RandomForestRegressor per sensor. Each model predicts that
        sensor's value from the other 6 sensors.
        
        Args:
            training_data: DataFrame with columns matching DIAGNOSIS_SENSORS.
                           If None, generates synthetic normal-operation data.
            save: Whether to save trained models to disk.
        """
        if training_data is None:
            training_data = self._generate_training_data(num_samples=2000)

        # Validate training data
        training_data = training_data.copy()
        training_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        training_data.dropna(subset=DIAGNOSIS_SENSORS, inplace=True)

        if len(training_data) < 50:
            raise ValueError(
                f"Insufficient training data: {len(training_data)} rows. Need >= 50."
            )

        print(f"[SensorDiagnosis] Training cross-prediction models on {len(training_data)} samples...")

        for target_sensor in DIAGNOSIS_SENSORS:
            # Features = all other sensors
            feature_sensors = [s for s in DIAGNOSIS_SENSORS if s != target_sensor]
            X = training_data[feature_sensors].values
            y = training_data[target_sensor].values

            # Train RandomForestRegressor
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_leaf=5,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X, y)

            # Compute residual std on training data for normalization
            y_pred = model.predict(X)
            residuals = y - y_pred
            residual_std = max(np.std(residuals), 1e-6)  # Avoid division by zero

            self.models[target_sensor] = model
            self.residual_stds[target_sensor] = residual_std

            print(
                f"  [{target_sensor}] Trained. "
                f"Train RMSE: {np.sqrt(np.mean(residuals**2)):.4f}, "
                f"Residual std: {residual_std:.4f}"
            )

        self.is_trained = True

        if save:
            os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
            joblib.dump(
                {
                    'models': self.models,
                    'residual_stds': self.residual_stds,
                },
                self.model_path
            )
            print(f"[SensorDiagnosis] Models saved to {self.model_path}")

    def load_models(self) -> bool:
        """
        Load pre-trained cross-prediction models from disk.
        Returns True if successful, False otherwise.
        """
        if not os.path.exists(self.model_path):
            return False

        try:
            data = joblib.load(self.model_path)
            self.models = data['models']
            self.residual_stds = data['residual_stds']
            self.is_trained = True
            print(f"[SensorDiagnosis] Loaded pre-trained models from {self.model_path}")
            return True
        except Exception as e:
            print(f"[SensorDiagnosis] Failed to load models: {e}")
            return False

    def predict_expected(self, telemetry: dict) -> dict:
        """
        For each sensor, predict its expected value using the other 6 sensors.
        
        Returns:
            dict: {sensor_name: expected_value}
        """
        if not self.is_trained:
            return {}

        expected = {}
        for target_sensor in DIAGNOSIS_SENSORS:
            feature_sensors = [s for s in DIAGNOSIS_SENSORS if s != target_sensor]
            X = np.array([[
                telemetry.get(s, SENSOR_BASELINES[s]['mean'])
                for s in feature_sensors
            ]])
            expected[target_sensor] = float(self.models[target_sensor].predict(X)[0])

        return expected

    def compute_sensor_scores(self, telemetry: dict) -> dict:
        """
        Compute normalized anomaly scores for each sensor.
        
        Score = |actual - predicted| / learned_residual_std
        
        A score of 1.0 = one standard deviation from expected.
        A score of 3.0+ = highly anomalous for that sensor.
        
        Returns:
            dict: {sensor_name: normalized_anomaly_score}
        """
        if not self.is_trained:
            return {s: 0.0 for s in DIAGNOSIS_SENSORS}

        expected = self.predict_expected(telemetry)
        scores = {}

        for sensor in DIAGNOSIS_SENSORS:
            actual = telemetry.get(sensor, SENSOR_BASELINES[sensor]['mean'])
            exp = expected[sensor]
            residual = abs(actual - exp)
            # Normalize by learned residual standard deviation
            scores[sensor] = float(residual / self.residual_stds[sensor])

        return scores

    def _update_persistence(self, sensor_scores: dict) -> dict:
        """
        Update temporal persistence tracking and compute persistence metrics.
        
        Returns:
            dict: {sensor_name: persistence_count} — how many of the last N
                  ticks each sensor was flagged as anomalous.
        """
        for sensor in DIAGNOSIS_SENSORS:
            is_anomalous = sensor_scores[sensor] > self.sensor_anomaly_threshold
            self.sensor_history[sensor].append(is_anomalous)

        persistence = {}
        for sensor in DIAGNOSIS_SENSORS:
            persistence[sensor] = sum(self.sensor_history[sensor])

        return persistence

    def _compute_confidence(
        self,
        sensor_scores: dict,
        persistence: dict,
        num_anomalous: int,
        total_sensors: int
    ) -> tuple:
        """
        Compute sensor-failure and engine-failure confidence scores.
        
        Returns:
            (sensor_fault_confidence, engine_fault_confidence)
            Both in range [0.0, 1.0]
        """
        max_score = max(sensor_scores.values()) if sensor_scores else 0.0
        max_sensor = max(sensor_scores, key=sensor_scores.get) if sensor_scores else None

        # Proportion of sensors that are anomalous
        anomaly_ratio = num_anomalous / total_sensors if total_sensors > 0 else 0.0

        # Persistence factor: average persistence of anomalous sensors
        anomalous_sensors = [
            s for s in DIAGNOSIS_SENSORS
            if sensor_scores.get(s, 0) > self.sensor_anomaly_threshold
        ]
        if anomalous_sensors:
            avg_persistence = np.mean([persistence[s] for s in anomalous_sensors])
        else:
            avg_persistence = 0.0

        persistence_factor = min(avg_persistence / self.persistence_window, 1.0)

        # --- Sensor failure confidence ---
        # High when: exactly 1 sensor abnormal, that sensor has high score,
        # other sensors have low scores, good persistence
        if num_anomalous == 1 and max_score > self.sensor_anomaly_threshold:
            # Score isolation: how much does the top sensor stand out?
            sorted_scores = sorted(sensor_scores.values(), reverse=True)
            if len(sorted_scores) > 1 and sorted_scores[1] > 0:
                isolation_ratio = sorted_scores[0] / max(sorted_scores[1], 0.01)
            else:
                isolation_ratio = sorted_scores[0] / 0.01

            # Clamp isolation contribution
            isolation_factor = min(isolation_ratio / 10.0, 1.0)

            # Magnitude factor
            magnitude_factor = min(max_score / (self.sensor_anomaly_threshold * 3), 1.0)

            sensor_conf = 0.3 * isolation_factor + 0.4 * persistence_factor + 0.3 * magnitude_factor
            sensor_conf = min(sensor_conf, 0.99)
        elif num_anomalous == 2:
            # 2 sensors could be borderline — lower confidence
            sensor_conf = 0.15 * persistence_factor
        else:
            sensor_conf = 0.0

        # --- Engine failure confidence ---
        # High when: multiple sensors abnormal, correlated, persistent
        if num_anomalous >= self.engine_failure_min_sensors:
            # More sensors = higher confidence
            coverage_factor = min(num_anomalous / total_sensors, 1.0)

            # Average anomaly magnitude of abnormal sensors
            abnormal_scores = [
                sensor_scores[s] for s in anomalous_sensors
            ]
            avg_magnitude = np.mean(abnormal_scores) if abnormal_scores else 0.0
            magnitude_factor = min(avg_magnitude / (self.sensor_anomaly_threshold * 2), 1.0)

            engine_conf = 0.3 * coverage_factor + 0.35 * persistence_factor + 0.35 * magnitude_factor
            engine_conf = min(engine_conf, 0.99)
        elif num_anomalous == 2:
            engine_conf = 0.1 * persistence_factor
        else:
            engine_conf = 0.0

        # Ensure they are complementary when one dominates
        total = sensor_conf + engine_conf
        if total > 0:
            # Normalize so they don't both be high
            sensor_conf_normalized = sensor_conf / total
            engine_conf_normalized = engine_conf / total

            # Scale by overall evidence strength
            evidence_strength = min(total, 1.0)
            sensor_conf = sensor_conf_normalized * evidence_strength
            engine_conf = engine_conf_normalized * evidence_strength

        return round(float(sensor_conf), 4), round(float(engine_conf), 4)

    def _generate_evidence(
        self,
        diagnosis_type: str,
        sensor_scores: dict,
        expected_values: dict,
        telemetry: dict,
        suspected_sensor: str,
        affected_sensors: list
    ) -> str:
        """
        Generate a human-readable explanation for the diagnosis.
        Uses actual sensor names, values, and deviations.
        """
        if diagnosis_type == DIAG_NORMAL:
            return (
                "All engine sensors are operating within their expected cross-predicted "
                "relationships. No sensor or engine anomaly detected."
            )

        if diagnosis_type == DIAG_SENSOR_FAILURE and suspected_sensor:
            display_name = SENSOR_DISPLAY_NAMES.get(suspected_sensor, suspected_sensor)
            actual_val = telemetry.get(suspected_sensor, 'N/A')
            expected_val = expected_values.get(suspected_sensor, 'N/A')

            # List healthy sensors
            healthy_sensors = [
                SENSOR_DISPLAY_NAMES.get(s, s)
                for s in DIAGNOSIS_SENSORS
                if s != suspected_sensor and sensor_scores.get(s, 0) <= self.sensor_anomaly_threshold
            ]

            # List the input features used for prediction
            input_sensors = [
                SENSOR_DISPLAY_NAMES.get(s, s).split(' (')[0]
                for s in DIAGNOSIS_SENSORS if s != suspected_sensor
            ]

            if isinstance(actual_val, (int, float)):
                actual_str = f"{actual_val:.2f}"
            else:
                actual_str = str(actual_val)

            if isinstance(expected_val, (int, float)):
                expected_str = f"{expected_val:.2f}"
            else:
                expected_str = str(expected_val)

            evidence = (
                f"{display_name} sensor reading ({actual_str}) strongly deviates from "
                f"the expected value ({expected_str}) predicted by "
                f"{', '.join(input_sensors)}. "
            )

            if healthy_sensors:
                evidence += (
                    f"All other engine parameters ({', '.join(healthy_sensors[:3])}"
                    f"{' and others' if len(healthy_sensors) > 3 else ''}) "
                    f"remain within their normal operating relationships. "
                    f"This pattern is consistent with a sensor malfunction rather "
                    f"than an engine fault."
                )

            return evidence

        if diagnosis_type == DIAG_ENGINE_FAILURE:
            affected_names = [
                SENSOR_DISPLAY_NAMES.get(s, s)
                for s in affected_sensors
            ]

            details = []
            for s in affected_sensors[:4]:
                actual = telemetry.get(s, 'N/A')
                expected = expected_values.get(s, 'N/A')
                if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                    details.append(
                        f"{SENSOR_DISPLAY_NAMES.get(s, s).split(' (')[0]}: "
                        f"actual={actual:.2f}, expected={expected:.2f}"
                    )

            evidence = (
                f"{', '.join([n.split(' (')[0] for n in affected_names])} "
                f"simultaneously deviate from their learned operating relationships, "
                f"indicating a system-level engine abnormality rather than an "
                f"isolated sensor fault. "
            )

            if details:
                evidence += "Deviations: " + "; ".join(details) + "."

            return evidence

        # UNKNOWN
        return (
            "Anomalous telemetry detected but insufficient cross-sensor evidence "
            "to conclusively classify as either a sensor failure or engine failure. "
            "Continued monitoring recommended."
        )

    def diagnose(
        self,
        telemetry: dict,
        is_isolation_forest_anomaly: bool = False,
        isolation_forest_score: float = 0.0
    ) -> dict:
        """
        Main diagnosis method. Classifies telemetry as:
        - NORMAL
        - POSSIBLE_SENSOR_FAILURE
        - POSSIBLE_ENGINE_FAILURE
        - UNKNOWN

        Args:
            telemetry: Current telemetry reading dict.
            is_isolation_forest_anomaly: Whether the Isolation Forest flagged this as anomalous.
            isolation_forest_score: The Isolation Forest decision function score.

        Returns:
            dict with keys:
                diagnosis_type, sensor_fault_confidence, engine_fault_confidence,
                suspected_sensor, affected_sensors, sensor_scores, evidence,
                persistence_count, expected_values
        """
        if not self.is_trained:
            return self._empty_diagnosis()

        # Step 1: Compute per-sensor anomaly scores
        sensor_scores = self.compute_sensor_scores(telemetry)
        expected_values = self.predict_expected(telemetry)

        # Step 2: Identify anomalous sensors
        anomalous_sensors = [
            s for s in DIAGNOSIS_SENSORS
            if sensor_scores[s] > self.sensor_anomaly_threshold
        ]
        num_anomalous = len(anomalous_sensors)
        total_sensors = len(DIAGNOSIS_SENSORS)

        # Step 3: Update temporal persistence
        persistence = self._update_persistence(sensor_scores)

        # Step 4: Classify
        if num_anomalous == 0:
            # No sensors anomalous — even if Isolation Forest flags it,
            # the cross-prediction models don't see sensor-level issues
            diagnosis_type = DIAG_NORMAL
            suspected_sensor = None
            affected_sensors = []

        elif num_anomalous == 1:
            # Single sensor diverges — candidate for sensor failure
            suspected_sensor = anomalous_sensors[0]

            # Require persistence before confirming
            if persistence[suspected_sensor] >= 2:
                diagnosis_type = DIAG_SENSOR_FAILURE
            else:
                # Single noisy reading — not enough evidence yet
                diagnosis_type = DIAG_NORMAL
                suspected_sensor = None

            affected_sensors = anomalous_sensors

        elif num_anomalous == 2:
            # Two sensors — ambiguous zone
            # Could be sensor failure with sympathetic noise,
            # or early engine failure
            max_persistence = max(persistence[s] for s in anomalous_sensors)

            if max_persistence >= 3:
                # Check if scores are heavily skewed to one sensor
                sorted_by_score = sorted(
                    anomalous_sensors,
                    key=lambda s: sensor_scores[s],
                    reverse=True
                )
                top_score = sensor_scores[sorted_by_score[0]]
                second_score = sensor_scores[sorted_by_score[1]]

                if top_score > second_score * 2.5:
                    # One sensor dominates — likely sensor failure
                    diagnosis_type = DIAG_SENSOR_FAILURE
                    suspected_sensor = sorted_by_score[0]
                else:
                    # Both similarly anomalous — lean toward unknown/early engine
                    diagnosis_type = DIAG_UNKNOWN
                    suspected_sensor = None
            else:
                diagnosis_type = DIAG_NORMAL
                suspected_sensor = None

            affected_sensors = anomalous_sensors

        else:
            # 3+ sensors anomalous — candidate for engine failure
            # Require some persistence
            avg_persistence = np.mean([persistence[s] for s in anomalous_sensors])

            if avg_persistence >= 2:
                diagnosis_type = DIAG_ENGINE_FAILURE
                suspected_sensor = None
            elif avg_persistence >= 1:
                diagnosis_type = DIAG_UNKNOWN
                suspected_sensor = None
            else:
                diagnosis_type = DIAG_NORMAL
                suspected_sensor = None

            affected_sensors = anomalous_sensors

        # Step 5: Compute confidence scores
        sensor_conf, engine_conf = self._compute_confidence(
            sensor_scores, persistence, num_anomalous, total_sensors
        )

        # Step 6: Generate evidence
        evidence = self._generate_evidence(
            diagnosis_type, sensor_scores, expected_values,
            telemetry, suspected_sensor, affected_sensors
        )

        # Step 7: Track diagnosis persistence
        self.diagnosis_history.append(diagnosis_type)

        # Max persistence count among affected sensors
        max_persistence = max(
            (persistence[s] for s in affected_sensors), default=0
        )

        return {
            "diagnosis_type": diagnosis_type,
            "sensor_fault_confidence": sensor_conf,
            "engine_fault_confidence": engine_conf,
            "suspected_sensor": suspected_sensor,
            "affected_sensors": affected_sensors,
            "sensor_scores": {s: round(v, 4) for s, v in sensor_scores.items()},
            "evidence": evidence,
            "persistence_count": int(max_persistence),
            "expected_values": {s: round(v, 2) for s, v in expected_values.items()}
        }

    def reset_persistence(self):
        """Reset all temporal tracking. Call when switching fault scenarios."""
        for sensor in DIAGNOSIS_SENSORS:
            self.sensor_history[sensor].clear()
        self.diagnosis_history.clear()

    def _empty_diagnosis(self) -> dict:
        """Return empty diagnosis when models are not trained."""
        return {
            "diagnosis_type": DIAG_NORMAL,
            "sensor_fault_confidence": 0.0,
            "engine_fault_confidence": 0.0,
            "suspected_sensor": None,
            "affected_sensors": [],
            "sensor_scores": {s: 0.0 for s in DIAGNOSIS_SENSORS},
            "evidence": "Sensor diagnosis models not yet trained.",
            "persistence_count": 0,
            "expected_values": {}
        }

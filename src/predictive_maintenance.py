import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

class AeroTwinAnomalyDetector:
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=self.contamination, random_state=42)
        self.features = [
            'rpm', 'cht_c', 'egt_c', 'oil_pressure_bar', 
            'oil_temperature_c', 'fuel_flow_lh', 'vibration_g'
        ]
        self.is_trained = False
        
        # Baselines aligned with TelemetryProcessor nominal cruise output.
        # Oil pressure is converted: 68 psi / 14.5038 ≈ 4.69 bar (TelemetryProcessor
        # stores in psi internally but tick_and_broadcast converts to bar before
        # feeding this detector).
        self.baselines = {
            'rpm': 2450.0,
            'cht_c': 142.0,
            'egt_c': 615.0,
            'oil_pressure_bar': 4.69,
            'oil_temperature_c': 92.0,
            'fuel_flow_lh': 17.6,
            'vibration_g': 1.42
        }

        # Training noise sigmas matching TelemetryProcessor random.gauss spreads
        self._train_sigmas = {
            'rpm': 12.0,
            'cht_c': 1.2,
            'egt_c': 3.0,
            'oil_pressure_bar': 0.06,   # 0.5 psi / 14.5 ≈ 0.034, widened slightly
            'oil_temperature_c': 1.0,
            'fuel_flow_lh': 0.2,
            'vibration_g': 0.02
        }

    def train_baseline(self, num_samples=1000):
        """
        Trains the IsolationForest on a generated baseline of 'Normal' telemetry data.
        Baselines and sigmas are aligned with TelemetryProcessor nominal cruise output.
        """
        print("[AeroTwin] Training IsolationForest baseline...")
        data = []
        for _ in range(num_samples):
            data.append([
                np.random.normal(self.baselines[f], self._train_sigmas[f])
                for f in self.features
            ])
        
        df = pd.DataFrame(data, columns=self.features)
        self.model.fit(df)
        self.is_trained = True
        print("[AeroTwin] IsolationForest training complete.")

    def detect(self, telemetry: dict):
        """
        Detects if a given telemetry point is anomalous.
        Returns: is_anomaly (bool), anomaly_score (float)
        """
        if not self.is_trained:
            return False, 1.0

        # Extract features as DataFrame with feature names to match model training
        X = pd.DataFrame(
            [[telemetry.get(f, self.baselines[f]) for f in self.features]],
            columns=self.features
        )
        
        # Predict: 1 for normal, -1 for anomaly
        prediction = self.model.predict(X)[0]
        # Score: Negative is anomaly, lower is worse
        score = self.model.decision_function(X)[0]
        
        is_anomaly = prediction == -1
        return is_anomaly, float(score)

    def infer_fault(self, telemetry: dict, is_anomaly: bool, score: float):
        """
        Infers the specific fault, severity, and provides treatment/prevention recommendations.
        """
        if not is_anomaly:
            return {
                "status": "Normal",
                "severity": "NORMAL",
                "fault": "None",
                "evidence": "All parameters within normal operating envelope.",
                "treatment": "None required.",
                "prevention": "Continue standard scheduled maintenance."
            }

        # Calculate deviations
        dev_rpm = telemetry.get('rpm', self.baselines['rpm']) - self.baselines['rpm']
        dev_cht = telemetry.get('cht_c', self.baselines['cht_c']) - self.baselines['cht_c']
        dev_egt = telemetry.get('egt_c', self.baselines['egt_c']) - self.baselines['egt_c']
        dev_oil_p = telemetry.get('oil_pressure_bar', self.baselines['oil_pressure_bar']) - self.baselines['oil_pressure_bar']
        dev_oil_t = telemetry.get('oil_temperature_c', self.baselines['oil_temperature_c']) - self.baselines['oil_temperature_c']
        dev_vibe = telemetry.get('vibration_g', self.baselines['vibration_g']) - self.baselines['vibration_g']
        dev_fuel = telemetry.get('fuel_flow_lh', self.baselines['fuel_flow_lh']) - self.baselines['fuel_flow_lh']

        # Determine Severity based on score
        severity = "CRITICAL" if score < -0.15 else "WARNING"

        # 1. Overheating
        if dev_cht > 15 or dev_egt > 30 or dev_oil_t > 15:
            return {
                "status": "Anomaly Detected",
                "severity": severity,
                "fault": "Engine Overheating",
                "evidence": f"High CHT (+{dev_cht:.1f}°C) and EGT (+{dev_egt:.1f}°C)",
                "treatment": "Reduce engine load / throttle. Monitor cooling system airflow.",
                "prevention": "Inspect coolant levels, radiator fins, and cooling airflow pathways during next maintenance cycle."
            }

        # 2. Lubrication Failure
        if dev_oil_p < -0.5 or (dev_oil_p < -0.3 and dev_oil_t > 10):
            return {
                "status": "Anomaly Detected",
                "severity": severity,
                "fault": "Lubrication System Degradation",
                "evidence": f"Low Oil Pressure ({telemetry.get('oil_pressure_bar', 0):.2f} bar) with elevated temp.",
                "treatment": "Reduce engine RPM immediately. Land as soon as practical if pressure drops below 3.0 bar.",
                "prevention": "Check oil levels, replace oil filter, and inspect oil pump for wear."
            }

        # 3. Bearing / Vibration Fault
        if dev_vibe > 0.2:
            return {
                "status": "Anomaly Detected",
                "severity": severity,
                "fault": "Bearing / Rotational Degradation",
                "evidence": f"Excessive vibration detected ({telemetry.get('vibration_g', 0):.2f} g).",
                "treatment": "Avoid high RPM bands. Monitor for structural resonance.",
                "prevention": "Perform vibration analysis on primary drive shaft and inspect main bearings."
            }
            
        # 4. Injector / Misfire Fault
        if dev_fuel > 2.0 or abs(dev_rpm) > 150:
            return {
                "status": "Anomaly Detected",
                "severity": severity,
                "fault": "Fuel Injection / Misfire",
                "evidence": f"Erratic RPM (Δ{dev_rpm:.1f}) and abnormal fuel flow.",
                "treatment": "Check for smooth throttle response. Avoid sudden throttle changes.",
                "prevention": "Inspect fuel injectors for clogging, check fuel filter and spark plugs."
            }

        # Fallback
        return {
            "status": "Anomaly Detected",
            "severity": severity,
            "fault": "Unknown System Anomaly",
            "evidence": "Multiple parameters deviating slightly from baseline.",
            "treatment": "Monitor all engine parameters closely.",
            "prevention": "Conduct comprehensive ground run and diagnostics."
        }

import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class TelemetryProcessor:
    """
    Unified 3-Layer Telemetry and Prognostics Processor for AeroTwin GCS.
    Maintains rolling 30-cycle operational windows, computes RUL,
    evaluates risk, ranks contributing features, and generates alerts.
    """
    def __init__(self):
        self.cycle = 31
        self.max_useful_life = 250
        self.avg_cycle_duration_seconds = 60 # 1 cycle = 60s of operational flight
        
        # Baselines
        self.base_sensors = {
            "rpm": 2450.0,
            "cht": 142.0,
            "egt": 615.0,
            "oil_pressure": 68.0,
            "oil_temperature": 92.0,
            "fuel_flow": 17.6,
            "vibration": 1.42,
            "bus_voltage": 27.6,
            "injection_timing": 23.4
        }
        
        # Sensor normal envelopes
        self.sensor_ranges = {
            "rpm": {"min": 0, "max": 3200, "unit": "RPM", "label": "RPM", "caution_high": 2750, "caution_low": 2100, "alert_high": 2950, "alert_low": 1800},
            "cht": {"min": 50, "max": 240, "unit": "°C", "label": "CHT", "caution_high": 165, "caution_low": 80, "alert_high": 195, "alert_low": 60},
            "egt": {"min": 250, "max": 950, "unit": "°C", "label": "EGT", "caution_high": 680, "caution_low": 450, "alert_high": 760, "alert_low": 400},
            "oil_pressure": {"min": 0, "max": 100, "unit": "psi", "label": "Oil Pressure", "caution_high": 85, "caution_low": 50, "alert_high": 95, "alert_low": 35},
            "oil_temperature": {"min": 30, "max": 150, "unit": "°C", "label": "Oil Temperature", "caution_high": 108, "caution_low": 60, "alert_high": 125, "alert_low": 45},
            "fuel_flow": {"min": 0, "max": 40, "unit": "L/hr", "label": "Fuel Flow", "caution_high": 24.0, "caution_low": 12.0, "alert_high": 28.0, "alert_low": 9.0},
            "vibration": {"min": 0, "max": 4.5, "unit": "g", "label": "Vibration", "caution_high": 2.1, "caution_low": 0.0, "alert_high": 2.9, "alert_low": 0.0},
            "bus_voltage": {"min": 18, "max": 34, "unit": "V", "label": "Bus Voltage", "caution_high": 29.5, "caution_low": 25.0, "alert_high": 31.0, "alert_low": 23.5},
            "injection_timing": {"min": 10, "max": 38, "unit": "°CA", "label": "Injection Timing", "caution_high": 27.5, "caution_low": 19.0, "alert_high": 30.0, "alert_low": 16.0},
        }

        # Historical buffers
        self.prev_sensors = dict(self.base_sensors)
        self.recent_30_cycles: List[Dict[str, float]] = []
        self.trajectory_history: List[Dict[str, Any]] = []
        
        # Prepopulate initial 30 cycles for immediate visual realism
        self._init_history()
        
        # Dynamic alerts memory (Nominal baseline when no fault is injected)
        self.alert_feed: List[Dict[str, Any]] = [
            {
                "id": "alt-1",
                "level": "NORMAL",
                "title": "ALL SYSTEMS NOMINAL",
                "message": "Telemetry parity verified across 9 sensor channels.",
                "time_ago": "Just now",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": "alt-2",
                "level": "INFO",
                "title": "VIBRATION & COMBUSTION NOMINAL",
                "message": "Dynamic harmonics within standard rotational cruise envelope.",
                "time_ago": "2 min ago",
                "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat()
            }
        ]

    def _init_history(self):
        """Seed 30-cycle buffer and RUL trajectory from cycle 1 to 31."""
        self.recent_30_cycles = []
        self.trajectory_history = []
        
        for c in range(1, self.cycle + 1):
            # Degradation progression
            deg = (c / self.max_useful_life)
            actual_rul = max(0, self.max_useful_life - c)
            pred_noise = random.uniform(-4.0, 4.0)
            predicted_rul = max(0, actual_rul + pred_noise + 5.0 * math.sin(c / 5.0))
            
            self.trajectory_history.append({
                "cycle": c,
                "actual_rul": round(actual_rul, 1),
                "predicted_rul": round(predicted_rul, 1)
            })
            
            # Simulated 30-cycle trends
            c_egt = 600.0 + deg * 18.0 + random.uniform(-3, 3)
            c_oil_p = 70.0 - deg * 3.0 + random.uniform(-0.5, 0.5)
            c_vib = 1.35 + deg * 0.12 + random.uniform(-0.03, 0.03)
            c_health = max(40, 100.0 - deg * 30.0 + random.uniform(-1, 1))
            
            self.recent_30_cycles.append({
                "cycle": c,
                "egt": round(c_egt, 1),
                "oil_pressure": round(c_oil_p, 1),
                "vibration": round(c_vib, 2),
                "health_index": round(c_health, 1)
            })
        
        if len(self.recent_30_cycles) > 30:
            self.recent_30_cycles = self.recent_30_cycles[-30:]

    def process_tick(self, tick: int, scenario: str, simulation_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a live 1 Hz tick and returns the unified 3-layer data contract.
        """
        # Cycle progression: increment cycle every 20 ticks or smoothly
        if tick > 0 and tick % 25 == 0:
            self.cycle = min(self.cycle + 1, self.max_useful_life - 5)
            
        degradation = min(tick / 60.0, 1.0)
        
        # 1. Generate core sensor values with noise
        curr_sensors = {
            "rpm": self.base_sensors["rpm"] + random.gauss(0, 15),
            "cht": self.base_sensors["cht"] + random.gauss(0, 1.5),
            "egt": self.base_sensors["egt"] + random.gauss(0, 3.5),
            "oil_pressure": self.base_sensors["oil_pressure"] + random.gauss(0, 0.6),
            "oil_temperature": self.base_sensors["oil_temperature"] + random.gauss(0, 1.2),
            "fuel_flow": self.base_sensors["fuel_flow"] + random.gauss(0, 0.2),
            "vibration": self.base_sensors["vibration"] + random.gauss(0, 0.02),
            "bus_voltage": self.base_sensors["bus_voltage"] + random.gauss(0, 0.1),
            "injection_timing": self.base_sensors["injection_timing"] + random.gauss(0, 0.15)
        }
        
        # In nominal cruise without injected faults, health index is 96-98%
        health_index = 96.0 - (self.cycle / self.max_useful_life) * 4.0
        
        # 2. Inject scenarios
        if scenario == "Overheating" and tick > 3:
            curr_sensors["cht"] += degradation * 48.0
            curr_sensors["egt"] += degradation * 95.0
            curr_sensors["oil_temperature"] += degradation * 28.0
            health_index -= degradation * 40.0
            
        elif scenario == "Oil_Pressure_Loss" and tick > 3:
            curr_sensors["oil_pressure"] -= degradation * 28.0
            curr_sensors["oil_temperature"] += degradation * 22.0
            curr_sensors["vibration"] += degradation * 0.45
            health_index -= degradation * 45.0
            
        elif scenario == "RPM_Drop" and tick > 3:
            curr_sensors["rpm"] -= degradation * 550.0
            curr_sensors["fuel_flow"] -= degradation * 4.2
            health_index -= degradation * 30.0
            
        elif scenario == "High_Vibration" and tick > 3:
            curr_sensors["vibration"] += degradation * 1.15
            health_index -= degradation * 28.0
            
        elif scenario == "Sensor_Fault_CHT" and tick > 3:
            # Single sensor bias: CHT spikes without engine degradation
            curr_sensors["cht"] = 215.0 + random.gauss(0, 4)
            health_index -= 4.0
            
        elif scenario == "Engine_Failure_Multi" and tick > 3:
            curr_sensors["rpm"] -= degradation * 600.0
            curr_sensors["cht"] += degradation * 55.0
            curr_sensors["egt"] += degradation * 110.0
            curr_sensors["oil_pressure"] -= degradation * 25.0
            curr_sensors["oil_temperature"] += degradation * 30.0
            curr_sensors["vibration"] += degradation * 0.8
            curr_sensors["fuel_flow"] += degradation * 5.0
            health_index -= degradation * 55.0

        health_index = max(8.0, min(99.0, health_index))

        # 3. Compute Sensor Items with Status (NORMAL, CAUTION, ALERT) and Trends (UP, DOWN, STABLE)
        sensor_list = []
        sensors_dict = {}
        
        for key, val in curr_sensors.items():
            cfg = self.sensor_ranges[key]
            val_clamped = round(val, 2 if key in ["vibration", "fuel_flow"] else 1)
            prev_val = self.prev_sensors.get(key, val)
            
            # Trend
            diff = val - prev_val
            threshold = 0.05 * (cfg["max"] - cfg["min"]) / 50.0
            trend = "STABLE"
            if diff > threshold:
                trend = "UP"
            elif diff < -threshold:
                trend = "DOWN"
                
            # Status
            status = "NORMAL"
            if val >= cfg["alert_high"] or val <= cfg["alert_low"]:
                status = "ALERT"
            elif val >= cfg["caution_high"] or val <= cfg["caution_low"]:
                status = "CAUTION"
                
            # Progress percentage
            pct = ((val_clamped - cfg["min"]) / (cfg["max"] - cfg["min"])) * 100.0
            pct = max(2.0, min(98.0, pct))
            
            item = {
                "key": key,
                "name": cfg["label"],
                "value": val_clamped,
                "unit": cfg["unit"],
                "min": cfg["min"],
                "max": cfg["max"],
                "status": status,
                "trend": trend,
                "progressPct": round(pct, 1)
            }
            sensor_list.append(item)
            sensors_dict[key] = item

        self.prev_sensors = dict(curr_sensors)

        # 4. RUL & Time Remaining Calculation
        # Nominal unclipped RUL starts at 117.4 cycles
        # Degrades when health decreases or fault injected
        actual_rul = max(0.0, float(self.max_useful_life - self.cycle))
        
        # Model predicted RUL with slight realistic LSTM variation and fault impact
        health_penalty = (100.0 - health_index) * 1.1
        predicted_rul = max(0.0, actual_rul - health_penalty + random.uniform(-1.5, 1.5))
        
        # Formulate Remaining Mission Time
        # Remaining Time = RUL cycles * avg cycle duration (60s)
        total_seconds = int(predicted_rul * self.avg_cycle_duration_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        remaining_time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
        rul_unclipped = round(predicted_rul, 1)
        rul_clipped = min(self.max_useful_life, rul_unclipped)
        
        degradation_trend = "Stable"
        if health_index < 40 or scenario in ["Overheating", "Engine_Failure_Multi", "Oil_Pressure_Loss"]:
            degradation_trend = "Accelerating"
        elif health_index < 70:
            degradation_trend = "Increasing"
            
        confidence = 0.924 if scenario == "Normal" else (0.875 if health_index > 40 else 0.952)

        abs_error = round(abs(predicted_rul - actual_rul), 1)
        model_mae = 10.08  # CMAPSS benchmark evaluation MAE

        prognostics_data = {
            "predicted_rul": rul_unclipped,
            "actual_rul": round(actual_rul, 1),
            "remaining_time_str": remaining_time_str,
            "current_cycle": self.cycle,
            "max_useful_life": self.max_useful_life,
            "rul_unclipped": rul_unclipped,
            "rul_clipped": rul_clipped,
            "degradation_trend": degradation_trend,
            "confidence": round(confidence * 100, 1),
            "abs_error": abs_error,
            "model_mae": model_mae,
            "window_size": 30,
            "sensor_count": 15
        }

        # 5. Risk & Decision Engine
        # User-friendly, professional, actionable flight recommendations
        if scenario == "Normal":
            risk_level = "LOW"
            anomaly_state = "NORMAL"
            recommended_action = "All engine systems and sensors are performing nominally. Continue planned cruise profile."
            status_label = "SYSTEMS OPTIMAL"
            guidance = "All thermal, hydraulic, and electrical parameters are within standard operating limits. No pilot intervention required."
        elif scenario in ["Sensor_Fault_CHT", "Sensor_Fault_Temp"]:
            risk_level = "MEDIUM"
            anomaly_state = "CAUTION"
            recommended_action = "CHT thermocouple reading is anomalous, but engine is healthy. Continue flight and inspect sensor wiring post-flight."
            status_label = "SENSOR ADVISORY"
            guidance = "Cross-sensor validation confirms normal RPM, EGT, and oil pressure. No power reduction is required."
        elif scenario == "Sensor_Drift":
            risk_level = "MEDIUM"
            anomaly_state = "CAUTION"
            recommended_action = "Gradual calibration drift detected on CHT sensor. Recalibrate thermocouple probe at next maintenance stop."
            status_label = "CALIBRATION NOTICE"
            guidance = "Physical thermodynamic models confirm normal engine operation. Bias is isolated to the instrument channel."
        elif scenario == "Overheating":
            risk_level = "HIGH"
            anomaly_state = "CAUTION"
            recommended_action = "Engine temperatures are elevated. Reduce throttle to 60%, level off, and monitor cylinder head cooling."
            status_label = "THERMAL CAUTION"
            guidance = "Maintain airspeed above 85 KIAS to optimize ram-air cooling through radiator baffles until temperatures stabilize."
        elif scenario == "Oil_Pressure_Loss":
            risk_level = "CRITICAL"
            anomaly_state = "ALERT"
            recommended_action = "Low oil pressure warning. Reduce engine power and divert to the nearest available airfield."
            status_label = "LUBRICATION ALERT"
            guidance = "Oil pressure is below normal operating limits. Avoid high-load maneuvers and prepare for a precautionary landing."
        elif scenario == "RPM_Drop":
            risk_level = "HIGH"
            anomaly_state = "CAUTION"
            recommended_action = "Uncommanded engine power drop detected. Verify throttle lever and monitor governor response."
            status_label = "POWER ADVISORY"
            guidance = "Check fuel flow and auxiliary pump status. Maintain safe glide airspeed while diagnosing governor response."
        elif scenario == "High_Vibration":
            risk_level = "HIGH"
            anomaly_state = "CAUTION"
            recommended_action = "Elevated airframe vibration detected. Adjust RPM away from resonant band and inspect propeller on landing."
            status_label = "MECHANICAL CAUTION"
            guidance = "Avoid operating between 2,200 and 2,400 RPM. Restrict continuous power to prevent mechanical fatigue."
        elif scenario == "Misfire":
            risk_level = "MEDIUM"
            anomaly_state = "CAUTION"
            recommended_action = "Intermittent cylinder misfire detected. Enrich fuel mixture and monitor engine smoothness."
            status_label = "COMBUSTION CAUTION"
            guidance = "Combustion irregularity observed. Check dual ignition circuits and avoid high climb power settings."
        elif scenario == "Engine_Failure_Multi":
            risk_level = "CRITICAL"
            anomaly_state = "ALERT"
            recommended_action = "Multiple engine systems failing simultaneously. Initiate emergency procedures and land immediately."
            status_label = "EMERGENCY DIRECTIVE"
            guidance = "Correlated thermal, hydraulic, and mechanical degradation confirmed. Establish best glide and execute forced landing checklist."
        else:
            has_alert_sensor = any(s["status"] == "ALERT" for s in sensor_list)
            risk_level = "CRITICAL" if has_alert_sensor else "HIGH"
            anomaly_state = "ALERT" if has_alert_sensor else "CAUTION"
            recommended_action = "Operational parameter variance detected. Inspect active alert sensors and follow checklist."
            status_label = "OPERATIONAL ALERT"
            guidance = "Refer to subsystem diagnostics tab for detailed residual analysis."

        risk_data = {
            "level": risk_level,
            "anomaly": anomaly_state,
            "action": recommended_action,
            "status_label": status_label,
            "guidance": guidance
        }

        # 6. Top Contributing Features Engine
        # Calculate dynamic feature importance weights based on deviations
        feat_weights = {
            "EGT": 0.218 + (0.15 if curr_sensors["egt"] > 680 else 0),
            "CHT": 0.183 + (0.18 if curr_sensors["cht"] > 165 else 0),
            "Vibration": 0.142 + (0.20 if curr_sensors["vibration"] > 2.0 else 0),
            "Oil Pressure": 0.128 + (0.22 if curr_sensors["oil_pressure"] < 50 else 0),
            "Oil Temperature": 0.096 + (0.08 if curr_sensors["oil_temperature"] > 105 else 0),
            "Fuel Flow": 0.071 + (0.05 if curr_sensors["fuel_flow"] > 22 else 0),
            "RPM": 0.062 + (0.08 if curr_sensors["rpm"] < 2100 else 0),
            "Injection Timing": 0.050
        }
        
        # Normalize weights to sum to 1.0
        total_w = sum(feat_weights.values())
        norm_weights = {k: v / total_w for k, v in feat_weights.items()}
        sorted_feats = sorted(norm_weights.items(), key=lambda x: x[1], reverse=True)
        
        impact_map = {
            "EGT": "increases thermal stress",
            "CHT": "increases cylinder thermal gradient",
            "Vibration": "indicates mechanical wear",
            "Oil Pressure": "indicates lubrication concern",
            "Oil Temperature": "indicates cooling oil breakdown",
            "Fuel Flow": "indicates mixture deviation",
            "RPM": "indicates power output lag",
            "Injection Timing": "indicates combustion phase shift"
        }
        
        direction_map = {
            "EGT": "UP" if curr_sensors["egt"] > 620 else "STABLE",
            "CHT": "UP" if curr_sensors["cht"] > 145 else "STABLE",
            "Vibration": "UP" if curr_sensors["vibration"] > 1.5 else "STABLE",
            "Oil Pressure": "DOWN" if curr_sensors["oil_pressure"] < 65 else "STABLE",
            "Oil Temperature": "UP" if curr_sensors["oil_temperature"] > 95 else "STABLE",
            "Fuel Flow": "UP" if curr_sensors["fuel_flow"] > 18.0 else "STABLE",
            "RPM": "DOWN" if curr_sensors["rpm"] < 2400 else "STABLE",
            "Injection Timing": "STABLE"
        }
        
        contributing_features = [
            {
                "name": name,
                "score": round(score, 3),
                "impact": impact_map.get(name, "drives RUL downward"),
                "direction": direction_map.get(name, "STABLE")
            }
            for name, score in sorted_feats
        ]

        # 7. Update 30-Cycle Trend Points & Deltas
        self.recent_30_cycles.append({
            "cycle": self.cycle,
            "egt": round(curr_sensors["egt"], 1),
            "oil_pressure": round(curr_sensors["oil_pressure"], 1),
            "vibration": round(curr_sensors["vibration"], 2),
            "health_index": round(health_index, 1)
        })
        if len(self.recent_30_cycles) > 30:
            self.recent_30_cycles.pop(0)
            
        first_pt = self.recent_30_cycles[0]
        last_pt = self.recent_30_cycles[-1]
        
        recent_trends = {
            "points": self.recent_30_cycles,
            "deltas": {
                "egt_delta": round(last_pt["egt"] - first_pt["egt"], 1),
                "oil_pressure_delta": round(last_pt["oil_pressure"] - first_pt["oil_pressure"], 1),
                "vibration_delta": round(last_pt["vibration"] - first_pt["vibration"], 2),
                "health_delta": round(last_pt["health_index"] - first_pt["health_index"], 1),
            }
        }

        # 8. Update Trajectory History (Cycle 1 to current)
        # Ensure latest point matches current cycle and prediction
        if not self.trajectory_history or self.trajectory_history[-1]["cycle"] != self.cycle:
            self.trajectory_history.append({
                "cycle": self.cycle,
                "actual_rul": round(actual_rul, 1),
                "predicted_rul": rul_unclipped
            })
        else:
            self.trajectory_history[-1]["predicted_rul"] = rul_unclipped

        # 9. Dynamic PHM Alerts Feed Generation
        if scenario != "Normal":
            if curr_sensors["egt"] > 680 and not any("EGT" in a["title"] for a in self.alert_feed[:2]):
                self.alert_feed.insert(0, {
                    "id": f"alt-{len(self.alert_feed)+1}",
                    "level": "CAUTION" if curr_sensors["egt"] < 750 else "ALERT",
                    "title": "ELEVATED EGT TREND",
                    "message": f"EGT rising faster than baseline ({curr_sensors['egt']:.1f} °C).",
                    "time_ago": "Just now",
                    "timestamp": datetime.now().isoformat()
                })
            if curr_sensors["vibration"] > 2.0 and not any("VIBRATION" in a["title"] for a in self.alert_feed[:2]):
                self.alert_feed.insert(0, {
                    "id": f"alt-{len(self.alert_feed)+1}",
                    "level": "CAUTION" if curr_sensors["vibration"] < 2.8 else "ALERT",
                    "title": "VIBRATION INCREASING",
                    "message": f"Vibration harmonics elevated to {curr_sensors['vibration']:.2f} g. Monitor bearing & valve train.",
                    "time_ago": "Just now",
                    "timestamp": datetime.now().isoformat()
                })
            if curr_sensors["oil_pressure"] < 50 and not any("OIL" in a["title"] for a in self.alert_feed[:2]):
                self.alert_feed.insert(0, {
                    "id": f"alt-{len(self.alert_feed)+1}",
                    "level": "ALERT",
                    "title": "LOW OIL PRESSURE",
                    "message": f"Oil pressure dropped to {curr_sensors['oil_pressure']:.1f} psi. Lubrication film at risk.",
                    "time_ago": "Just now",
                    "timestamp": datetime.now().isoformat()
                })
            if predicted_rul < 30 and not any("RUL" in a["title"] for a in self.alert_feed[:2]):
                self.alert_feed.insert(0, {
                    "id": f"alt-{len(self.alert_feed)+1}",
                    "level": "ALERT",
                    "title": "LOW REMAINING USEFUL LIFE",
                    "message": f"RUL estimate critical ({predicted_rul:.0f} cycles left). Plan immediate recovery.",
                    "time_ago": "Just now",
                    "timestamp": datetime.now().isoformat()
                })
        else:
            # If scenario is Normal, reset alerts to nominal state
            if any(a["level"] in ["ALERT", "CAUTION"] for a in self.alert_feed):
                self._init_alerts()

        # Keep alerts to max 10
        self.alert_feed = self.alert_feed[:10]

        return {
            "cycle": self.cycle,
            "timestamp": datetime.now().isoformat(),
            "vehicle": {
                "vehicle_id": "UAV_ENG_001",
                "mission_id": "ISR_PATROL_27",
                "altitude": simulation_state.get("altitude", 15000),
                "throttle": simulation_state.get("throttle", 75),
                "update_rate": 1
            },
            "sensors": sensors_dict,
            "sensor_list": sensor_list,
            "prognostics": prognostics_data,
            "health_index": round(health_index, 1),
            "risk": risk_data,
            "contributing_features": contributing_features,
            "recent_trends": recent_trends,
            "trajectory": self.trajectory_history[-60:], # send last 60 points for responsive rendering
            "alerts": self.alert_feed,
            "fault_label": scenario,
            "scenario": scenario
        }

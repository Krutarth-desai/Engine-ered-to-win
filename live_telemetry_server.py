import os
import warnings
# Suppress TensorFlow and scikit-learn warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
warnings.filterwarnings("ignore", category=UserWarning)

import asyncio
import json
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from supabase import create_client, Client

from src.predictive_maintenance import AeroTwinAnomalyDetector
from src.sensor_diagnosis import SensorDiagnosisEngine

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase Client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase_client = None
if supabase_url and supabase_key:
    supabase_client = create_client(supabase_url, supabase_key)
    print("Successfully connected to Supabase for backend logging.")
else:
    print("Warning: Missing Supabase credentials in .env. Anomalies will not be logged to DB.")

# Useful sensors expected by the LSTM model
useful_sensors = ['sensor_2', 'sensor_3', 'sensor_4', 'sensor_6', 'sensor_7', 'sensor_8', 'sensor_9', 'sensor_11', 'sensor_12', 'sensor_13', 'sensor_14', 'sensor_15', 'sensor_17', 'sensor_20', 'sensor_21']

# Load LSTM Model and Scaler at startup
rul_scaler = None
rul_model = None
test_df = None
rul_ground_truth = []

try:
    scaler_path = "models/rul_scaler.pkl"
    model_path = "models/rul_lstm.keras"
    test_path = "data/HPC_Degradation/test_FD001.txt"
    truth_path = "data/HPC_Degradation/RUL_FD001.txt"
    
    if os.path.exists(scaler_path):
        rul_scaler = joblib.load(scaler_path)
        print("Successfully loaded RUL scaler.")
    if os.path.exists(model_path):
        rul_model = tf.keras.models.load_model(model_path)
        print("Successfully loaded RUL LSTM model.")
    if os.path.exists(test_path):
        test_df = pd.read_csv(test_path, sep=r'\s+', header=None)
        test_df.columns = ["unit", "cycle", "setting1", "setting2", "setting3"] + [f"sensor_{i}" for i in range(1, 22)]
        print("Successfully loaded CMAPSS test data.")
    if os.path.exists(truth_path):
        rul_ground_truth = pd.read_csv(truth_path, sep=r'\s+', header=None).iloc[:, 0].tolist()
        print("Successfully loaded CMAPSS ground truth RUL values.")
except Exception as e:
    print(f"Error loading models/datasets at startup: {e}")

app = FastAPI(title="MALE UAV Digital Twin Telemetry Server")

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_root():
    """API Root endpoint pointing to the Next.js React frontend."""
    return {
        "status": "online",
        "service": "AeroTwin MALE UAV Digital Twin Telemetry & ML Server",
        "version": "2.0.0",
        "frontend": "http://localhost:3000",
        "endpoints": {
            "telemetry_ws": "/ws/telemetry",
            "rul_ws": "/ws/rul",
            "regression_plot": "/api/regression_plot"
        }
    }

# Global simulation state
simulation_state = {
    "is_running": True,  # Auto-start for convenience
    "scenario": "Normal",
    "selected_unit": 1,
    "tick": 0,
    "throttle": 75.0,
    "altitude": 15000.0,
    "ambient_temp": 15.0
}

# Predictive Maintenance State
anomaly_detector = AeroTwinAnomalyDetector(contamination=0.05)
sensor_diagnosis_engine = SensorDiagnosisEngine(
    sensor_anomaly_threshold=3.0,
    engine_failure_min_sensors=3,
    persistence_window=5,
    model_path="models/sensor_cross_models.pkl"
)
recent_telemetry_buffer = []  # Store recent telemetry for regression plot

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

def generate_live_data_tick(tick: int, scenario: str):
    """Generates a single point in time telemetry tick."""
    RUL_DATA = sorted([112, 98, 69, 82, 91, 93, 91, 95, 111, 96, 97, 124, 95, 107, 83, 84, 50, 28, 87, 16, 57, 111, 113, 20, 145, 119, 66, 97, 90, 115, 8, 48, 106, 7, 11, 19, 21, 50, 142, 28, 18, 10, 59, 109, 114, 47, 135, 92, 21, 79, 114, 29, 26, 97, 137, 15, 103, 37, 114, 100, 21, 54, 72, 28, 128, 14, 77, 8, 121, 94, 118, 50, 131, 126, 113, 10, 34, 107, 63, 90, 8, 9, 137, 58, 118, 89, 116, 115, 136, 28, 38, 20, 85, 55, 128, 137, 82, 59, 117, 20, 18, 79, 106, 110, 15, 155, 6, 90, 11, 79, 6, 73, 30, 11, 37, 67, 68, 99, 22, 54, 97, 10, 142, 77, 88, 163, 126, 138, 83, 78, 75, 11, 53, 173, 63, 100, 151, 55, 48, 37, 44, 27, 18, 6, 15, 112, 131, 13, 122, 13, 98, 53, 52, 106, 103, 152, 123, 26, 178, 73, 169, 39, 39, 14, 11, 121, 86, 56, 115, 17, 148, 104, 78, 86, 98, 36, 94, 52, 91, 15, 141, 74, 146, 17, 47, 194, 21, 79, 97, 8, 9, 73, 183, 97, 73, 49, 31, 97, 9, 14, 106, 8, 8, 106, 116, 120, 61, 168, 35, 80, 9, 50, 151, 78, 91, 7, 181, 150, 106, 15, 67, 145, 180, 7, 179, 124, 82, 108, 79, 121, 120, 39, 38, 9, 167, 87, 88, 7, 51, 55, 155, 47, 81, 43, 98, 10, 92, 11, 165, 34, 115, 59, 99, 103, 108, 83, 171, 15, 9, 42, 13, 41, 88, 14, 155, 188, 96, 82, 135, 182, 36, 107, 14, 95, 142, 23, 6, 144, 35, 97, 68, 14, 67, 191, 19, 10, 158, 183, 43, 12, 148, 13, 37, 122, 80, 93, 132, 32, 103, 174, 111, 68, 192, 121, 134, 48, 85, 8, 23, 8, 6, 57, 83, 172, 101, 81, 86, 165, 73, 121, 139, 75, 151, 145, 11, 108, 14, 126, 61, 85, 8, 101, 153, 89, 190, 12, 62, 134, 101, 121, 167, 17, 161, 181, 16, 152, 148, 56, 111, 23, 84, 12, 43, 48, 122, 191, 56, 131, 51, 44, 51, 27, 120, 101, 99, 71, 55, 55, 66, 77, 115, 115, 31, 108, 56, 136, 132, 85, 56, 18, 119, 78, 9, 58, 11, 88, 144, 124, 89, 79, 55, 71, 65, 87, 137, 145, 22, 8, 41, 131, 115, 128, 69, 111, 7, 137, 55, 135, 11, 78, 120, 87, 87, 55, 93, 88, 40, 49, 128, 129, 58, 117, 28, 115, 87, 92, 103, 100, 63, 35, 45, 99, 117, 45, 27, 86, 20, 18, 133, 15, 6, 145, 104, 56, 25, 68, 144, 41, 51, 81, 14, 67, 10, 127, 113, 123, 17, 8, 28], reverse=True)
    # Base engine parameters with normal operational noise
    rpm = np.random.normal(6100, 20)
    cht = np.random.normal(150, 2)
    egt = np.random.normal(700, 5)
    oil_pressure = np.random.normal(4.3, 0.1)
    oil_temperature = np.random.normal(95, 2)
    fuel_flow = np.random.normal(18.5, 0.2)
    vibration = np.random.normal(0.2, 0.02)
    battery_voltage = np.random.normal(28.0, 0.1)
    injection_timing = np.random.normal(22.0, 0.1)
    
    health_index = 100.0
    fault_label = "Normal"
    
    # Fault injection based on time progression (tick)
    degradation = min(tick / 60.0, 1.0)
    
    if scenario == "Overheating" and tick > 5:
        cht += degradation * 40
        egt += degradation * 60
        oil_temperature += degradation * 30
        health_index -= degradation * 30
        fault_label = "Overheating"
        
    elif scenario == "Injector_Degradation" and tick > 5:
        fuel_flow += degradation * 5
        egt += degradation * 40
        rpm += np.random.normal(0, degradation * 50)
        health_index -= degradation * 40
        fault_label = "Injector_Degradation"
        
    elif scenario == "Lubrication" and tick > 5:
        oil_pressure -= degradation * 1.5
        oil_temperature += degradation * 25
        vibration += degradation * 0.3
        health_index -= degradation * 50
        fault_label = "Lubrication"
        
    elif scenario == "Vibration_Fault" and tick > 5:
        vibration += degradation * 0.8
        health_index -= degradation * 25
        fault_label = "Vibration_Fault"
        
    elif scenario == "Sensor_Drift" and tick > 5:
        cht += degradation * 30
        health_index -= degradation * 10
        fault_label = "Sensor_Drift"
        
    elif scenario == "Misfire" and tick > 5:
        misfire_severity = degradation
        rpm -= np.random.uniform(0, misfire_severity * 300)
        vibration += misfire_severity * 0.5
        egt -= misfire_severity * 50
        health_index -= misfire_severity * 45
        fault_label = "Misfire"

    # --- NEW: Sensor Fault Isolation Demo ---
    elif scenario == "Sensor_Fault_Temp" and tick > 3:
        # Only CHT sensor goes extreme; all other params stay normal
        # This simulates a faulty temperature sensor, NOT an engine problem
        cht = 350.0 + np.random.normal(0, 5)  # [DEMO] Injected sensor fault
        health_index -= 5  # Mild health impact from suspicious reading
        fault_label = "Sensor_Fault_Temp"

    # --- NEW: Multi-Sensor Engine Failure Demo ---
    elif scenario == "Engine_Failure_Multi" and tick > 3:
        # Multiple sensors degrade simultaneously — genuine engine fault
        engine_deg = degradation
        rpm -= engine_deg * 700
        cht += engine_deg * 60
        egt += engine_deg * 120
        oil_pressure -= engine_deg * 1.8
        oil_temperature += engine_deg * 35
        vibration += engine_deg * 0.7
        fuel_flow += engine_deg * 7
        health_index -= engine_deg * 55
        fault_label = "Engine_Failure_Multi"

    data = {
        "timestamp": datetime.now().isoformat(),
        "engine_id": "ENG_001",
        "mission_id": "LIVE_SIM_001",
        "scenario": scenario,
        "tick": tick,
        "rpm": round(rpm, 1),
        "throttle_pct": simulation_state["throttle"],
        "altitude_ft": simulation_state["altitude"],
        "ambient_temp_c": simulation_state["ambient_temp"],
        "cht_c": round(cht, 1),
        "egt_c": round(egt, 1),
        "oil_pressure_bar": round(oil_pressure, 2),
        "oil_temperature_c": round(oil_temperature, 1),
        "fuel_flow_lh": round(fuel_flow, 1),
        "vibration_g": round(vibration, 3),
        "battery_voltage_v": round(battery_voltage, 1),
        "injection_timing_deg": round(injection_timing, 1),
        "health_index": round(health_index, 1),
        "rul": RUL_DATA[tick % len(RUL_DATA)],
        "fault_label": fault_label
    }
    return data

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                if "scenario" in cmd:
                    simulation_state["scenario"] = cmd["scenario"]
                    simulation_state["tick"] = 0
                    # Reset sensor diagnosis persistence on scenario change
                    sensor_diagnosis_engine.reset_persistence()
                    print(f"*** Injected scenario: {cmd['scenario']} ***")
                if "is_running" in cmd:
                    simulation_state["is_running"] = cmd["is_running"]
            except Exception as e:
                print(f"Error parsing command: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def simulation_loop():
    """Background task that ticks the simulation and broadcasts data at 1 Hz."""
    while True:
        if simulation_state["is_running"] and len(manager.active_connections) > 0:
            data = generate_live_data_tick(simulation_state["tick"], simulation_state["scenario"])
            
            # --- Predictive Maintenance Pipeline ---
            is_anomaly, score = anomaly_detector.detect(data)
            fault_info = anomaly_detector.infer_fault(data, is_anomaly, score)
            data.update(fault_info)
            data["anomaly_score"] = score
            
            # --- Sensor vs Engine Diagnosis Pipeline ---
            diag_result = sensor_diagnosis_engine.diagnose(
                data,
                is_isolation_forest_anomaly=is_anomaly,
                isolation_forest_score=score
            )
            data["sensor_diagnosis"] = diag_result
            
            # If sensor failure is suspected, override treatment recommendation
            if diag_result["diagnosis_type"] == "POSSIBLE_SENSOR_FAILURE" and diag_result["suspected_sensor"]:
                sensor_name = diag_result["suspected_sensor"]
                data["prevention"] = (
                    f"SENSOR DIAGNOSIS: Possible {sensor_name} sensor malfunction detected. "
                    f"Check sensor wiring, calibration, and connector integrity. "
                    f"Replace sensor if fault persists. Engine core appears healthy."
                )
            elif diag_result["diagnosis_type"] == "POSSIBLE_ENGINE_FAILURE":
                data["prevention"] = (
                    f"ENGINE DIAGNOSIS: Multiple sensor anomalies detected simultaneously. "
                    f"Affected: {', '.join(diag_result['affected_sensors'])}. "
                    f"Proceed with engine fault prediction and preventive maintenance protocol."
                )
            
            # Log anomaly to Supabase if it's not normal
            if supabase_client and fault_info["status"] != "Normal":
                anomaly_record = {
                    "engine_id": "Engine-1",
                    "anomaly_score": float(score),
                    "severity": fault_info["severity"],
                    "fault_type": fault_info["fault"],
                    "evidence": fault_info["evidence"],
                    "treatment_action": fault_info["treatment"],
                    "prevention_action": fault_info["prevention"],
                    "diagnosis_type": diag_result["diagnosis_type"],
                    "diagnosis_confidence": max(
                        diag_result["sensor_fault_confidence"],
                        diag_result["engine_fault_confidence"]
                    ),
                    "suspected_sensor": diag_result.get("suspected_sensor"),
                    "affected_sensors": json.dumps(diag_result.get("affected_sensors", [])),
                    "sensor_anomaly_scores": json.dumps(diag_result.get("sensor_scores", {}))
                }
                # Run in background to prevent blocking the WebSocket loop
                def push_to_supabase(record):
                    try:
                        supabase_client.table("telemetry_anomalies").insert(record).execute()
                    except Exception as e:
                        print(f"[Supabase] Failed to log anomaly: {e}")
                
                asyncio.create_task(asyncio.to_thread(push_to_supabase, anomaly_record))
            
            # Buffer for regression plot
            recent_telemetry_buffer.append(data)
            if len(recent_telemetry_buffer) > 100:
                recent_telemetry_buffer.pop(0)
            # ---------------------------------------

            await manager.broadcast(json.dumps(data))
            simulation_state["tick"] += 1
        await asyncio.sleep(1.0)

@app.get("/api/regression_plot")
async def get_regression_plot():
    """Generates a regression plot from recent telemetry buffer and returns it as a base64 image."""
    if len(recent_telemetry_buffer) < 10:
        return {"image": None}

    # Prepare data (CHT vs RPM)
    df = pd.DataFrame(recent_telemetry_buffer)
    if 'rpm' not in df or 'cht_c' not in df:
        return {"image": None}
        
    x = df['rpm']
    y = df['cht_c']

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0e1526')
    ax.set_facecolor('#070b14')

    ax.scatter(x, y, color='#38bdf8', alpha=0.6, label="Telemetry Points")
    
    # Regression line
    if len(x) > 1:
        m, b = np.polyfit(x, y, 1)
        ax.plot(x, m*x + b, color='#ef4444', linewidth=2, label="Trend (Best Fit)")

    ax.set_xlabel("Engine RPM", color='#94a3b8')
    ax.set_ylabel("CHT (°C)", color='#94a3b8')
    ax.set_title("Engine Temperature vs RPM Analysis", color='#f8fafc')
    ax.tick_params(colors='#64748b')
    ax.spines['bottom'].set_color('#1e293b')
    ax.spines['top'].set_color('#1e293b')
    ax.spines['right'].set_color('#1e293b')
    ax.spines['left'].set_color('#1e293b')
    ax.legend(facecolor='#070b14', edgecolor='#1e293b', labelcolor='#94a3b8')

    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    plt.close(fig)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    return {"image": f"data:image/png;base64,{img_base64}"}

# ================================================================
# REMAINING TIME — /ws/rul WebSocket Endpoint
# ================================================================
WINDOW_SIZE = 30

@app.websocket("/ws/rul")
async def websocket_rul(websocket: WebSocket):
    """WebSocket endpoint for CMAPSS RUL prognostics streaming."""
    await websocket.accept()
    print("RUL client connected.")

    # Send list of available engine units
    if test_df is not None:
        units = sorted(test_df["unit"].unique().tolist())
        await websocket.send_text(json.dumps({"type": "engine_list", "units": units}))
    else:
        await websocket.send_text(json.dumps({"type": "engine_list", "units": []}))

    selected_unit = 1
    cycle_idx = 0
    streaming = False
    unit_data = None
    sensor_buffer = []

    async def stream_engine():
        nonlocal cycle_idx, unit_data, sensor_buffer, selected_unit, streaming

        if test_df is None or rul_model is None or rul_scaler is None:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "LSTM model or CMAPSS data not loaded on server."
            }))
            return

        # Get data for the selected unit
        unit_data_df = test_df[test_df["unit"] == selected_unit].sort_values("cycle").reset_index(drop=True)
        if len(unit_data_df) == 0:
            return

        # Compute actual RUL for this test engine
        # Ground truth gives the remaining RUL after the last recorded cycle
        unit_idx = selected_unit - 1
        remaining_after_last = rul_ground_truth[unit_idx] if unit_idx < len(rul_ground_truth) else 0
        max_rul = len(unit_data_df) - 1 + remaining_after_last

        sensor_buffer = []
        cycle_idx = 0
        streaming = True

        for i in range(len(unit_data_df)):
            if not streaming:
                break

            row = unit_data_df.iloc[i]
            cycle = int(row["cycle"])
            actual_rul = float(max_rul - i)
            actual_rul_clipped = min(actual_rul, 125.0)

            # Get sensor values for this cycle
            sensor_vals = row[useful_sensors].values.astype(float).reshape(1, -1)
            scaled_vals = rul_scaler.transform(sensor_vals)
            sensor_buffer.append(scaled_vals[0])

            predicted_rul = None

            # Once we have enough cycles for a window, run inference
            if len(sensor_buffer) >= WINDOW_SIZE:
                window = np.array(sensor_buffer[-WINDOW_SIZE:]).reshape(1, WINDOW_SIZE, len(useful_sensors))
                pred = rul_model.predict(window, verbose=0).flatten()[0]
                predicted_rul = float(max(pred, 0))

            tick_data = {
                "type": "rul_tick",
                "unit": selected_unit,
                "cycle": cycle,
                "actual_rul": round(actual_rul_clipped, 2),
                "predicted_rul": round(predicted_rul, 2) if predicted_rul is not None else None,
            }

            try:
                await websocket.send_text(json.dumps(tick_data))
            except Exception:
                streaming = False
                break

            await asyncio.sleep(0.15)  # Stream at ~6.7 Hz for smooth visualization

    try:
        # Start streaming in background
        stream_task = None

        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                if "unit" in cmd:
                    streaming = False  # Stop current stream
                    if stream_task and not stream_task.done():
                        stream_task.cancel()
                        try:
                            await stream_task
                        except (asyncio.CancelledError, Exception):
                            pass

                    selected_unit = int(cmd["unit"])
                    await websocket.send_text(json.dumps({"type": "reset", "unit": selected_unit}))
                    await asyncio.sleep(0.1)
                    stream_task = asyncio.create_task(stream_engine())
            except Exception as e:
                print(f"RUL WS error: {e}")
    except WebSocketDisconnect:
        streaming = False
        print("RUL client disconnected.")

@app.on_event("startup")
async def startup_event():
    # Train the IsolationForest baseline
    anomaly_detector.train_baseline()
    
    # Load or train sensor diagnosis cross-prediction models
    if not sensor_diagnosis_engine.load_models():
        print("[SensorDiagnosis] Pre-trained models not found. Training now...")
        sensor_diagnosis_engine.train_cross_models()
    
    asyncio.create_task(simulation_loop())
    print("\n=======================================================")
    print("MALE UAV Live Telemetry Server Started!")
    print("Open your browser and navigate to: http://localhost:8000")
    print("=======================================================\n")

if __name__ == "__main__":
    uvicorn.run("live_telemetry_server:app", host="0.0.0.0", port=8000, reload=True)

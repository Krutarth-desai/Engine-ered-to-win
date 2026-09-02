"use client";

import React from "react";
import { UnifiedTelemetryPayload } from "../types/telemetry";
import SensorDiagnosisPanel from "./SensorDiagnosisPanel";
import DiagnosisPanel from "./DiagnosisPanel";
import FeatureContributionPanel from "./FeatureContributionPanel";

interface DiagnosticsViewProps {
  payload: UnifiedTelemetryPayload;
}

export default function DiagnosticsView({ payload }: DiagnosticsViewProps) {
  const flatTelemetry = {
    timestamp: payload.timestamp,
    engine_id: payload.vehicle?.vehicle_id || "ENG_001",
    rpm: payload.sensors?.rpm?.value ?? payload.rpm ?? 2450,
    cht_c: payload.sensors?.cht?.value ?? payload.cht_c ?? 142.0,
    egt_c: payload.sensors?.egt?.value ?? payload.egt_c ?? 615.0,
    oil_pressure_bar: payload.sensors?.oil_pressure?.value
      ? payload.sensors.oil_pressure.value / 14.5038
      : (payload.oil_pressure_bar ?? 4.7),
    oil_temperature_c: payload.sensors?.oil_temperature?.value ?? payload.oil_temperature_c ?? 92.0,
    fuel_flow_lh: payload.sensors?.fuel_flow?.value ?? payload.fuel_flow_lh ?? 17.6,
    vibration_g: payload.sensors?.vibration?.value ?? payload.vibration_g ?? 1.42,
    battery_voltage_v: payload.sensors?.bus_voltage?.value ?? payload.battery_voltage_v ?? 27.6,
    injection_timing_deg: payload.sensors?.injection_timing?.value ?? payload.injection_timing_deg ?? 23.4,
    health_index: payload.health_index ?? 72,
    rul: payload.prognostics?.predicted_rul ?? 117,
    fault_label: payload.fault_label ?? "Normal",
    status: payload.risk?.anomaly ?? "Normal",
    severity: payload.risk?.level ?? "LOW",
    fault: payload.fault_label ?? "Nominal",
    evidence: payload.risk?.action ?? "All parameters within standard cruise envelope",
    treatment: payload.risk?.action ?? "Continue standard cruise",
    prevention: "Regular line inspection of wiring harness and sensors",
    sensor_diagnosis: payload.sensor_diagnosis,
  };

  return (
    <div className="view-container diagnostics-view">
      <div className="view-header-strip">
        <div>
          <h2 className="view-title"><strong>SUBSYSTEM DIAGNOSTICS &amp; SENSOR FAULT ISOLATION</strong></h2>
          <p className="view-subtitle">Cross-sensor regression modeling, physics health verification, and anomaly root-cause attribution</p>
        </div>
        <div className="diag-header-status">
          <span className="status-label"><strong>CURRENT DIAGNOSIS:</strong></span>
          <span className={`status-val status-${(payload.sensor_diagnosis?.diagnosis_type || "normal").toLowerCase()}`}>
            <strong>{payload.sensor_diagnosis?.diagnosis_type || "NORMAL"}</strong>
          </span>
        </div>
      </div>

      <div className="diagnostics-view-grid">
        {/* Row 1: Left Sensor vs Engine Diagnosis | Right Subsystem Physics Health & PHM Matrix */}
        <div className="diag-top-row">
          <div className="diag-col">
            <SensorDiagnosisPanel telemetry={flatTelemetry} />
          </div>
          <div className="diag-col">
            <DiagnosisPanel telemetry={flatTelemetry} />
          </div>
        </div>

        {/* Row 2: Top Contributing Features (SHAP / Gradient Feature Attribution) */}
        <div className="diag-bottom-row">
          <FeatureContributionPanel features={payload.contributing_features || []} />
        </div>
      </div>
    </div>
  );
}

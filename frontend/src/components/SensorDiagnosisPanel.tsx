"use client";

import React from "react";
import { TelemetryData } from "../types/telemetry";

interface SensorDiagnosisPanelProps {
  telemetry: TelemetryData | null;
}

const SENSOR_DISPLAY_MAP: Record<string, string> = {
  rpm: "Engine RPM",
  cht_c: "Cylinder Head Temp",
  egt_c: "Exhaust Gas Temp",
  oil_pressure_bar: "Oil Pressure",
  oil_temperature_c: "Oil Temperature",
  fuel_flow_lh: "Fuel Flow Rate",
  vibration_g: "Vibration RMS",
};

export default function SensorDiagnosisPanel({ telemetry }: SensorDiagnosisPanelProps) {
  const diag = telemetry?.sensor_diagnosis;
  const diagType = diag?.diagnosis_type || "NORMAL";
  let diagBadgeClass = "diag-badge-normal";
  if (diagType === "POSSIBLE_SENSOR_FAILURE") diagBadgeClass = "diag-badge-sensor";
  else if (diagType === "POSSIBLE_ENGINE_FAILURE") diagBadgeClass = "diag-badge-engine";
  else if (diagType !== "NORMAL") diagBadgeClass = "diag-badge-unknown";

  const diagBadgeText = diagType.replace(/_/g, " ");
  const suspectedSensor = diag?.suspected_sensor;
  const sensorConf = diag ? (diag.sensor_fault_confidence * 100).toFixed(0) + "%" : "0%";
  const engineConf = diag ? (diag.engine_fault_confidence * 100).toFixed(0) + "%" : "0%";
  const persistence = diag ? `${diag.persistence_count}/5` : "0/5";

  const scores = diag?.sensor_scores || {};
  const sensorsList = [
    { key: "rpm", label: "RPM" },
    { key: "cht_c", label: "CHT" },
    { key: "egt_c", label: "EGT" },
    { key: "oil_pressure_bar", label: "OIL P" },
    { key: "oil_temperature_c", label: "OIL T" },
    { key: "fuel_flow_lh", label: "FUEL" },
    { key: "vibration_g", label: "VIB" },
  ];

  const evidence =
    diag?.evidence ||
    "All engine sensors operating within expected cross-predicted relationships. No sensor or engine anomaly detected.";

  return (
    <div className="panel" id="sensor-diag-section">
      <div className="panel-header">
        <span className="panel-title">
          <span>🔬</span> SENSOR VS ENGINE DIAGNOSIS
        </span>
        <span id="diag-diagnosis-badge" className={`diag-diagnosis-badge ${diagBadgeClass}`}>
          {diagBadgeText}
        </span>
      </div>

      {/* Suspected Sensor */}
      {suspectedSensor && (
        <div className="diag-suspected-sensor" id="diag-suspected-row" style={{ display: "flex", padding: "0 0.5rem" }}>
          <span className="diag-suspected-label">Suspected Sensor:</span>
          <span className="diag-suspected-val" id="diag-suspected-val">
            {SENSOR_DISPLAY_MAP[suspectedSensor] || suspectedSensor}
          </span>
        </div>
      )}

      {/* Confidence Scores */}
      <div className="diag-confidence-row">
        <div className="diag-conf-item">
          <div className="diag-conf-label">SENSOR FAULT CONF.</div>
          <div className="diag-conf-val" id="diag-sensor-conf" style={{ color: "var(--accent-amber)" }}>
            {sensorConf}
          </div>
        </div>
        <div className="diag-conf-item">
          <div className="diag-conf-label">ENGINE FAULT CONF.</div>
          <div className="diag-conf-val" id="diag-engine-conf" style={{ color: "var(--accent-rose)" }}>
            {engineConf}
          </div>
        </div>
        <div className="diag-conf-item">
          <div className="diag-conf-label">PERSISTENCE</div>
          <div className="diag-conf-val" id="diag-persistence" style={{ color: "var(--accent-cyan)" }}>
            {persistence}
          </div>
        </div>
      </div>

      {/* Sensor Anomaly Score Bars */}
      <div className="diag-section-header" style={{ marginTop: "0.85rem", padding: "0 0.2rem" }}>
        <span>Sensor Anomaly Scores</span>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: "0.68rem",
            color: "var(--accent-cyan)",
          }}
        >
          CROSS-PREDICTION Σ
        </span>
      </div>
      <div className="sensor-bars-container" id="sensor-bars-container">
        {sensorsList.map((s) => {
          const score = scores[s.key] || 0;
          const pct = Math.min((score / 10) * 100, 100);
          let fillClass = "sensor-bar-fill";
          if (score > 3.0) fillClass += " critical";
          else if (score > 1.5) fillClass += " elevated";

          return (
            <div key={s.key} className="sensor-bar-row">
              <span className="sensor-bar-label">{s.label}</span>
              <div className="sensor-bar-track">
                <div
                  className={fillClass}
                  id={`sbar-${s.key}`}
                  style={{ width: `${Math.max(pct, 2)}%` }}
                />
              </div>
              <span className="sensor-bar-score" id={`sscore-${s.key}`}>
                {score.toFixed(1)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Evidence */}
      <div className="diag-evidence-box" id="diag-evidence">
        {evidence}
      </div>
    </div>
  );
}

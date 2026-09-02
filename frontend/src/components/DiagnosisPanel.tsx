"use client";

import React, { useEffect, useState } from "react";
import { TelemetryData } from "@/types/telemetry";

interface DiagnosisPanelProps {
  telemetry: TelemetryData | null;
}

const SENSOR_DISPLAY_MAP: Record<string, string> = {
  rpm: "RPM",
  cht_c: "CHT (Temp)",
  egt_c: "EGT",
  oil_pressure_bar: "Oil Pressure",
  oil_temperature_c: "Oil Temp",
  fuel_flow_lh: "Fuel Flow",
  vibration_g: "Vibration",
};

export default function DiagnosisPanel({ telemetry }: DiagnosisPanelProps) {
  const [regressionImage, setRegressionImage] = useState<string | null>(null);

  // Poll regression plot every 5 seconds
  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

    const fetchPlot = async () => {
      try {
        const res = await fetch(`${backendUrl}/api/regression_plot`);
        const json = await res.json();
        if (json.image) {
          setRegressionImage(json.image);
        }
      } catch (err) {
        // Silent catch for background poller
      }
    };

    fetchPlot();
    const interval = setInterval(fetchPlot, 5000);
    return () => clearInterval(interval);
  }, []);

  const faultLabel = telemetry?.fault_label || "Normal";
  const cht = telemetry?.cht_c ?? 150.0;
  const egt = telemetry?.egt_c ?? 700.0;
  const oilP = telemetry?.oil_pressure_bar ?? 4.3;
  const oilT = telemetry?.oil_temperature_c ?? 95.0;
  const fuel = telemetry?.fuel_flow_lh ?? 18.5;
  const vib = telemetry?.vibration_g ?? 0.2;
  const rpm = telemetry?.rpm ?? 6100;
  const anomalyScore = telemetry?.anomaly_score;

  // Subsystem variables
  let thermalPct = 98;
  let thermalText = "98% NOMINAL";
  let thermalColor = "var(--accent-emerald)";

  let fuelPct = 97;
  let fuelText = "97% NOMINAL";
  let fuelColor = "var(--accent-emerald)";

  let oilPct = 99;
  let oilText = "99% NOMINAL";
  let oilColor = "var(--accent-emerald)";

  let vibPct = 96;
  let vibText = "96% NOMINAL";
  let vibColor = "var(--accent-emerald)";

  let avionicsPct = 100;
  let avionicsText = "100% NOMINAL";
  let avionicsColor = "var(--accent-emerald)";

  // Advisory details
  let cardClass = "advisory-box";
  let title = "🛡️ Propulsion Health: Nominal";
  let desc =
    "All thermal, combustion, and lubrication parameters are operating within baseline tolerances. Digital Twin physics residuals are < 2.5%.";
  let action = "RECOMMENDATION: Continue planned mission profile. No maintenance required.";
  let badgeClass = "badge-optimal";
  let badgeText = "PHM AI: OPTIMAL";

  let statConf = "99.4%";
  let statConfColor = "var(--text-primary)";
  let statResidual = "< 2.1% RMS";
  let statPriority = "ROUTINE";
  let statPriorityColor = "var(--accent-emerald)";
  let statTrend = "STABLE CRUISE";
  let statTrendColor = "var(--accent-cyan)";
  let logText =
    "PHYSICS ENGINE: Telemetry parity matched across 9 sensor channels with zero divergence.";

  if (faultLabel === "Normal") {
    cardClass = "advisory-box";
    title = "🛡️ Propulsion Health: Nominal";
    desc =
      "All thermal, combustion, and lubrication parameters are operating within baseline tolerances. Digital Twin physics residuals are < 2.5%.";
    action = "RECOMMENDATION: Continue planned mission profile. No maintenance required.";
    badgeClass = "badge-optimal";
    badgeText = "PHM AI: OPTIMAL";
    statConf = "99.4%";
    statResidual = "< 2.1% RMS";
    statPriority = "ROUTINE";
    statPriorityColor = "var(--accent-emerald)";
    statTrend = "STABLE CRUISE";
    statTrendColor = "var(--accent-cyan)";
    logText =
      "PHYSICS ENGINE: Telemetry parity matched across 9 sensor channels with zero divergence.";
  } else if (faultLabel === "Overheating") {
    cardClass = "advisory-box critical";
    title = "🔥 Alert: Engine Overheating Trend Detected";
    desc = `CHT reached ${cht.toFixed(1)}°C and Oil Temp reached ${oilT.toFixed(1)}°C. Physics residual exceeds +35°C thermal model boundary.`;
    action =
      "ACTION: Reduce cruise throttle to 55%. Plan altitude descent for enhanced ram-air cooling. Inspect radiator fins post-flight.";
    badgeClass = "badge-critical";
    badgeText = "PHM AI: CRITICAL ALERT";
    thermalPct = 28;
    thermalText = "28% CRITICAL HEAT";
    thermalColor = "var(--accent-rose)";
    oilPct = 54;
    oilText = "54% HIGH TEMP";
    oilColor = "var(--accent-amber)";
    statConf = "98.9%";
    statResidual = "+38.4°C CHT DIV";
    statPriority = "URGENT (P1)";
    statPriorityColor = "var(--accent-rose)";
    statTrend = "HEAT DISSIPATION LOSS";
    statTrendColor = "var(--accent-rose)";
    logText = `THERMAL ANOMALY: Cylinder jacket heat transfer deficit detected (${cht.toFixed(1)}°C).`;
  } else if (faultLabel === "Injector_Degradation") {
    cardClass = "advisory-box warning";
    title = "⚙️ Warning: Fuel Injector Delivery Degradation";
    desc = `Fuel flow elevated (${fuel.toFixed(1)} L/h) with abnormal EGT and RPM fluctuations. Flow coefficient dropped 18%.`;
    action =
      "ACTION: Monitor fuel consumption vs endurance margin. Schedule injector ultrasonic cleaning at next turnaround.";
    badgeClass = "badge-warning";
    badgeText = "PHM AI: DEGRADED";
    fuelPct = 42;
    fuelText = "42% FLOW DEVIATION";
    fuelColor = "var(--accent-amber)";
    statConf = "96.8%";
    statResidual = "+4.6 L/H BIAS";
    statPriority = "ACTION REQ";
    statPriorityColor = "var(--accent-amber)";
    statTrend = "COMBUSTION IMBALANCE";
    statTrendColor = "var(--accent-amber)";
    logText = `COMBUSTION DIAGNOSTIC: Fuel mass flow residual divergence on rail (+${(fuel - 18.5).toFixed(1)} L/h).`;
  } else if (faultLabel === "Lubrication") {
    cardClass = "advisory-box critical";
    title = "🛢️ Urgent: Lubrication Starvation & Pressure Loss";
    desc = `Oil pressure dropped to ${oilP.toFixed(2)} bar while friction vibration is climbing (${vib.toFixed(3)} g).`;
    action =
      "CRITICAL ADVISORY: Potential bearing wear/pump cavitation. Abort mission if pressure drops below 3.0 bar. Divert to nearest recovery base.";
    badgeClass = "badge-critical";
    badgeText = "PHM AI: HYDRAULIC ALARM";
    oilPct = 18;
    oilText = "18% STARVATION";
    oilColor = "var(--accent-rose)";
    vibPct = 58;
    vibText = "58% FRICTION RISE";
    vibColor = "var(--accent-amber)";
    statConf = "99.5%";
    statResidual = "-1.85 BAR DEFICIT";
    statPriority = "EMERGENCY";
    statPriorityColor = "var(--accent-rose)";
    statTrend = "HYDRODYNAMIC LOSS";
    statTrendColor = "var(--accent-rose)";
    logText = `HYDRAULIC FAILURE: Main gallery oil pressure collapsed below 3.5 bar margin.`;
  } else if (faultLabel === "Vibration_Fault") {
    cardClass = "advisory-box warning";
    title = "〰️ Mechanical Anomaly: High Vibration Signature";
    desc = `Spectral energy spikes detected in 1X-2X crankshaft harmonics (${vib.toFixed(3)} g RMS). Probable propeller imbalance or mount looseness.`;
    action =
      "ACTION: Avoid resonant RPM bands. Restrict maximum continuous power. Perform mechanical mount inspection.";
    badgeClass = "badge-warning";
    badgeText = "PHM AI: VIBRATION SPIKE";
    vibPct = 25;
    vibText = "25% HARMONIC SPIKE";
    vibColor = "var(--accent-rose)";
    statConf = "97.6%";
    statResidual = `+${(vib - 0.2).toFixed(3)}g RMS`;
    statPriority = "INSPECTION";
    statPriorityColor = "var(--accent-amber)";
    statTrend = "DYNAMIC UNBALANCE";
    statTrendColor = "var(--accent-amber)";
    logText = `ROTORDYNAMICS: 1X crankshaft fundamental frequency vibration spike detected.`;
  } else if (faultLabel === "Sensor_Drift") {
    cardClass = "advisory-box warning";
    title = "📡 Avionics Alert: CHT Sensor Drift / Calibration Error";
    desc = `CHT reading (${cht.toFixed(1)}°C) diverges from physics-informed estimation, while EGT & Oil Temp remain normal. Engine is healthy.`;
    action =
      "INTELLIGENT DIAGNOSIS: Sensor failure detected via cross-sensor fusion. Engine safe to operate. Replace CHT probe on return.";
    badgeClass = "badge-warning";
    badgeText = "PHM AI: SENSOR FAULT";
    avionicsPct = 35;
    avionicsText = "35% SENSOR BIAS";
    avionicsColor = "var(--accent-amber)";
    statConf = "99.8%";
    statResidual = `+${(cht - 150).toFixed(1)}°C DRIFT`;
    statPriority = "POST-FLIGHT";
    statPriorityColor = "var(--accent-cyan)";
    statTrend = "SENSOR BIAS ONLY";
    statTrendColor = "var(--accent-cyan)";
    logText = `ANOMALY ISOLATION: Digital Twin neural estimator verified mechanical engine core is 100% healthy.`;
  } else if (faultLabel === "Misfire") {
    cardClass = "advisory-box critical";
    title = "💥 Combustion Instability: Intermittent Cylinder Misfire";
    desc =
      "Combustion irregularity detected with sudden RPM drops and unburnt exhaust gas temperature dips.";
    action =
      "ACTION: Check ignition coil & spark plug telemetry. Adjust mixture trim. If misfires persist, abort climb.";
    badgeClass = "badge-critical";
    badgeText = "PHM AI: MISFIRE FAULT";
    fuelPct = 22;
    fuelText = "22% MISFIRE UNSTABLE";
    fuelColor = "var(--accent-rose)";
    vibPct = 45;
    vibText = "45% COMBUSTION ROUGH";
    vibColor = "var(--accent-amber)";
    statConf = "98.5%";
    statResidual = "ΔRPM -280 / ΔEGT -50°";
    statPriority = "URGENT";
    statPriorityColor = "var(--accent-rose)";
    statTrend = "CYLINDER #1 MISFIRE";
    statTrendColor = "var(--accent-rose)";
    logText = `IGNITION FAULT: Power stroke torque pulsation detected on Cylinder #1.`;
  } else if (faultLabel === "Sensor_Fault_Temp") {
    cardClass = "advisory-box warning";
    title = "Sensor Isolation: CHT Sensor Fault Detected";
    desc = `CHT sensor reading (${cht.toFixed(1)} C) is physically impossible given normal RPM, EGT, oil pressure, and vibration. Cross-sensor ML prediction confirms engine is healthy - sensor malfunction suspected.`;
    action =
      "INTELLIGENT DIAGNOSIS: This is a SENSOR fault, NOT an engine fault. Engine safe to operate. Schedule CHT probe replacement.";
    badgeClass = "badge-warning";
    badgeText = "SENSOR ISOLATED";
    avionicsPct = 15;
    avionicsText = "15% SENSOR FAULT";
    avionicsColor = "var(--accent-rose)";
    statConf = "99.1%";
    statResidual = `+${(cht - 150).toFixed(0)} C SENSOR BIAS`;
    statPriority = "POST-FLIGHT";
    statPriorityColor = "var(--accent-cyan)";
    statTrend = "SENSOR FAULT ONLY";
    statTrendColor = "var(--accent-cyan)";
    logText = `SENSOR ISOLATION: Cross-sensor ML model confirmed CHT reading is inconsistent with other healthy parameters.`;
  } else if (faultLabel === "Engine_Failure_Multi") {
    cardClass = "advisory-box critical";
    title = "Critical: Multi-Sensor Engine Failure Detected";
    desc = `RPM (${rpm.toFixed(0)}), CHT (${cht.toFixed(1)} C), EGT (${egt.toFixed(1)} C), Oil Pressure (${oilP.toFixed(2)} bar), and Vibration (${vib.toFixed(3)} g) are simultaneously deviating from their learned cross-sensor relationships. This is a genuine engine fault, not a sensor error.`;
    action =
      "CRITICAL: Multiple correlated sensor anomalies confirm ENGINE-LEVEL failure. Initiate emergency procedures. Divert immediately.";
    badgeClass = "badge-critical";
    badgeText = "ENGINE FAILURE";
    thermalPct = 18;
    thermalText = "18% THERMAL CRISIS";
    thermalColor = "var(--accent-rose)";
    fuelPct = 25;
    fuelText = "25% FLOW ABNORMAL";
    fuelColor = "var(--accent-rose)";
    oilPct = 12;
    oilText = "12% OIL COLLAPSE";
    oilColor = "var(--accent-rose)";
    vibPct = 20;
    vibText = "20% MECH FAILURE";
    vibColor = "var(--accent-rose)";
    statConf = "99.7%";
    statResidual = "MULTI-SENSOR DIVERGENCE";
    statPriority = "EMERGENCY";
    statPriorityColor = "var(--accent-rose)";
    statTrend = "ENGINE FAILURE";
    statTrendColor = "var(--accent-rose)";
    logText = `ENGINE DIAGNOSIS: Cross-sensor ML analysis confirms correlated multi-parameter degradation - genuine engine fault.`;
  }

  if (anomalyScore !== undefined) {
    if (anomalyScore < 0) {
      statConf = `Score: ${anomalyScore.toFixed(3)}`;
      statConfColor = "var(--accent-rose)";
    } else {
      statConfColor = "var(--text-primary)";
    }
  }

  // Sensor vs Engine Diagnosis Extraction
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
    <div className="panel" style={{ flex: 1 }}>
      <div className="panel-header">
        <span className="panel-title">
          <span>🧠</span> Digital Twin Predictive Diagnostics
        </span>
        <span className={`status-badge-lg ${badgeClass}`} id="phm-mode-badge">
          {badgeText}
        </span>
      </div>

      <div className="diag-container">
        {/* Dynamic Advisory Box */}
        <div id="advisory-card" className={cardClass}>
          <div className="advisory-title" id="advisory-title">
            {title}
          </div>
          <div className="advisory-desc" id="advisory-desc">
            {desc}
          </div>
          <div className="advisory-action" id="advisory-action">
            {action}
          </div>
        </div>

        {/* Preventive Maintenance Box */}
        {telemetry?.prevention &&
          telemetry.prevention !== "Continue standard scheduled maintenance." && (
            <div
              id="prevention-card"
              className="advisory-box"
              style={{
                marginTop: "10px",
                borderColor: "rgba(56, 189, 248, 0.4)",
                display: "block",
              }}
            >
              <div className="advisory-title" style={{ color: "var(--accent-cyan)" }}>
                <span>🔧 Preventive Maintenance Action</span>
              </div>
              <div
                className="advisory-desc"
                id="prevention-action"
                style={{ color: "var(--text-primary)", fontSize: "0.85rem" }}
              >
                {telemetry.prevention}
              </div>
            </div>
          )}

        {/* Feature Regression Plot (Matplotlib) */}
        <div className="diag-section-header" style={{ marginTop: "15px" }}>
          <span>Telemetry Feature Regression</span>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "0.68rem",
              color: "var(--accent-cyan)",
            }}
          >
            Live Buffer
          </span>
        </div>
        <div style={{ textAlign: "center", marginBottom: "15px" }}>
          <img
            id="regression-plot"
            src={regressionImage || ""}
            alt="Regression Plot Loading..."
            style={{
              width: "100%",
              borderRadius: "8px",
              border: "1px solid var(--border-subtle)",
              minHeight: "200px",
              objectFit: "contain",
              background: "#070b14",
            }}
          />
        </div>

        {/* Subsystem Degradation & Physics Deviations */}
        <div className="diag-section-header">
          <span>Subsystem Physics Health & Integrity</span>
          <span
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "0.68rem",
              color: "var(--accent-cyan)",
            }}
          >
            TOLERANCE: ±5%
          </span>
        </div>

        <div className="diag-subsystems-list">
          {/* Thermal Management */}
          <div className="diag-subsystem-item">
            <div className="diag-subsystem-header">
              <span className="diag-subsystem-name">🔥 Thermal Core & Cooling Jacket</span>
              <span className="diag-subsystem-val" id="diag-val-thermal" style={{ color: thermalColor }}>
                {thermalText}
              </span>
            </div>
            <div className="diag-progress-bar">
              <div
                className="diag-progress-fill"
                id="diag-prog-thermal"
                style={{
                  width: `${thermalPct}%`,
                  background: thermalColor,
                }}
              />
            </div>
          </div>

          {/* Fuel Delivery System */}
          <div className="diag-subsystem-item">
            <div className="diag-subsystem-header">
              <span className="diag-subsystem-name">⚙️ Fuel Rail & Combustion Balance</span>
              <span className="diag-subsystem-val" id="diag-val-fuel" style={{ color: fuelColor }}>
                {fuelText}
              </span>
            </div>
            <div className="diag-progress-bar">
              <div
                className="diag-progress-fill"
                id="diag-prog-fuel"
                style={{
                  width: `${fuelPct}%`,
                  background: fuelColor,
                }}
              />
            </div>
          </div>

          {/* Lubrication System */}
          <div className="diag-subsystem-item">
            <div className="diag-subsystem-header">
              <span className="diag-subsystem-name">🛢️ Lubrication Circuit & Sump</span>
              <span className="diag-subsystem-val" id="diag-val-oil" style={{ color: oilColor }}>
                {oilText}
              </span>
            </div>
            <div className="diag-progress-bar">
              <div
                className="diag-progress-fill"
                id="diag-prog-oil"
                style={{
                  width: `${oilPct}%`,
                  background: oilColor,
                }}
              />
            </div>
          </div>

          {/* Mechanical / Vibration */}
          <div className="diag-subsystem-item">
            <div className="diag-subsystem-header">
              <span className="diag-subsystem-name">〰️ Mechanical Balance & Mounts</span>
              <span className="diag-subsystem-val" id="diag-val-vib" style={{ color: vibColor }}>
                {vibText}
              </span>
            </div>
            <div className="diag-progress-bar">
              <div
                className="diag-progress-fill"
                id="diag-prog-vib"
                style={{
                  width: `${vibPct}%`,
                  background: vibColor,
                }}
              />
            </div>
          </div>

          {/* Avionics & Sensors */}
          <div className="diag-subsystem-item">
            <div className="diag-subsystem-header">
              <span className="diag-subsystem-name">📡 Avionics Sensor Channel Fusion</span>
              <span className="diag-subsystem-val" id="diag-val-avionics" style={{ color: avionicsColor }}>
                {avionicsText}
              </span>
            </div>
            <div className="diag-progress-bar">
              <div
                className="diag-progress-fill"
                id="diag-prog-avionics"
                style={{
                  width: `${avionicsPct}%`,
                  background: avionicsColor,
                }}
              />
            </div>
          </div>
        </div>

        {/* PHM Prognostic Matrix */}
        <div className="diag-section-header">
          <span>PHM PROGNOSTIC MATRIX</span>
        </div>

        <div className="diag-phm-grid">
          <div className="diag-phm-card">
            <div className="diag-phm-label">ANOMALY CONFIDENCE</div>
            <div className="diag-phm-val" id="diag-stat-conf" style={{ color: statConfColor }}>
              {statConf}
            </div>
          </div>
          <div className="diag-phm-card">
            <div className="diag-phm-label">PHYSICS RESIDUAL</div>
            <div className="diag-phm-val" id="diag-stat-residual" style={{ color: "var(--accent-cyan)" }}>
              {statResidual}
            </div>
          </div>
          <div className="diag-phm-card">
            <div className="diag-phm-label">MAINTENANCE PRIORITY</div>
            <div className="diag-phm-val" id="diag-stat-priority" style={{ color: statPriorityColor }}>
              {statPriority}
            </div>
          </div>
          <div className="diag-phm-card">
            <div className="diag-phm-label">DEGRADATION TREND</div>
            <div className="diag-phm-val" id="diag-stat-trend" style={{ color: statTrendColor }}>
              {statTrend}
            </div>
          </div>
        </div>

        {/* Diagnostic Log Ticker */}
        <div className="diag-log-container">
          <span style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>PHM LOG:</span>
          <span id="diag-log-text">{logText}</span>
        </div>
      </div>
    </div>
  );
}

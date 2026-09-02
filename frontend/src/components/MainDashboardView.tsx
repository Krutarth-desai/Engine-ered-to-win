"use client";

import React from "react";
import { UnifiedTelemetryPayload, SensorItem } from "../types/telemetry";
import DigitalTwinCenterpiece from "./DigitalTwinCenterpiece";
import { NavView } from "./Sidebar";

interface MainDashboardViewProps {
  payload: UnifiedTelemetryPayload;
  activeScenario: string;
  onInjectScenario: (scenario: string) => void;
  onNavigate: (view: NavView) => void;
}

export default function MainDashboardView({
  payload,
  activeScenario,
  onInjectScenario,
  onNavigate,
}: MainDashboardViewProps) {
  const safeHealth = Math.min(100, Math.max(0, Math.round(payload.health_index ?? 96)));
  const currentRul = Math.round(payload.prognostics?.predicted_rul || 117);
  const trend = payload.prognostics?.degradation_trend || "Stable";
  const riskLevel = payload.risk?.level || "LOW";
  const anomalyState = payload.risk?.anomaly || "NORMAL";
  const actionText = payload.risk?.action || "Nominal Cruise Profile - All Systems Normal";

  // Active top alert (most recent high-priority alert)
  const activeAlert = payload.alerts && payload.alerts.length > 0 ? payload.alerts[0] : null;

  const sensors: SensorItem[] = payload.sensor_list || [];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ALERT":
        return "#ef4444";
      case "CAUTION":
        return "#f59e0b";
      case "NORMAL":
      default:
        return "#10b981";
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "#ef4444";
      case "HIGH":
        return "#f97316";
      case "MEDIUM":
        return "#f59e0b";
      case "LOW":
      default:
        return "#10b981";
    }
  };

  return (
    <div className="main-dashboard-container">
      {/* 1. TOP KPI SUMMARY ROW */}
      <div className="dashboard-kpi-row">
        {/* Card 1: Health Index */}
        <div className="kpi-card kpi-health">
          <div className="kpi-header">
            <span className="kpi-label"><strong>HEALTH INDEX</strong></span>
            <span className="kpi-icon">PHM</span>
          </div>
          <div className="kpi-body">
            <div className="kpi-main-val">
              <span className="kpi-big-num" style={{ color: safeHealth > 75 ? "#10b981" : safeHealth > 45 ? "#f59e0b" : "#ef4444" }}>
                {safeHealth}
              </span>
              <span className="kpi-denom">/ 100</span>
            </div>
            <div className="kpi-subtext">
              {safeHealth >= 80 ? "Nominal Operating Envelope" : safeHealth >= 50 ? "Moderate Degradation Detected" : "Critical Component Stress"}
            </div>
          </div>
        </div>

        {/* Card 2: Anomaly / Risk Status */}
        <div
          className="kpi-card kpi-risk clickable"
          onClick={() => onNavigate("diagnostics")}
          title="Click to view full Diagnostics analysis"
        >
          <div className="kpi-header">
            <span className="kpi-label"><strong>ANOMALY &amp; RISK</strong></span>
            <span className="kpi-link-hint">DETAILS →</span>
          </div>
          <div className="kpi-body">
            <div className="risk-dual-readout">
              <div className="risk-item">
                <span className="risk-tag">ANOMALY:</span>
                <span className={`risk-val status-${anomalyState.toLowerCase()}`}>
                  {anomalyState}
                </span>
              </div>
              <div className="risk-item">
                <span className="risk-tag">RISK LEVEL:</span>
                <span className="risk-val" style={{ color: getRiskColor(riskLevel) }}>
                  {riskLevel}
                </span>
              </div>
            </div>
            <div className="kpi-subtext">Automated Multi-Sensor Cross Isolation</div>
          </div>
        </div>

        {/* Card 3: Basic RUL Summary (Clickable -> RUL & Prognostics) */}
        <div
          className="kpi-card kpi-rul clickable"
          onClick={() => onNavigate("rul")}
          title="Click to view detailed RUL & Prognostics page"
        >
          <div className="kpi-header">
            <span className="kpi-label"><strong>REMAINING USEFUL LIFE</strong></span>
            <span className="kpi-link-hint">PROGNOSTICS →</span>
          </div>
          <div className="kpi-body">
            <div className="kpi-main-val">
              <span className="kpi-big-num text-cyan">{currentRul}</span>
              <span className="kpi-unit">CYCLES</span>
            </div>
            <div className="rul-trend-row">
              <span className="rul-trend-badge">
                {trend === "Accelerating" ? "ACCELERATING" : `RATE: ${trend.toUpperCase()}`}
              </span>
              <span className="rul-time-hint">≈ {payload.prognostics?.remaining_time_str || "01:57:32"}</span>
            </div>
          </div>
        </div>

        {/* Card 4: Current Recommendation / Action (Clickable -> Maintenance) */}
        <div
          className="kpi-card kpi-action clickable"
          onClick={() => onNavigate("maintenance")}
          title="Click to view Maintenance workflows"
        >
          <div className="kpi-header">
            <span className="kpi-label"><strong>ACTION RECOMMENDATION</strong></span>
            <span className="kpi-link-hint">MAINTENANCE →</span>
          </div>
          <div className="kpi-body">
            <div className="action-highlight-box">
              <span className="action-title-text"><strong>{actionText}</strong></span>
            </div>
            <div className="kpi-subtext">
              {riskLevel === "CRITICAL" || riskLevel === "HIGH"
                ? "Immediate pilot intervention recommended"
                : "Continuous telemetry baseline nominal"}
            </div>
          </div>
        </div>
      </div>

      {/* 2. CENTER: ENGINE DIGITAL TWIN VISUALIZATION */}
      <div className="dashboard-center-engine">
        <DigitalTwinCenterpiece
          telemetry={{
            ...payload,
            rpm: payload.sensors?.rpm?.value ?? payload.rpm ?? 2450,
            cht_c: payload.sensors?.cht?.value ?? payload.cht_c ?? 142.0,
            egt_c: payload.sensors?.egt?.value ?? payload.egt_c ?? 615.0,
            oil_pressure_bar: payload.sensors?.oil_pressure?.value
              ? payload.sensors.oil_pressure.value / 14.5038
              : (payload.oil_pressure_bar ?? 4.7),
            oil_temperature_c: payload.sensors?.oil_temperature?.value ?? payload.oil_temperature_c ?? 92.0,
            fuel_flow_lh: payload.sensors?.fuel_flow?.value ?? payload.fuel_flow_lh ?? 17.6,
            vibration_g: payload.sensors?.vibration?.value ?? payload.vibration_g ?? 1.42,
            health_index: safeHealth,
            fault_label: payload.fault_label ?? activeScenario,
          }}
          activeScenario={activeScenario}
          onInjectScenario={onInjectScenario}
        />
      </div>

      {/* 3. BELOW / SIDE: 9 LIVE ENGINE SENSORS COMPACT GRID */}
      <div className="dashboard-sensors-section">
        <div className="section-header-row">
          <div className="section-title">
            <strong>9-CHANNEL LIVE SENSORS (OPERATIONAL HUD)</strong>
          </div>
          <button
            className="view-more-btn"
            onClick={() => onNavigate("telemetry")}
          >
            VIEW FULL TELEMETRY &amp; TIME-SERIES →
          </button>
        </div>

        <div className="compact-sensors-grid">
          {sensors.map((sensor) => {
            const statusColor = getStatusColor(sensor.status);
            return (
              <div
                key={sensor.key}
                className={`compact-sensor-card status-${sensor.status.toLowerCase()}`}
                onClick={() => onNavigate("telemetry")}
                title={`Click to view detailed ${sensor.name} telemetry`}
              >
                <div className="card-header-line">
                  <span className="compact-sensor-name"><strong>{sensor.name}</strong></span>
                  <span
                    className="compact-sensor-dot"
                    style={{ backgroundColor: statusColor, boxShadow: `0 0 6px ${statusColor}` }}
                  />
                </div>
                <div className="card-value-line">
                  <span className="compact-sensor-val" style={{ color: statusColor }}>
                    {typeof sensor.value === "number" ? sensor.value.toLocaleString() : sensor.value}
                  </span>
                  <span className="compact-sensor-unit">{sensor.unit}</span>
                </div>
                <div className="compact-progress-track">
                  <div
                    className="compact-progress-fill"
                    style={{
                      width: `${Math.min(100, Math.max(0, sensor.progressPct))}%`,
                      backgroundColor: statusColor,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4. BOTTOM: ACTIVE ALERT / IMPORTANT EVENT */}
      {activeAlert && (
        <div
          className={`dashboard-active-alert-bar ${
            activeAlert.level === "ALERT"
              ? "alert-bar-crit"
              : activeAlert.level === "CAUTION"
              ? "alert-bar-warn"
              : "alert-bar-nom"
          }`}
          onClick={() => onNavigate("alerts")}
          title="Click to open full Alerts log"
        >
          <div className="alert-bar-left">
            <span className="alert-bar-level-tag">
              [{activeAlert.level}]
            </span>
            <div className="alert-bar-content">
              <div className="alert-bar-title">
                <strong>{activeAlert.title}</strong>
                <span className="alert-bar-time">{activeAlert.time_ago}</span>
              </div>
              <div className="alert-bar-msg">{activeAlert.message}</div>
            </div>
          </div>
          <button className="alert-bar-action-btn">
            VIEW ALL ALERTS ({payload.alerts.length}) →
          </button>
        </div>
      )}
    </div>
  );
}

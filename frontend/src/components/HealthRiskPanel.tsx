"use client";

import React from "react";
import { RiskData } from "../types/telemetry";

interface HealthRiskPanelProps {
  healthIndex: number;
  risk: RiskData;
}

export default function HealthRiskPanel({ healthIndex, risk }: HealthRiskPanelProps) {
  const safeHealth = Math.min(100, Math.max(0, Math.round(healthIndex)));

  // SVG Circular progress math
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (safeHealth / 100) * circumference;

  let healthColor = "#10b981"; // Green
  let degradationState = "NOMINAL";
  if (safeHealth < 40) {
    healthColor = "#ef4444"; // Red
    degradationState = "SEVERE";
  } else if (safeHealth < 75) {
    healthColor = "#f59e0b"; // Yellow/Amber
    degradationState = "MODERATE";
  }

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return { color: "#ef4444", bg: "rgba(239, 68, 68, 0.15)", border: "rgba(239, 68, 68, 0.5)" };
      case "HIGH":
        return { color: "#f97316", bg: "rgba(249, 115, 22, 0.15)", border: "rgba(249, 115, 22, 0.5)" };
      case "MEDIUM":
        return { color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)", border: "rgba(245, 158, 11, 0.5)" };
      case "LOW":
      default:
        return { color: "#10b981", bg: "rgba(16, 185, 129, 0.15)", border: "rgba(16, 185, 129, 0.5)" };
    }
  };

  const riskStyle = getRiskBadgeColor(risk.level);

  return (
    <div className="panel health-risk-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>HEALTH &amp; RISK ENGINE</strong>
        </div>
        <div
          className="risk-indicator-pill"
          style={{
            color: riskStyle.color,
            backgroundColor: riskStyle.bg,
            borderColor: riskStyle.border,
          }}
        >
          <strong>{risk.level} RISK</strong>
        </div>
      </div>

      <div className="health-circular-section">
        {/* SVG Circular Health Meter */}
        <div className="circular-meter-wrap">
          <svg viewBox="0 0 140 140" className="circular-svg">
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="10"
            />
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke={healthColor}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              transform="rotate(-90 70 70)"
              style={{
                transition: "stroke-dashoffset 0.8s ease, stroke 0.4s ease",
                filter: `drop-shadow(0 0 6px ${healthColor}60)`,
              }}
            />
          </svg>
          <div className="circular-readout">
            <span className="circular-score" style={{ color: healthColor }}>
              {safeHealth}
            </span>
            <span className="circular-denom">/ 100</span>
          </div>
        </div>

        <div className="health-meta-col">
          <div className="health-stat-block">
            <span className="stat-label">DEGRADATION STATE</span>
            <span className="stat-value font-bold" style={{ color: healthColor }}>
              {degradationState}
            </span>
          </div>
          <div className="health-stat-block">
            <span className="stat-label">ANOMALY STATE</span>
            <span className={`stat-value status-${risk.anomaly.toLowerCase()}`}>
              {risk.anomaly}
            </span>
          </div>
        </div>
      </div>

      {/* Decision Engine Recommended Action Box */}
      <div className="decision-action-box">
        <div className="decision-header">
          <span className="decision-label"><strong>RECOMMENDED ACTION</strong></span>
        </div>
        <div className="decision-text" id="decision-action-text">
          {risk.action}
        </div>
      </div>
    </div>
  );
}

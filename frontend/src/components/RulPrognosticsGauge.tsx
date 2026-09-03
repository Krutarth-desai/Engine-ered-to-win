"use client";

import React from "react";
import { PrognosticsData } from "../types/telemetry";

interface RulPrognosticsGaugeProps {
  prognostics: PrognosticsData;
}

export default function RulPrognosticsGauge({ prognostics }: RulPrognosticsGaugeProps) {
  const maxLife = prognostics.max_useful_life || 250;
  const currentRul = Math.max(0, prognostics.predicted_rul || 0);
  const rulPct = Math.min(100, Math.max(0, (currentRul / maxLife) * 100));

  // Determine current zone
  let zoneColor = "#10b981";
  let zoneLabel = "HEALTHY";
  if (currentRul < 30) {
    zoneColor = "#ef4444";
    zoneLabel = "CRITICAL";
  } else if (currentRul < 75) {
    zoneColor = "#f97316";
    zoneLabel = "HIGH RISK";
  } else if (currentRul < 130) {
    zoneColor = "#f59e0b";
    zoneLabel = "DEGRADING";
  }

  const trendValue = prognostics.degradation_trend || "Stable";
  const trendColor =
    trendValue === "Accelerating"
      ? "#ef4444"
      : trendValue === "Decelerating"
      ? "#f59e0b"
      : "#10b981";

  return (
    <div className="panel rul-centerpiece-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>REMAINING USEFUL LIFE (RUL) — LSTM PROGNOSTICS</strong>
        </div>
        <div
          className="zone-pill"
          style={{
            borderColor: `${zoneColor}60`,
            color: zoneColor,
            background: `${zoneColor}15`,
          }}
        >
          <span
            className="status-dot"
            style={{
              background: zoneColor,
              boxShadow: `0 0 8px ${zoneColor}`,
            }}
          />
          <strong>{zoneLabel}</strong>
        </div>
      </div>

      {/* Hero RUL Readout + Overview in a clean 2-column layout */}
      <div className="rul-hero-overview-grid">
        {/* Left: Big RUL Number + Progress Bar */}
        <div className="rul-hero-card">
          <div className="rul-hero-number-row">
            <span className="rul-big-number" style={{ color: zoneColor }}>
              {Math.round(currentRul)}
            </span>
            <div className="rul-hero-meta">
              <span className="rul-big-unit">CYCLES</span>
              <span className="rul-big-unit-sub">REMAINING</span>
            </div>
          </div>

          {/* Linear Progress Bar */}
          <div className="rul-progress-track">
            <div
              className="rul-progress-fill"
              style={{
                width: `${rulPct}%`,
                background: `linear-gradient(90deg, #ef4444 0%, #f97316 20%, #f59e0b 45%, #10b981 75%)`,
                backgroundSize: "400% 100%",
                backgroundPosition: `${100 - rulPct}% 0`,
              }}
            />
            {/* Zone markers */}
            <div className="rul-progress-marker" style={{ left: "12%" }} />
            <div className="rul-progress-marker" style={{ left: "30%" }} />
            <div className="rul-progress-marker" style={{ left: "52%" }} />
          </div>

          {/* Zone Legend */}
          <div className="rul-zone-legend">
            <span className="zone-tag zone-red">0–30 CRITICAL</span>
            <span className="zone-tag zone-orange">30–75 HIGH RISK</span>
            <span className="zone-tag zone-yellow">75–130 DEGRADING</span>
            <span className="zone-tag zone-green">130–250 HEALTHY</span>
          </div>

          {/* Time remaining pill */}
          <div className="rul-time-pill">
            <span className="rul-time-icon">⏱</span>
            <span>
              EST. <strong>{prognostics.remaining_time_str}</strong> TIME
              REMAINING
            </span>
          </div>
        </div>

        {/* Right: RUL Overview Stats */}
        <div className="rul-overview-card">
          <div className="overview-header">
            <span className="overview-title">
              <strong>RUL OVERVIEW</strong>
            </span>
            <span className="overview-badge">LSTM INFERENCE</span>
          </div>

          <div className="overview-rows">
            <div className="overview-row">
              <span className="row-label">Current Cycle</span>
              <span className="row-val font-mono">
                {prognostics.current_cycle}
              </span>
            </div>
            <div className="overview-row">
              <span className="row-label">Maximum Useful Life</span>
              <span className="row-val font-mono">
                {prognostics.max_useful_life} cycles
              </span>
            </div>
            <div className="overview-row">
              <span className="row-label">RUL (Unclipped)</span>
              <span className="row-val font-mono text-cyan">
                {typeof prognostics.rul_unclipped === "number"
                  ? prognostics.rul_unclipped.toFixed(1)
                  : prognostics.rul_unclipped}{" "}
                cycles
              </span>
            </div>
            <div className="overview-row">
              <span className="row-label">RUL (Clipped)</span>
              <span className="row-val font-mono text-cyan">
                {typeof prognostics.rul_clipped === "number"
                  ? prognostics.rul_clipped.toFixed(1)
                  : prognostics.rul_clipped}{" "}
                cycles
              </span>
            </div>
            <div className="overview-row">
              <span className="row-label">Degradation Trend</span>
              <span className="row-val font-bold" style={{ color: trendColor }}>
                {trendValue}
              </span>
            </div>
            <div className="overview-row highlight-row">
              <span className="row-label">Prognostic Confidence</span>
              <span className="row-val text-green font-bold">
                {prognostics.confidence}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


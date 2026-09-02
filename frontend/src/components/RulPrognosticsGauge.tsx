"use client";

import React from "react";
import { PrognosticsData } from "../types/telemetry";

interface RulPrognosticsGaugeProps {
  prognostics: PrognosticsData;
}

export default function RulPrognosticsGauge({ prognostics }: RulPrognosticsGaugeProps) {
  const maxLife = prognostics.max_useful_life || 250;
  const currentRul = Math.max(0, prognostics.predicted_rul || 0);
  const rulRatio = Math.min(1.0, Math.max(0.0, currentRul / maxLife));

  // Determine current zone color
  let zoneColor = "#10b981"; // GREEN Healthy
  let zoneLabel = "HEALTHY";
  if (currentRul < 30) {
    zoneColor = "#ef4444"; // RED Critical
    zoneLabel = "CRITICAL";
  } else if (currentRul < 75) {
    zoneColor = "#f97316"; // ORANGE High Risk
    zoneLabel = "HIGH RISK";
  } else if (currentRul < 130) {
    zoneColor = "#f59e0b"; // YELLOW Degrading
    zoneLabel = "DEGRADING";
  }

  // Semi-circle SVG math (180 degree arc from left 0 to right 250)
  const radius = 88;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference * (1 - rulRatio);
  
  // Angle for needle/indicator: 0 deg points left (0 cycles), 180 deg points right (250 cycles)
  const rotationAngle = rulRatio * 180;

  return (
    <div className="panel rul-centerpiece-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>REMAINING USEFUL LIFE (RUL) — LSTM PROGNOSTICS</strong>
        </div>
        <div className="zone-pill" style={{ borderColor: `${zoneColor}60`, color: zoneColor, background: `${zoneColor}15` }}>
          <span className="status-dot" style={{ background: zoneColor, boxShadow: `0 0 8px ${zoneColor}` }} />
          <strong>{zoneLabel}</strong>
        </div>
      </div>

      <div className="rul-gauge-grid">
        {/* Left: Prominent Arc Gauge */}
        <div className="rul-gauge-col">
          <div className="rul-arc-wrapper">
            <svg viewBox="0 0 220 130" className="rul-arc-svg">
              <defs>
                <linearGradient id="rulArcTrack" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#ef4444" />
                  <stop offset="30%" stopColor="#f97316" />
                  <stop offset="60%" stopColor="#f59e0b" />
                  <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
                <filter id="rulGlow" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feComposite in="SourceGraphic" in2="blur" operator="over" />
                </filter>
              </defs>

              {/* Background Reference Arc */}
              <path
                d="M 22 110 A 88 88 0 0 1 198 110"
                fill="none"
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="14"
                strokeLinecap="round"
              />

              {/* Multi-Zone Base Arc */}
              <path
                d="M 22 110 A 88 88 0 0 1 198 110"
                fill="none"
                stroke="url(#rulArcTrack)"
                strokeWidth="14"
                strokeLinecap="round"
                opacity="0.35"
              />

              {/* Active Animated Value Arc */}
              <path
                d="M 22 110 A 88 88 0 0 1 198 110"
                fill="none"
                stroke={zoneColor}
                strokeWidth="14"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                filter="url(#rulGlow)"
                className="rul-progress-path"
              />

              {/* Needle Hub & Pointer */}
              <g transform={`translate(110, 110) rotate(${rotationAngle})`}>
                <line x1="0" y1="0" x2="-80" y2="0" stroke={zoneColor} strokeWidth="3" strokeLinecap="round" />
                <polygon points="-84,0 -76,-3.5 -76,3.5" fill={zoneColor} />
                <circle cx="0" cy="0" r="7" fill="#0f172a" stroke={zoneColor} strokeWidth="3" />
              </g>

              {/* Scale Ticks */}
              <text x="18" y="126" className="arc-tick-text">0</text>
              <text x="65" y="42" className="arc-tick-text">50</text>
              <text x="110" y="20" className="arc-tick-text">125</text>
              <text x="195" y="126" className="arc-tick-text">250</text>
            </svg>

            {/* Central Impossible-to-Miss RUL readout */}
            <div className="rul-hero-readout">
              <div className="rul-number-wrap">
                <span className="rul-big-number" style={{ color: zoneColor }}>
                  {Math.round(currentRul)}
                </span>
                <span className="rul-big-unit">CYCLES</span>
              </div>
              <div className="rul-sub-remaining">
                <span className="time-text">EST. {prognostics.remaining_time_str} TIME REMAINING</span>
              </div>
            </div>
          </div>

          {/* Color Zone Legend Bar */}
          <div className="rul-zone-legend">
            <span className="zone-tag zone-red">0-30 CRITICAL</span>
            <span className="zone-tag zone-orange">30-75 HIGH RISK</span>
            <span className="zone-tag zone-yellow">75-130 DEGRADING</span>
            <span className="zone-tag zone-green">130-250 HEALTHY</span>
          </div>
        </div>

        {/* Right: RUL Overview Card */}
        <div className="rul-overview-card">
          <div className="overview-header">
            <span className="overview-title"><strong>RUL OVERVIEW</strong></span>
            <span className="overview-badge">LSTM INFERENCE</span>
          </div>

          <div className="overview-rows">
            <div className="overview-row">
              <span className="row-label">Current Cycle</span>
              <span className="row-val font-mono">{prognostics.current_cycle}</span>
            </div>
            <div className="overview-row">
              <span className="row-label">Maximum Useful Life</span>
              <span className="row-val font-mono">{prognostics.max_useful_life} cycles</span>
            </div>
            <div className="overview-row">
              <span className="row-label">RUL (Unclipped)</span>
              <span className="row-val font-mono text-cyan">{prognostics.rul_unclipped} cycles</span>
            </div>
            <div className="overview-row">
              <span className="row-label">RUL (Clipped)</span>
              <span className="row-val font-mono text-cyan">{prognostics.rul_clipped} cycles</span>
            </div>
            <div className="overview-row">
              <span className="row-label">Degradation Trend</span>
              <span className={`row-val trend-${prognostics.degradation_trend.toLowerCase()}`}>
                {prognostics.degradation_trend === "Accelerating" ? "Accelerating" : prognostics.degradation_trend}
              </span>
            </div>
            <div className="overview-row highlight-row">
              <span className="row-label">Prognostic Confidence</span>
              <span className="row-val text-green font-bold">{prognostics.confidence}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

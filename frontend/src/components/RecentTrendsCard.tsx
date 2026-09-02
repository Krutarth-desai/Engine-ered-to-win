"use client";

import React from "react";
import { TrendHistoryPoint } from "../types/telemetry";

interface RecentTrendsCardProps {
  points: TrendHistoryPoint[];
  deltas: {
    egt_delta: number;
    oil_pressure_delta: number;
    vibration_delta: number;
    health_delta: number;
  };
}

export default function RecentTrendsCard({ points, deltas }: RecentTrendsCardProps) {
  // Helper to generate SVG sparkline path from array of numbers
  const generateSparklinePath = (values: number[], width = 120, height = 32) => {
    if (!values || values.length < 2) return "";
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    return values
      .map((val, idx) => {
        const x = (idx / (values.length - 1)) * width;
        const y = height - ((val - min) / range) * (height - 6) - 3;
        return `${idx === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(" ");
  };

  const egtVals = points.map((p) => p.egt);
  const oilPVals = points.map((p) => p.oil_pressure);
  const vibVals = points.map((p) => p.vibration);
  const healthVals = points.map((p) => p.health_index);

  const formatDelta = (val: number, unit = "") => {
    const sign = val > 0 ? "↑ +" : val < 0 ? "↓ " : "→ ";
    return `${sign}${Math.abs(val)}${unit ? " " + unit : ""}`;
  };

  return (
    <div className="panel recent-trends-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>RECENT 30-CYCLE TREND (LSTM WINDOW)</strong>
        </div>
        <span className="window-pill"><strong>30 CYCLES</strong></span>
      </div>

      <div className="trends-grid">
        {/* EGT Sparkline */}
        <div className="trend-tile">
          <div className="trend-meta">
            <span className="trend-name">EGT</span>
            <span className="trend-curr">
              {egtVals.length > 0 ? egtVals[egtVals.length - 1] : 615} °C
            </span>
          </div>
          <svg viewBox="0 0 120 32" className="sparkline-svg">
            <path
              d={generateSparklinePath(egtVals)}
              fill="none"
              stroke="#f59e0b"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <div className="trend-delta text-amber">
            {formatDelta(deltas.egt_delta, "°C")}
          </div>
        </div>

        {/* Oil Pressure Sparkline */}
        <div className="trend-tile">
          <div className="trend-meta">
            <span className="trend-name">Oil Pressure</span>
            <span className="trend-curr">
              {oilPVals.length > 0 ? oilPVals[oilPVals.length - 1] : 68} psi
            </span>
          </div>
          <svg viewBox="0 0 120 32" className="sparkline-svg">
            <path
              d={generateSparklinePath(oilPVals)}
              fill="none"
              stroke="#38bdf8"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <div className="trend-delta text-cyan">
            {formatDelta(deltas.oil_pressure_delta, "psi")}
          </div>
        </div>

        {/* Vibration Sparkline */}
        <div className="trend-tile">
          <div className="trend-meta">
            <span className="trend-name">Vibration</span>
            <span className="trend-curr">
              {vibVals.length > 0 ? vibVals[vibVals.length - 1] : 1.42} g
            </span>
          </div>
          <svg viewBox="0 0 120 32" className="sparkline-svg">
            <path
              d={generateSparklinePath(vibVals)}
              fill="none"
              stroke="#ec4899"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <div className="trend-delta text-pink">
            {formatDelta(deltas.vibration_delta, "g")}
          </div>
        </div>

        {/* Health Index Sparkline */}
        <div className="trend-tile">
          <div className="trend-meta">
            <span className="trend-name">Health Index</span>
            <span className="trend-curr">
              {healthVals.length > 0 ? Math.round(healthVals[healthVals.length - 1]) : 72} / 100
            </span>
          </div>
          <svg viewBox="0 0 120 32" className="sparkline-svg">
            <path
              d={generateSparklinePath(healthVals)}
              fill="none"
              stroke="#10b981"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
          <div className="trend-delta text-green">
            {formatDelta(deltas.health_delta, "%")}
          </div>
        </div>
      </div>
    </div>
  );
}

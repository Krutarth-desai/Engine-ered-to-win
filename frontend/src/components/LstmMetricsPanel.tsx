"use client";

import React from "react";
import { PrognosticsData } from "../types/telemetry";

interface LstmMetricsPanelProps {
  prognostics: PrognosticsData;
}

export default function LstmMetricsPanel({ prognostics }: LstmMetricsPanelProps) {
  return (
    <div className="panel lstm-metrics-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-icon">🧠</span>
          LSTM PROGNOSTIC METRICS
        </div>
        <span className="model-chip">CMAPSS FD001</span>
      </div>

      <div className="lstm-grid-2x3">
        {/* Row 1: Predicted vs Actual RUL */}
        <div className="metric-box">
          <span className="metric-box-label">PREDICTED RUL</span>
          <span className="metric-box-val text-cyan font-mono">
            {prognostics.predicted_rul.toFixed(1)}
          </span>
          <span className="metric-box-sub">Current LSTM cycle output</span>
        </div>

        <div className="metric-box">
          <span className="metric-box-label">ACTUAL RUL</span>
          <span className="metric-box-val text-green font-mono">
            {prognostics.actual_rul.toFixed(1)}
          </span>
          <span className="metric-box-sub">Ground truth reference</span>
        </div>

        {/* Row 2: Current Abs Error vs Model MAE */}
        <div className="metric-box">
          <span className="metric-box-label">ABS ERROR</span>
          <span className="metric-box-val text-yellow font-mono">
            {prognostics.abs_error.toFixed(1)}
          </span>
          <span className="metric-box-sub">|Predicted - Actual|</span>
        </div>

        <div className="metric-box">
          <span className="metric-box-label">MODEL MAE</span>
          <span className="metric-box-val text-blue font-mono">
            {prognostics.model_mae.toFixed(2)}
          </span>
          <span className="metric-box-sub">Evaluation set benchmark</span>
        </div>

        {/* Row 3: Operational Window vs Ingestion Sensors */}
        <div className="metric-box">
          <span className="metric-box-label">WINDOW</span>
          <span className="metric-box-val font-mono">
            {prognostics.window_size} cycles
          </span>
          <span className="metric-box-sub">Temporal sequence memory</span>
        </div>

        <div className="metric-box">
          <span className="metric-box-label">SENSORS</span>
          <span className="metric-box-val font-mono">
            {prognostics.sensor_count} features
          </span>
          <span className="metric-box-sub">Filtered physical channels</span>
        </div>
      </div>
    </div>
  );
}

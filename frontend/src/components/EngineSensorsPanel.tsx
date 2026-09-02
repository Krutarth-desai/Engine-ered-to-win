"use client";

import React from "react";
import { SensorItem } from "../types/telemetry";

interface EngineSensorsPanelProps {
  sensors: SensorItem[];
}

export default function EngineSensorsPanel({ sensors }: EngineSensorsPanelProps) {
  const getStatusColor = (status: "NORMAL" | "CAUTION" | "ALERT") => {
    switch (status) {
      case "ALERT":
        return "#ef4444"; // Red
      case "CAUTION":
        return "#f59e0b"; // Yellow/Amber
      case "NORMAL":
      default:
        return "#10b981"; // Emerald Green
    }
  };

  const getStatusDotClass = (status: "NORMAL" | "CAUTION" | "ALERT") => {
    switch (status) {
      case "ALERT":
        return "sensor-dot alert";
      case "CAUTION":
        return "sensor-dot caution";
      case "NORMAL":
      default:
        return "sensor-dot normal";
    }
  };

  const getTrendIcon = (trend: "UP" | "DOWN" | "STABLE") => {
    switch (trend) {
      case "UP":
        return "↑";
      case "DOWN":
        return "↓";
      case "STABLE":
      default:
        return "→";
    }
  };

  return (
    <div className="panel engine-sensors-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>ENGINE SENSORS (LIVE)</strong>
        </div>
        <span className="badge-live-pulse"><strong>REAL-TIME</strong></span>
      </div>

      <div className="sensors-list">
        {sensors.map((sensor) => {
          const statusColor = getStatusColor(sensor.status);
          const trendIcon = getTrendIcon(sensor.trend);

          return (
            <div key={sensor.key} className={`sensor-row status-${sensor.status.toLowerCase()}`}>
              {/* Top metadata line: Name & Value/Unit */}
              <div className="sensor-top-row">
                <div className="sensor-name-wrap">
                  <span className={getStatusDotClass(sensor.status)}>●</span>
                  <span className="sensor-label"><strong>{sensor.name}</strong></span>
                </div>
                <div className="sensor-value-wrap">
                  <span className="sensor-trend" title={`Trend: ${sensor.trend}`}>
                    {trendIcon}
                  </span>
                  <span className="sensor-value" style={{ color: statusColor }}>
                    {typeof sensor.value === "number" ? sensor.value.toLocaleString() : sensor.value}
                  </span>
                  <span className="sensor-unit">{sensor.unit}</span>
                </div>
              </div>

              {/* Progress bar visual indicator */}
              <div className="sensor-progress-track">
                <div
                  className="sensor-progress-fill"
                  style={{
                    width: `${Math.min(100, Math.max(0, sensor.progressPct))}%`,
                    backgroundColor: statusColor,
                    boxShadow: `0 0 8px ${statusColor}40`,
                  }}
                />
              </div>

              {/* Range context footer */}
              <div className="sensor-envelope-footer">
                <span>{sensor.min}</span>
                <span className="sensor-envelope-tag">
                  {sensor.status === "NORMAL" ? "NOMINAL" : sensor.status}
                </span>
                <span>{sensor.max} {sensor.unit}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

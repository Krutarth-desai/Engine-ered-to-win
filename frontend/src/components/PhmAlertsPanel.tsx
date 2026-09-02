"use client";

import React from "react";
import { PhmAlertItem } from "../types/telemetry";

interface PhmAlertsPanelProps {
  alerts: PhmAlertItem[];
}

export default function PhmAlertsPanel({ alerts }: PhmAlertsPanelProps) {
  const getAlertIcon = (level: string) => {
    switch (level) {
      case "ALERT":
        return "🚨";
      case "CAUTION":
        return "⚠️";
      case "INFO":
        return "ⓘ";
      case "NORMAL":
      default:
        return "✓";
    }
  };

  const getAlertClass = (level: string) => {
    switch (level) {
      case "ALERT":
        return "alert-card alert-critical";
      case "CAUTION":
        return "alert-card alert-caution";
      case "INFO":
        return "alert-card alert-info";
      case "NORMAL":
      default:
        return "alert-card alert-nominal";
    }
  };

  return (
    <div className="panel phm-alerts-panel">
      <div className="panel-header">
        <div className="panel-title">
          <span className="panel-icon">🔔</span>
          PHM ALERTS &amp; DIAGNOSTICS
        </div>
        <span className="active-alerts-count">
          {alerts.filter((a) => a.level === "ALERT" || a.level === "CAUTION").length} ACTIVE
        </span>
      </div>

      <div className="alerts-feed-container">
        {alerts.length === 0 ? (
          <div className="empty-alerts">✓ All operational parameters nominal. No active alerts.</div>
        ) : (
          alerts.map((alert) => (
            <div key={alert.id} className={getAlertClass(alert.level)}>
              <div className="alert-badge-col">
                <span className="alert-symbol">{getAlertIcon(alert.level)}</span>
              </div>
              <div className="alert-content-col">
                <div className="alert-header-row">
                  <span className="alert-title">{alert.title}</span>
                  <span className="alert-time-tag">{alert.time_ago}</span>
                </div>
                <div className="alert-message-text">{alert.message}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

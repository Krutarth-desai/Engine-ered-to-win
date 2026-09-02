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
        return "[ALT]";
      case "CAUTION":
        return "[CAU]";
      case "INFO":
        return "[INF]";
      case "NORMAL":
      default:
        return "[OK]";
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
          <strong>PHM ALERTS &amp; DIAGNOSTICS</strong>
        </div>
        <span className="active-alerts-count">
          <strong>{alerts.filter((a) => a.level === "ALERT" || a.level === "CAUTION").length} ACTIVE</strong>
        </span>
      </div>

      <div className="alerts-feed-container">
        {alerts.length === 0 ? (
          <div className="empty-alerts">[OK] All operational parameters nominal. No active alerts.</div>
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

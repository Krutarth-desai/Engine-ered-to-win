"use client";

import React, { useState } from "react";
import { PhmAlertItem } from "../types/telemetry";
import ScenarioBar from "./ScenarioBar";

interface AlertsViewProps {
  alerts: PhmAlertItem[];
  activeScenario: string;
  onInjectScenario: (scenario: string) => void;
}

export default function AlertsView({
  alerts,
  activeScenario,
  onInjectScenario,
}: AlertsViewProps) {
  const [filter, setFilter] = useState<string>("ALL");
  const [acknowledgedIds, setAcknowledgedIds] = useState<Set<string>>(new Set());

  const handleToggleAck = (id: string) => {
    setAcknowledgedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const filteredAlerts = alerts.filter((a) => {
    if (filter === "ALL") return true;
    return a.level === filter;
  });

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

  const getAlertCardClass = (level: string, isAck: boolean) => {
    let base = "alert-log-card";
    if (level === "ALERT") base += " alert-crit";
    else if (level === "CAUTION") base += " alert-warn";
    else if (level === "INFO") base += " alert-info";
    else base += " alert-nom";

    if (isAck) base += " acknowledged";
    return base;
  };

  return (
    <div className="view-container alerts-view">
      <div className="view-header-strip">
        <div>
          <h2 className="view-title"><strong>ACTIVE ALERTS &amp; CHRONOLOGICAL PHM LOG</strong></h2>
          <p className="view-subtitle">Full operational incident record, timestamped threshold violations, and telemetry event logs</p>
        </div>

        {/* Severity Filter Pills */}
        <div className="alert-filters-row">
          {["ALL", "ALERT", "CAUTION", "INFO", "NORMAL"].map((f) => (
            <button
              key={f}
              className={`filter-pill-btn ${filter === f ? "active" : ""}`}
              onClick={() => setFilter(f)}
            >
              <strong>{f}</strong>
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Scenario Injection Simulator */}
      <div className="alerts-simulator-card">
        <ScenarioBar
          activeScenario={activeScenario}
          onSelectScenario={onInjectScenario}
        />
      </div>

      {/* Alerts Feed List */}
      <div className="alerts-full-list">
        {filteredAlerts.length === 0 ? (
          <div className="empty-alerts-box">
            <span>[OK] No alerts found matching filter "{filter}". All telemetry nominal.</span>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isAck = acknowledgedIds.has(alert.id);
            return (
              <div key={alert.id} className={getAlertCardClass(alert.level, isAck)}>
                <div className="alert-symbol-col">
                  <span className="symbol-icon">{getAlertIcon(alert.level)}</span>
                </div>

                <div className="alert-details-col">
                  <div className="alert-meta-line">
                    <span className="alert-severity-pill"><strong>{alert.level}</strong></span>
                    <span className="alert-headline"><strong>{alert.title}</strong></span>
                    <span className="alert-timestamp-mono">
                      {new Date(alert.timestamp).toLocaleTimeString()} ({alert.time_ago})
                    </span>
                  </div>
                  <div className="alert-desc-line">{alert.message}</div>
                </div>

                <div className="alert-action-col">
                  <button
                    className={`ack-btn ${isAck ? "acked" : ""}`}
                    onClick={() => handleToggleAck(alert.id)}
                  >
                    {isAck ? "ACKNOWLEDGED" : "ACKNOWLEDGE"}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

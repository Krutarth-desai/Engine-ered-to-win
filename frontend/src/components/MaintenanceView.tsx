"use client";

import React from "react";
import { UnifiedTelemetryPayload } from "../types/telemetry";

interface MaintenanceViewProps {
  payload: UnifiedTelemetryPayload;
}

export default function MaintenanceView({ payload }: MaintenanceViewProps) {
  const riskLevel = payload.risk?.level || "LOW";
  const action = payload.risk?.action || "All engine systems and sensors are performing nominally. Continue planned cruise profile.";
  const guidance = payload.risk?.guidance;
  const health = Math.round(payload.health_index || 96);

  const getPriorityStyle = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return { color: "#ef4444", bg: "rgba(239, 68, 68, 0.15)", border: "#ef4444" };
      case "HIGH":
        return { color: "#f97316", bg: "rgba(249, 115, 22, 0.15)", border: "#f97316" };
      case "MEDIUM":
        return { color: "#f59e0b", bg: "rgba(245, 158, 11, 0.15)", border: "#f59e0b" };
      case "LOW":
      default:
        return { color: "#10b981", bg: "rgba(16, 185, 129, 0.15)", border: "#10b981" };
    }
  };

  const prio = getPriorityStyle(riskLevel);

  const checklist = [
    { item: "Cylinder Head & Barrel Temperature Harness", status: payload.sensors?.cht?.status || "NORMAL", action: "Verify CHT thermocouple seating & continuity" },
    { item: "High-Pressure Fuel Injection Rail & Filter", status: payload.sensors?.fuel_flow?.status || "NORMAL", action: "Check fuel line pressure & ultrasonic injector spray" },
    { item: "Lubrication Sump & Oil Scavenge Circuit", status: payload.sensors?.oil_pressure?.status || "NORMAL", action: "Inspect magnetic drain plug & oil filter element" },
    { item: "Dynafocal Engine Mounts & Crankcase Balance", status: payload.sensors?.vibration?.status || "NORMAL", action: "Torque engine bed bolts & inspect rubber isolators" },
    { item: "Avionics Power Bus & Voltage Regulators", status: payload.sensors?.bus_voltage?.status || "NORMAL", action: "Check 28V alternator belt tension & ground straps" },
  ];

  return (
    <div className="view-container maintenance-view">
      <div className="view-header-strip">
        <div>
          <h2 className="view-title"><strong>PREDICTIVE MAINTENANCE &amp; ACTION PROTOCOL</strong></h2>
          <p className="view-subtitle">Condition-based maintenance (CBM), component wear life thresholds, and field action procedures</p>
        </div>
        <div
          className="priority-badge"
          style={{ color: prio.color, backgroundColor: prio.bg, borderColor: prio.border }}
        >
          <strong>PRIORITY: {riskLevel}</strong>
        </div>
      </div>

      <div className="maintenance-grid">
        {/* Left Column: Immediate Operational Action Card */}
        <div className="maint-col-left">
          <div className="panel maint-action-hero">
            <div className="panel-header">
              <div className="panel-title">
                <strong>CURRENT PILOT / OPERATOR DIRECTIVE</strong>
              </div>
              <span className="status-pill"><strong>{riskLevel} RISK</strong></span>
            </div>

            <div className="maint-action-body">
              <div className="action-large-readout">
                <span className="action-hero-text"><strong>{action}</strong></span>
              </div>
              <p className="action-context">
                {guidance || `Automated recommendation generated based on cross-correlated physical telemetry, remaining useful life estimates (${Math.round(payload.prognostics?.predicted_rul || 117)} cycles), and current health index (${health}/100).`}
              </p>
            </div>
          </div>

          <div className="panel maint-protocols-card">
            <div className="panel-header">
              <div className="panel-title">
                <strong>PREVENTATIVE MAINTENANCE PROTOCOLS</strong>
              </div>
            </div>
            <div className="protocols-list">
              <div className="protocol-item">
                <span className="protocol-tag tag-thermal">THERMAL MITIGATION</span>
                <p className="protocol-desc">If CHT exceeds 165°C or EGT exceeds 680°C, enrich mixture to rich-of-peak and reduce continuous throttle below 70% to prevent detonation.</p>
              </div>
              <div className="protocol-item">
                <span className="protocol-tag tag-hydraulic">LUBRICATION PROTECT</span>
                <p className="protocol-desc">If oil pressure drops below 50 psi during high-G maneuvers, execute immediate level flight recovery and throttle back to cruise idle.</p>
              </div>
              <div className="protocol-item">
                <span className="protocol-tag tag-mechanical">VIBRATION DAMPENING</span>
                <p className="protocol-desc">Sustained vibration above 2.0 g indicates prop imbalance or bearing brinelling; schedule ground dynamic balance balancing within 5 flight hours.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Subsystem Maintenance Inspection Checklist */}
        <div className="maint-col-right">
          <div className="panel maint-checklist-card">
            <div className="panel-header">
              <div className="panel-title">
                <strong>SUBSYSTEM INSPECTION CHECKLIST</strong>
              </div>
              <span className="model-chip"><strong>5 CRITICAL NODES</strong></span>
            </div>

            <div className="checklist-items-wrap">
              {checklist.map((chk, i) => (
                <div key={i} className={`checklist-item status-${chk.status.toLowerCase()}`}>
                  <div className="chk-top-line">
                    <span className="chk-name"><strong>{chk.item}</strong></span>
                    <span className={`chk-badge status-${chk.status.toLowerCase()}`}>
                      {chk.status}
                    </span>
                  </div>
                  <div className="chk-action-line">{chk.action}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

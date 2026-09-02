"use client";

import React from "react";

interface HeaderProps {
  userEmail: string;
  isConnected: boolean;
  vehicleId?: string;
  missionId?: string;
  altitude?: number;
  throttle?: number;
  remainingTimeStr?: string;
  onLogout: () => void;
}

export default function Header({
  userEmail,
  isConnected,
  vehicleId = "UAV_ENG_001",
  missionId = "ISR_PATROL_27",
  altitude = 15000,
  throttle = 75,
  remainingTimeStr = "01:57:32",
  onLogout,
}: HeaderProps) {
  return (
    <header id="app-header" className="gcs-mission-header">
      {/* Left: Mission Brand */}
      <div className="brand">
        <div className="logo-badge"><span className="aerotwin-icon">▲</span> AEROTWIN</div>
        <div>
          <div className="brand-title"><strong>MALE UAV PISTON ENGINE DIGITAL TWIN</strong></div>
          <div className="brand-subtitle">GROUND CONTROL STATION &amp; PHM SUITE</div>
        </div>
      </div>

      {/* Center: Mission Operational Telemetry */}
      <div className="mission-center-bar">
        <div className="metric-chip">
          <span className="metric-label">VEHICLE</span>
          <span className="metric-value text-cyan">{vehicleId}</span>
        </div>
        <div className="metric-chip">
          <span className="metric-label">MISSION</span>
          <span className="metric-value text-blue">{missionId}</span>
        </div>
        <div className="metric-chip">
          <span className="metric-label">ALTITUDE</span>
          <span className="metric-value">{altitude.toLocaleString()} FT</span>
        </div>
        <div className="metric-chip">
          <span className="metric-label">THROTTLE</span>
          <span className="metric-value">{throttle}%</span>
        </div>
      </div>

      {/* Right: RUL Countdown & Status Badge */}
      <div className="mission-right-bar">
        <div className="remaining-time-badge" title="Estimated Mission Time Remaining based on LSTM RUL Cycles">
          <span className="time-icon">REM:</span>
          <div className="time-content">
            <span className="time-label">REMAINING TIME</span>
            <span className="time-digits" id="header-remaining-time">
              {remainingTimeStr}
            </span>
          </div>
        </div>

        <div
          id="conn-badge"
          className="status-pill"
          style={{
            borderColor: isConnected ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)",
            color: isConnected ? "#10b981" : "#ef4444",
          }}
        >
          <span className="status-dot"></span>
          <span id="conn-text">{isConnected ? "LIVE 1 Hz" : "RECONNECTING"}</span>
        </div>

        <div className="auth-user-info">
          <span className="auth-user-email" id="auth-user-email">
            {userEmail || "Operator"}
          </span>
          <button className="auth-logout-btn" id="auth-logout-btn" onClick={onLogout}>
            LOGOUT
          </button>
        </div>
      </div>
    </header>
  );
}

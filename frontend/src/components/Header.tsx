"use client";

import React from "react";

interface HeaderProps {
  userEmail: string;
  isConnected: boolean;
  isRulView: boolean;
  onToggleRulView: () => void;
  onLogout: () => void;
}

export default function Header({
  userEmail,
  isConnected,
  isRulView,
  onToggleRulView,
  onLogout,
}: HeaderProps) {
  return (
    <header id="app-header">
      <div className="brand">
        <div className="logo-badge">AEROTWIN</div>
        <div>
          <div className="brand-title">MALE UAV PISTON ENGINE DIGITAL TWIN</div>
          <div className="brand-subtitle">Ground Control Station Telemetry & PHM Suite</div>
        </div>
      </div>

      <div className="mission-status-bar">
        <div>
          <span className="metric-tag">VEHICLE:</span>{" "}
          <span className="metric-val" id="val-engine">
            ENG_001
          </span>
        </div>
        <div>
          <span className="metric-tag">MISSION:</span>{" "}
          <span className="metric-val" id="val-mission">
            LIVE_SIM_001
          </span>
        </div>
        <div>
          <span className="metric-tag">ALTITUDE:</span>{" "}
          <span className="metric-val" id="val-alt">
            15,000 FT
          </span>
        </div>
        <div>
          <span className="metric-tag">THROTTLE:</span>{" "}
          <span className="metric-val" id="val-throttle">
            75%
          </span>
        </div>
        <button
          className={`nav-rul-btn ${isRulView ? "active" : ""}`}
          id="btn-rul-view"
          onClick={onToggleRulView}
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 22h14" />
            <path d="M5 2h14" />
            <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22" />
            <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2" />
          </svg>
          REMAINING TIME
        </button>
        <div
          id="conn-badge"
          className="status-pill"
          style={{
            borderColor: isConnected ? "rgba(16, 185, 129, 0.3)" : "rgba(239, 68, 68, 0.3)",
            color: isConnected ? "#10b981" : "#ef4444",
          }}
        >
          <span className="status-dot"></span>
          <span id="conn-text">{isConnected ? "LIVE 1 Hz" : "RECONNECTING..."}</span>
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

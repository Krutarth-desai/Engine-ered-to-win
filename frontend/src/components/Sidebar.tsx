"use client";

import React, { useState } from "react";

export type NavView =
  | "dashboard"
  | "telemetry"
  | "diagnostics"
  | "rul"
  | "regression"
  | "maintenance"
  | "alerts";

interface NavItem {
  id: NavView;
  label: string;
  icon: string;
  tag?: string;
  badge?: number;
}

interface NavSection {
  heading: string;
  items: NavItem[];
}

interface SidebarProps {
  currentView: NavView;
  onSelectView: (view: NavView) => void;
  selectedEngine: string;
  onSelectEngine: (engine: string) => void;
  activeAlertCount: number;
}

export default function Sidebar({
  currentView,
  onSelectView,
  selectedEngine,
  onSelectEngine,
  activeAlertCount,
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navSections: NavSection[] = [
    {
      heading: "OVERVIEW",
      items: [
        { id: "dashboard" as NavView, label: "Dashboard", icon: "🎛️", tag: "LIVE" },
      ],
    },
    {
      heading: "MONITORING",
      items: [
        { id: "telemetry" as NavView, label: "Live Telemetry", icon: "⚡", tag: "9 CH" },
      ],
    },
    {
      heading: "ANALYSIS",
      items: [
        { id: "diagnostics" as NavView, label: "Diagnostics", icon: "🔬" },
        { id: "rul" as NavView, label: "RUL & Prognostics", icon: "⏱️" },
        { id: "regression" as NavView, label: "Regression & Trends", icon: "📈" },
      ],
    },
    {
      heading: "OPERATIONS",
      items: [
        { id: "maintenance" as NavView, label: "Maintenance", icon: "🛠️" },
        {
          id: "alerts" as NavView,
          label: "Alerts",
          icon: "🔔",
          badge: activeAlertCount > 0 ? activeAlertCount : undefined,
        },
      ],
    },
  ];

  const engineOptions = ["UAV_ENG_001", "UAV_ENG_002", "TEST_BENCH_ROTAX"];

  return (
    <aside className={`gcs-sidebar ${isCollapsed ? "collapsed" : ""}`}>
      {/* Sidebar Header with Toggle */}
      <div className="sidebar-header">
        <div className="sidebar-brand-title">
          {!isCollapsed && (
            <>
              <span className="sidebar-logo">✈️</span>
              <span className="sidebar-title-text">AEROTWIN GCS</span>
            </>
          )}
        </div>
        <button
          className="sidebar-collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          aria-label="Toggle Sidebar"
        >
          {isCollapsed ? "▶" : "◀"}
        </button>
      </div>

      {/* Engine Selector Dropdown */}
      <div className="sidebar-engine-selector">
        {!isCollapsed && <span className="engine-selector-label">TARGET ENGINE</span>}
        <div className="engine-dropdown-wrap">
          <span className="engine-chip-icon">🛩️</span>
          <select
            className="engine-select"
            value={selectedEngine}
            onChange={(e) => onSelectEngine(e.target.value)}
            disabled={isCollapsed}
          >
            {engineOptions.map((eng) => (
              <option key={eng} value={eng}>
                {eng}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="sidebar-nav">
        {navSections.map((sec) => (
          <div key={sec.heading} className="nav-group">
            {!isCollapsed && <div className="nav-group-heading">{sec.heading}</div>}
            <ul className="nav-list">
              {sec.items.map((item) => {
                const isActive = currentView === item.id;
                return (
                  <li key={item.id}>
                    <button
                      className={`nav-item-btn ${isActive ? "active" : ""}`}
                      onClick={() => onSelectView(item.id)}
                      title={item.label}
                    >
                      <span className="nav-icon">{item.icon}</span>
                      {!isCollapsed && (
                        <span className="nav-label">{item.label}</span>
                      )}
                      {!isCollapsed && item.tag && (
                        <span className="nav-tag">{item.tag}</span>
                      )}
                      {!isCollapsed && item.badge !== undefined && (
                        <span className="nav-badge-count">{item.badge}</span>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Sidebar Footer status */}
      <div className="sidebar-footer">
        {!isCollapsed && (
          <div className="sidebar-telemetry-status">
            <span className="footer-status-dot"></span>
            <span className="footer-status-text">AVIONICS BUS OK</span>
          </div>
        )}
      </div>
    </aside>
  );
}

"use client";

import React, { useState } from "react";
import { TelemetryData } from "@/types/telemetry";

interface DigitalTwinCenterpieceProps {
  telemetry: TelemetryData | null;
  activeScenario: string;
  onInjectScenario: (scenario: string) => void;
}

export default function DigitalTwinCenterpiece({
  telemetry,
  activeScenario,
  onInjectScenario,
}: DigitalTwinCenterpieceProps) {
  const [viewMode, setViewMode] = useState<"full" | "engine" | "thermal">("full");
  const [tooltip, setTooltip] = useState<{ title: string; desc: string } | null>(null);

  const rpm = telemetry?.rpm ?? 6100;
  const spinPeriod = Math.max(0.08, 60 / Math.max(rpm, 1000));
  const scenario = telemetry?.fault_label || activeScenario || "Normal";
  const health = telemetry ? Math.max(Math.min(telemetry.health_index, 100), 0) : 100;

  // Compute SVG transform based on camera view mode
  let svgTransform = "scale(1) translate(0, 0)";
  if (viewMode === "engine") {
    svgTransform = "scale(1.85) translate(-100px, 0)";
  } else if (viewMode === "thermal") {
    svgTransform = "scale(1.35) translate(-40px, 0)";
  }

  // Determine Subsystem classes and colors based on Scenario
  let elAvionicsClass = "part-nominal";
  let elRadiatorClass = "part-nominal";
  let elEngineClass = "part-nominal";
  let elCyl1Class = "part-nominal";
  let elCyl2Class = "part-nominal";
  let elCyl3Class = "part-nominal";
  let elCyl4Class = "part-nominal";
  let elFuelStroke = "#38bdf8";
  let elOilClass = "part-nominal";
  let elExhaustStroke = "#ef4444";
  let elPropFill = "#38bdf8";
  let mountFills = ["#64748b", "#64748b", "#64748b", "#64748b"];

  let reticleVisible = false;
  let reticlePos = { cx: 315, cy: 135 };
  let dotColor = "var(--accent-emerald)";
  let anomalyTitle = "ALL PROPULSION SUBSYSTEMS NOMINAL";
  let anomalyTitleColor = "#10b981";
  let anomalyPart = "PIN: PROPULSION BAY [OK]";

  if (scenario === "Normal" || health > 90) {
    reticleVisible = false;
    dotColor = "#10b981";
    anomalyTitle = "ALL PROPULSION SUBSYSTEMS NOMINAL";
    anomalyTitleColor = "#10b981";
    anomalyPart = "PIN: PROPULSION BAY [OK]";
  } else if (scenario === "Overheating") {
    elRadiatorClass = "part-thermal";
    elEngineClass = "part-thermal";
    elCyl1Class = "part-thermal";
    elCyl2Class = "part-thermal";
    elCyl3Class = "part-thermal";
    elCyl4Class = "part-thermal";

    reticleVisible = true;
    reticlePos = { cx: 280, cy: 135 };
    dotColor = "#ef4444";
    anomalyTitle = `THERMAL ANOMALY: CHT ${(telemetry?.cht_c ?? 150).toFixed(1)}°C / OIL ${(telemetry?.oil_temperature_c ?? 95).toFixed(1)}°C`;
    anomalyTitleColor = "#ff5722";
    anomalyPart = "HOTSPOT: CYLINDER HEADS & COOLING RADIATOR";
  } else if (scenario === "Injector_Degradation") {
    elFuelStroke = "#f59e0b";
    elEngineClass = "part-warning";

    reticleVisible = true;
    reticlePos = { cx: 305, cy: 130 };
    dotColor = "#f59e0b";
    anomalyTitle = `COMBUSTION DEGRADATION: FUEL FLOW ${(telemetry?.fuel_flow_lh ?? 18.5).toFixed(1)} L/H`;
    anomalyTitleColor = "#f59e0b";
    anomalyPart = "HOTSPOT: HIGH-PRESSURE FUEL INJECTION RAIL";
  } else if (scenario === "Lubrication") {
    elOilClass = "part-critical";
    elEngineClass = "part-warning";

    reticleVisible = true;
    reticlePos = { cx: 373, cy: 135 };
    dotColor = "#ef4444";
    anomalyTitle = `HYDRAULIC ANOMALY: OIL PRESSURE CRITICAL (${(telemetry?.oil_pressure_bar ?? 4.3).toFixed(2)} BAR)`;
    anomalyTitleColor = "#ef4444";
    anomalyPart = "HOTSPOT: LUBRICATION SUMP & OIL SCAVENGE PUMP";
  } else if (scenario === "Vibration_Fault") {
    elPropFill = "#f59e0b";
    elEngineClass = "part-warning";
    mountFills = ["#ef4444", "#ef4444", "#ef4444", "#ef4444"];

    reticleVisible = true;
    reticlePos = { cx: 350, cy: 135 };
    dotColor = "#f59e0b";
    anomalyTitle = `MECHANICAL ANOMALY: VIBRATION SPIKE (${(telemetry?.vibration_g ?? 0.2).toFixed(3)} g RMS)`;
    anomalyTitleColor = "#f59e0b";
    anomalyPart = "HOTSPOT: CRANKSHAFT & DYNAFOCAL ENGINE MOUNTS";
  } else if (scenario === "Sensor_Drift") {
    elAvionicsClass = "part-warning";

    reticleVisible = true;
    reticlePos = { cx: 85, cy: 135 };
    dotColor = "#f59e0b";
    anomalyTitle = `AVIONICS HARNESS: CHT SENSOR DRIFT DETECTED (${(telemetry?.cht_c ?? 150).toFixed(1)}°C)`;
    anomalyTitleColor = "#38bdf8";
    anomalyPart = "HOTSPOT: NOSE AVIONICS & CHT SENSOR HARNESS";
  } else if (scenario === "Misfire") {
    elCyl1Class = "part-critical";
    elCyl3Class = "part-warning";
    elExhaustStroke = "#ff3d00";

    reticleVisible = true;
    reticlePos = { cx: 310, cy: 120 };
    dotColor = "#ef4444";
    anomalyTitle = `IGNITION FAULT: INTERMITTENT CYLINDER MISFIRE`;
    anomalyTitleColor = "#ef4444";
    anomalyPart = "HOTSPOT: CYLINDER #1 SPARK & EXHAUST RUNNER";
  } else if (scenario === "Sensor_Fault_Temp") {
    elAvionicsClass = "part-critical";

    reticleVisible = true;
    reticlePos = { cx: 85, cy: 135 };
    dotColor = "#f59e0b";
    anomalyTitle = `SENSOR ISOLATION: CHT SENSOR FAULT DETECTED (${(telemetry?.cht_c ?? 350).toFixed(1)}°C) — ENGINE HEALTHY`;
    anomalyTitleColor = "#f59e0b";
    anomalyPart = "DIAGNOSIS: ISOLATED SENSOR MALFUNCTION — NOT AN ENGINE FAULT";
  } else if (scenario === "Engine_Failure_Multi") {
    elEngineClass = "part-critical";
    elCyl1Class = "part-critical";
    elCyl2Class = "part-critical";
    elCyl3Class = "part-thermal";
    elCyl4Class = "part-thermal";
    elRadiatorClass = "part-warning";
    elOilClass = "part-critical";
    elPropFill = "#ef4444";
    mountFills = ["#ef4444", "#ef4444", "#ef4444", "#ef4444"];

    reticleVisible = true;
    reticlePos = { cx: 315, cy: 135 };
    dotColor = "#ef4444";
    anomalyTitle = `ENGINE FAILURE: MULTI-SENSOR CORRELATED ANOMALY DETECTED`;
    anomalyTitleColor = "#ef4444";
    anomalyPart = "DIAGNOSIS: SYSTEM-LEVEL ENGINE FAULT — MULTIPLE SUBSYSTEMS AFFECTED";
  }

  const scenariosList = [
    { id: "Normal", label: "🟢 Nominal Operation", tag: "HEALTHY", tagClass: "normal" },
    { id: "Overheating", label: "🔥 Cooling / Overheating", tag: "THERMAL", tagClass: "" },
    { id: "Injector_Degradation", label: "⚙️ Injector Degradation", tag: "COMBUSTION", tagClass: "" },
    { id: "Lubrication", label: "🛢️ Lubrication Starvation", tag: "HYDRAULIC", tagClass: "" },
    { id: "Vibration_Fault", label: "〰️ Abnormal Vibration", tag: "MECHANICAL", tagClass: "" },
    { id: "Sensor_Drift", label: "📡 CHT Sensor Drift", tag: "AVIONICS", tagClass: "" },
    { id: "Misfire", label: "💥 Cylinder Misfire", tag: "IGNITION", tagClass: "" },
    { id: "Sensor_Fault_Temp", label: "🌡️ Sensor Fault: Temp", tag: "SENSOR ISO", tagClass: "" },
    { id: "Engine_Failure_Multi", label: "🔧 Engine Failure: Multi", tag: "ENGINE DX", tagClass: "" },
  ];

  return (
    <>
      {/* MALE UAV DIGITAL TWIN MINI-CLONE VISUALIZER */}
      <div className="panel uav-twin-panel">
        <div className="panel-header">
          <span className="panel-title">
            <span>🛩️</span> MALE UAV Airframe & Subsystem Mini-Clone
          </span>
          <div className="uav-view-controls">
            <button
              className={`uav-btn-mini ${viewMode === "full" ? "active" : ""}`}
              id="btn-view-all"
              onClick={() => setViewMode("full")}
            >
              Full Drone
            </button>
            <button
              className={`uav-btn-mini ${viewMode === "engine" ? "active" : ""}`}
              id="btn-view-engine"
              onClick={() => setViewMode("engine")}
            >
              Engine Bay
            </button>
            <button
              className={`uav-btn-mini ${viewMode === "thermal" ? "active" : ""}`}
              id="btn-view-thermal"
              onClick={() => setViewMode("thermal")}
            >
              Thermal HUD
            </button>
          </div>
        </div>

        <div className="uav-hud-container" id="uav-hud">
          <div className="uav-hud-grid"></div>
          <div className="uav-hud-radar"></div>

          {tooltip && (
            <div className="uav-tooltip" id="uav-tooltip" style={{ display: "block" }}>
              <span style={{ color: "var(--accent-cyan)", fontWeight: 700 }}>
                {tooltip.title}
              </span>
              <br />
              <span style={{ color: "#94a3b8", fontSize: "0.65rem" }}>
                {tooltip.desc}
              </span>
            </div>
          )}

          {/* Vector Graphic of MALE UAV Digital Twin */}
          <svg
            className="uav-svg-model"
            id="uav-svg"
            viewBox="0 0 540 270"
            xmlns="http://www.w3.org/2000/svg"
            style={{ transform: svgTransform }}
          >
            <defs>
              <linearGradient id="fuselageGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#0f172a" />
                <stop offset="50%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0f172a" />
              </linearGradient>
              <linearGradient id="wingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#0b1329" />
                <stop offset="50%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#0b1329" />
              </linearGradient>
              <filter id="glow-cyan" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Wings */}
            <g id="uav-wings" className="uav-wing-structure">
              <polygon
                points="180,135 210,25 240,25 230,135"
                fill="url(#wingGrad)"
                stroke="rgba(56, 189, 248, 0.4)"
                strokeWidth="1.2"
              />
              <polygon
                points="180,135 210,245 240,245 230,135"
                fill="url(#wingGrad)"
                stroke="rgba(56, 189, 248, 0.4)"
                strokeWidth="1.2"
              />
              <line
                x1="200"
                y1="55"
                x2="225"
                y2="55"
                stroke="rgba(56, 189, 248, 0.25)"
                strokeDasharray="3,2"
              />
              <line
                x1="200"
                y1="215"
                x2="225"
                y2="215"
                stroke="rgba(56, 189, 248, 0.25)"
                strokeDasharray="3,2"
              />
            </g>

            {/* Inverted V-Tail */}
            <g id="uav-tail">
              <polygon
                points="380,135 440,75 455,75 420,135"
                fill="#0b1329"
                stroke="rgba(56, 189, 248, 0.4)"
                strokeWidth="1.2"
              />
              <polygon
                points="380,135 440,195 455,195 420,135"
                fill="#0b1329"
                stroke="rgba(56, 189, 248, 0.4)"
                strokeWidth="1.2"
              />
            </g>

            {/* Fuselage */}
            <path
              className="uav-hull"
              d="M 60,135 C 75,115 150,118 360,122 L 440,128 L 470,135 L 440,142 L 360,148 C 150,152 75,155 60,135 Z"
              fill="url(#fuselageGrad)"
            />

            {/* Avionics */}
            <g
              id="part-avionics"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Avionics & Sensor Bay (Nose)",
                  desc: "Dual-redundant Flight Computer & CHT Sensor Bus",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <path
                d="M 60,135 C 68,122 100,122 110,135 C 100,148 68,148 60,135 Z"
                className={elAvionicsClass}
                id="svg-part-avionics"
              />
              <circle cx="85" cy="135" r="3.5" fill="#38bdf8" />
              <text
                x="85"
                y="112"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                AVIONICS/PROBE
              </text>
              <line x1="85" y1="116" x2="85" y2="126" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Mid-Fuselage Payload */}
            <rect
              x="135"
              y="126"
              width="60"
              height="18"
              rx="3"
              fill="rgba(37, 99, 235, 0.1)"
              stroke="rgba(56, 189, 248, 0.2)"
              strokeWidth="1"
            />

            {/* Radiator */}
            <g
              id="part-radiator"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Cooling System & Radiator",
                  desc: "Ram-air cooling scoop, liquid coolant jacket & CHT heat sink",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <rect
                x="235"
                y="115"
                width="28"
                height="40"
                rx="3"
                className={elRadiatorClass}
                id="svg-part-radiator"
              />
              <line x1="240" y1="119" x2="240" y2="151" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
              <line x1="249" y1="119" x2="249" y2="151" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
              <line x1="258" y1="119" x2="258" y2="151" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
              <text
                x="249"
                y="105"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                RADIATOR/COOLING
              </text>
              <line x1="249" y1="107" x2="249" y2="114" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Engine Block */}
            <g
              id="part-engine-block"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Aero Piston Engine Block",
                  desc: "4-Cylinder 4-Stroke Turbocharged Boxer Engine (CHT/EGT core)",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <rect x="280" y="123" width="70" height="24" rx="4" className={elEngineClass} id="svg-part-engine" />
              <rect x="290" y="112" width="22" height="11" rx="2" className={elCyl1Class} id="svg-cyl-top1" />
              <rect x="320" y="112" width="22" height="11" rx="2" className={elCyl2Class} id="svg-cyl-top2" />
              <rect x="290" y="147" width="22" height="11" rx="2" className={elCyl3Class} id="svg-cyl-bot1" />
              <rect x="320" y="147" width="22" height="11" rx="2" className={elCyl4Class} id="svg-cyl-bot2" />
              <text
                x="315"
                y="98"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                PISTON ENGINE BLOCK
              </text>
              <line x1="315" y1="100" x2="315" y2="111" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Fuel System */}
            <g
              id="part-fuel-system"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Fuel Injection Rail",
                  desc: "High-pressure electronic fuel rail & port injectors",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <path
                d="M 215,135 L 285,130 M 285,130 L 345,130"
                stroke={elFuelStroke}
                strokeWidth="1.8"
                fill="none"
                id="svg-part-fuel"
              />
              <circle cx="301" cy="130" r="2.5" fill="#38bdf8" id="svg-inj-1" />
              <circle cx="331" cy="130" r="2.5" fill="#38bdf8" id="svg-inj-2" />
              <text
                x="300"
                y="174"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                FUEL RAIL
              </text>
              <line x1="300" y1="166" x2="300" y2="135" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Oil System */}
            <g
              id="part-oil-system"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Lubrication & Oil Circuit",
                  desc: "Oil sump, mechanical scavenge pump & oil cooling lines",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <rect x="360" y="125" width="26" height="20" rx="3" className={elOilClass} id="svg-part-oil" />
              <path d="M 350,140 L 360,140" stroke="#10b981" strokeWidth="1.5" />
              <text
                x="373"
                y="174"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                OIL SUMP/PUMP
              </text>
              <line x1="373" y1="166" x2="373" y2="147" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Mounts */}
            <g
              id="part-mounts"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Engine Dynafocal Mounts",
                  desc: "Vibration isolation dampers & airframe structural nacelle",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <circle cx="282" cy="120" r="3" fill={mountFills[0]} id="svg-mount-1" />
              <circle cx="282" cy="150" r="3" fill={mountFills[1]} id="svg-mount-2" />
              <circle cx="352" cy="120" r="3" fill={mountFills[2]} id="svg-mount-3" />
              <circle cx="352" cy="150" r="3" fill={mountFills[3]} id="svg-mount-4" />
            </g>

            {/* Exhaust */}
            <g
              id="part-exhaust"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Exhaust & Turbocharger",
                  desc: "Inconel exhaust headers & variable geometry turbine (EGT sensor zone)",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <path
                d="M 345,123 C 375,116 395,118 410,124"
                stroke={elExhaustStroke}
                strokeWidth="2"
                fill="none"
                id="svg-part-exhaust"
              />
              <circle cx="412" cy="124" r="4.5" fill="#ef4444" opacity="0.8" />
            </g>

            {/* Pusher Propeller */}
            <g
              id="part-propeller"
              className="uav-subsystem"
              onMouseEnter={() =>
                setTooltip({
                  title: "Pusher Propeller Hub",
                  desc: "Variable-pitch composite pusher propeller assembly",
                })
              }
              onMouseLeave={() => setTooltip(null)}
            >
              <circle
                cx="472"
                cy="135"
                r="5"
                fill={elPropFill}
                stroke="#ffffff"
                strokeWidth="1"
                id="svg-part-propeller"
              />
              <ellipse
                cx="472"
                cy="135"
                rx="3"
                ry="50"
                fill="rgba(56, 189, 248, 0.15)"
                stroke="rgba(56, 189, 248, 0.4)"
                strokeDasharray="4,2"
              />
              <g
                className="propeller-blade"
                id="prop-blades"
                style={{ animationDuration: `${spinPeriod.toFixed(2)}s` }}
              >
                <line x1="472" y1="90" x2="472" y2="180" stroke="#f8fafc" strokeWidth="3" strokeLinecap="round" />
                <circle cx="472" cy="90" r="2.5" fill="#ef4444" />
                <circle cx="472" cy="180" r="2.5" fill="#ef4444" />
              </g>
              <text
                x="472"
                y="75"
                fill="#94a3b8"
                fontSize="7"
                fontFamily="JetBrains Mono"
                textAnchor="middle"
              >
                PUSHER PROP
              </text>
              <line x1="472" y1="78" x2="472" y2="88" stroke="#64748b" strokeWidth="0.8" />
            </g>

            {/* Anomaly Reticle */}
            {reticleVisible && (
              <g id="anomaly-reticle">
                <circle
                  cx={reticlePos.cx}
                  cy={reticlePos.cy}
                  r="24"
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="1.5"
                  strokeDasharray="4,3"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from={`0 ${reticlePos.cx} ${reticlePos.cy}`}
                    to={`360 ${reticlePos.cx} ${reticlePos.cy}`}
                    dur="4s"
                    repeatCount="indefinite"
                  />
                </circle>
                <circle cx={reticlePos.cx} cy={reticlePos.cy} r="4" fill="#ef4444" />
              </g>
            )}
          </svg>

          {/* Fault Banner */}
          <div className="uav-fault-banner">
            <div className="fault-indicator" id="uav-fault-text">
              <span className="status-dot" style={{ color: dotColor }} id="uav-status-dot" />
              <span id="uav-anomaly-title" style={{ color: anomalyTitleColor }}>
                {anomalyTitle}
              </span>
            </div>
            <div
              style={{
                color: "var(--text-muted)",
                fontSize: "0.68rem",
                fontFamily: "'JetBrains Mono', monospace",
              }}
              id="uav-anomaly-part"
            >
              {anomalyPart}
            </div>
          </div>
        </div>
      </div>

      {/* Fault Injection Simulator (Interactive Demo) */}
      <div className="panel">
        <div className="panel-header">
          <span className="panel-title">Fault Injection Matrix</span>
          <span className="scenario-tag" id="active-scenario-tag">
            {scenario.toUpperCase()}
          </span>
        </div>
        <div className="scenarios-container">
          {scenariosList.map((sc) => (
            <button
              key={sc.id}
              className={`scenario-btn ${activeScenario === sc.id ? `active ${sc.tagClass}` : ""}`}
              onClick={() => onInjectScenario(sc.id)}
            >
              <span>{sc.label}</span>
              <span className="scenario-tag">{sc.tag}</span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

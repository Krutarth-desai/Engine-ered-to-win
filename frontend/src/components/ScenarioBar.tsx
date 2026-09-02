"use client";

import React from "react";

interface ScenarioBarProps {
  activeScenario: string;
  onSelectScenario: (scenario: string) => void;
}

export default function ScenarioBar({ activeScenario, onSelectScenario }: ScenarioBarProps) {
  const scenarios = [
    { id: "Normal", label: "Normal Cruise", desc: "Nominal 2450 RPM cruise baseline" },
    { id: "Overheating", label: "Overheating", desc: "Thermal stress: EGT/CHT ramp" },
    { id: "Oil_Pressure_Loss", label: "Oil Pressure Loss", desc: "Lubrication failure risk" },
    { id: "RPM_Drop", label: "Power Loss", desc: "Governor / fuel supply restriction" },
    { id: "High_Vibration", label: "High Vibration", desc: "Imbalance & bearing wear" },
    { id: "Sensor_Fault_CHT", label: "Sensor Fault (CHT)", desc: "Isolated thermocouple bias" },
    { id: "Engine_Failure_Multi", label: "Critical Engine Failure", desc: "Correlated multi-sensor breakdown" },
  ];

  return (
    <div className="scenario-injector-bar">
      <div className="scenario-label-wrap">
        <span className="scenario-bar-title"><strong>MISSION FAULT INJECTION:</strong></span>
      </div>
      <div className="scenario-buttons-row">
        {scenarios.map((sc) => (
          <button
            key={sc.id}
            className={`scenario-btn ${activeScenario === sc.id ? "active" : ""}`}
            onClick={() => onSelectScenario(sc.id)}
            title={sc.desc}
          >
            <strong>{sc.label}</strong>
          </button>
        ))}
      </div>
    </div>
  );
}

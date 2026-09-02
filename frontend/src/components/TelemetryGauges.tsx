"use client";

import React from "react";
import { TelemetryData } from "@/types/telemetry";

interface TelemetryGaugesProps {
  telemetry: TelemetryData | null;
}

export default function TelemetryGauges({ telemetry }: TelemetryGaugesProps) {
  const rpm = telemetry?.rpm ?? 6100;
  const cht = telemetry?.cht_c ?? 150.0;
  const egt = telemetry?.egt_c ?? 700.0;
  const oilP = telemetry?.oil_pressure_bar ?? 4.3;
  const oilT = telemetry?.oil_temperature_c ?? 95.0;
  const fuel = telemetry?.fuel_flow_lh ?? 18.5;
  const vib = telemetry?.vibration_g ?? 0.2;
  const battery = telemetry?.battery_voltage_v ?? 28.0;
  const timing = telemetry?.injection_timing_deg ?? 22.0;
  const timestamp = telemetry
    ? new Date(telemetry.timestamp).toLocaleTimeString()
    : "--:--:--";

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Live Sensor Telemetry Gauges</span>
        <span
          className="metric-tag"
          style={{ fontSize: "0.75rem", fontFamily: "'JetBrains Mono', monospace" }}
          id="val-timestamp"
        >
          {timestamp}
        </span>
      </div>
      <div className="telemetry-grid">
        {/* RPM */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Rotational Speed</span>
            <span className="card-unit">RPM</span>
          </div>
          <div className="card-val" id="val-rpm">
            {rpm.toFixed(0)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-rpm"
              className="card-progress-fill"
              style={{ width: `${Math.min((rpm / 7000) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* CHT */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Cylinder Head (CHT)</span>
            <span className="card-unit">°C</span>
          </div>
          <div className="card-val" id="val-cht">
            {cht.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-cht"
              className="card-progress-fill"
              style={{ width: `${Math.min((cht / 250) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* EGT */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Exhaust Gas (EGT)</span>
            <span className="card-unit">°C</span>
          </div>
          <div className="card-val" id="val-egt">
            {egt.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-egt"
              className="card-progress-fill"
              style={{ width: `${Math.min((egt / 900) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Oil Pressure */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Oil Pressure</span>
            <span className="card-unit">BAR</span>
          </div>
          <div className="card-val" id="val-oil-p">
            {oilP.toFixed(2)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-oil-p"
              className="card-progress-fill"
              style={{ width: `${Math.min((oilP / 6) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Oil Temp */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Oil Temperature</span>
            <span className="card-unit">°C</span>
          </div>
          <div className="card-val" id="val-oil-t">
            {oilT.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-oil-t"
              className="card-progress-fill"
              style={{ width: `${Math.min((oilT / 150) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Fuel Flow */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Fuel Flow</span>
            <span className="card-unit">L/H</span>
          </div>
          <div className="card-val" id="val-fuel">
            {fuel.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-fuel"
              className="card-progress-fill"
              style={{ width: `${Math.min((fuel / 30) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Vibration */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Vibration RMS</span>
            <span className="card-unit">g</span>
          </div>
          <div className="card-val" id="val-vib">
            {vib.toFixed(3)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-vib"
              className="card-progress-fill"
              style={{ width: `${Math.min((vib / 1.5) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Battery */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Bus Voltage</span>
            <span className="card-unit">V</span>
          </div>
          <div className="card-val" id="val-battery">
            {battery.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-battery"
              className="card-progress-fill"
              style={{ width: `${Math.min((battery / 32) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Timing */}
        <div className="telemetry-card">
          <div className="card-top">
            <span className="card-name">Injection Timing</span>
            <span className="card-unit">° BTDC</span>
          </div>
          <div className="card-val" id="val-timing">
            {timing.toFixed(1)}
          </div>
          <div className="card-progress-bar">
            <div
              id="prog-timing"
              className="card-progress-fill"
              style={{ width: `${Math.min((timing / 35) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

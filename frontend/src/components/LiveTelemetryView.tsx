"use client";

import React from "react";
import { UnifiedTelemetryPayload } from "../types/telemetry";
import EngineSensorsPanel from "./EngineSensorsPanel";
import TelemetryChart from "./TelemetryChart";
import TelemetryGauges from "./TelemetryGauges";

interface LiveTelemetryViewProps {
  payload: UnifiedTelemetryPayload;
}

export default function LiveTelemetryView({ payload }: LiveTelemetryViewProps) {
  // Convert payload to TelemetryData format for TelemetryChart & TelemetryGauges
  const flatTelemetry = {
    timestamp: payload.timestamp,
    engine_id: payload.vehicle?.vehicle_id || "ENG_001",
    rpm: payload.sensors?.rpm?.value ?? payload.rpm ?? 2450,
    cht_c: payload.sensors?.cht?.value ?? payload.cht_c ?? 142.0,
    egt_c: payload.sensors?.egt?.value ?? payload.egt_c ?? 615.0,
    oil_pressure_bar: payload.sensors?.oil_pressure?.value
      ? payload.sensors.oil_pressure.value / 14.5038
      : (payload.oil_pressure_bar ?? 4.7),
    oil_temperature_c: payload.sensors?.oil_temperature?.value ?? payload.oil_temperature_c ?? 92.0,
    fuel_flow_lh: payload.sensors?.fuel_flow?.value ?? payload.fuel_flow_lh ?? 17.6,
    vibration_g: payload.sensors?.vibration?.value ?? payload.vibration_g ?? 1.42,
    battery_voltage_v: payload.sensors?.bus_voltage?.value ?? payload.battery_voltage_v ?? 27.6,
    injection_timing_deg: payload.sensors?.injection_timing?.value ?? payload.injection_timing_deg ?? 23.4,
    health_index: payload.health_index ?? 72,
    rul: payload.prognostics?.predicted_rul ?? 117,
    fault_label: payload.fault_label ?? "Normal",
  };

  return (
    <div className="view-container live-telemetry-view">
      <div className="view-header-strip">
        <div>
          <h2 className="view-title"><strong>9-CHANNEL LIVE TELEMETRY &amp; TIME-SERIES DYNAMICS</strong></h2>
          <p className="view-subtitle">High-frequency 1 Hz avionics telemetry stream, min/max envelopes, and rolling thermal waveforms</p>
        </div>
        <span className="badge-live-pulse">LIVE 1 Hz STREAM</span>
      </div>

      <div className="telemetry-view-grid">
        {/* Left Column: Detailed 9-Sensor Panel */}
        <div className="telemetry-col-left">
          <EngineSensorsPanel sensors={payload.sensor_list || []} />
        </div>

        {/* Right Column: Dynamic Time-Series Waveforms & Gauge Clusters */}
        <div className="telemetry-col-right">
          {/* Real-Time 30-Second Thermal Waveforms */}
          <div className="telemetry-chart-card">
            <TelemetryChart telemetry={flatTelemetry} />
          </div>

          {/* Analog/Digital Multi-Gauge Cluster */}
          <div className="telemetry-gauges-card">
            <TelemetryGauges telemetry={flatTelemetry} />
          </div>
        </div>
      </div>
    </div>
  );
}

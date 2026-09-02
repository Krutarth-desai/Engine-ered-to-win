"use client";

import React, { useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { UnifiedTelemetryPayload, SensorItem } from "@/types/telemetry";
import AuthScreen from "@/components/AuthScreen";
import Header from "@/components/Header";
import DigitalTwinCenterpiece from "@/components/DigitalTwinCenterpiece";
import EngineSensorsPanel from "@/components/EngineSensorsPanel";
import RulPrognosticsGauge from "@/components/RulPrognosticsGauge";
import RulTrajectoryChart from "@/components/RulTrajectoryChart";
import RecentTrendsCard from "@/components/RecentTrendsCard";
import HealthRiskPanel from "@/components/HealthRiskPanel";
import LstmMetricsPanel from "@/components/LstmMetricsPanel";
import FeatureContributionPanel from "@/components/FeatureContributionPanel";
import PhmAlertsPanel from "@/components/PhmAlertsPanel";
import ScenarioBar from "@/components/ScenarioBar";

// Default initial state matching nominal operational cruise
const DEFAULT_SENSORS: SensorItem[] = [
  { key: "rpm", name: "RPM", value: 2450, unit: "RPM", min: 0, max: 3200, status: "NORMAL", trend: "STABLE", progressPct: 76.5 },
  { key: "cht", name: "CHT", value: 142.0, unit: "°C", min: 50, max: 240, status: "NORMAL", trend: "STABLE", progressPct: 48.4 },
  { key: "egt", name: "EGT", value: 615.0, unit: "°C", min: 250, max: 950, status: "NORMAL", trend: "STABLE", progressPct: 52.1 },
  { key: "oil_pressure", name: "Oil Pressure", value: 68.0, unit: "psi", min: 0, max: 100, status: "NORMAL", trend: "STABLE", progressPct: 68.0 },
  { key: "oil_temperature", name: "Oil Temperature", value: 92.0, unit: "°C", min: 30, max: 150, status: "NORMAL", trend: "STABLE", progressPct: 51.6 },
  { key: "fuel_flow", name: "Fuel Flow", value: 17.6, unit: "L/hr", min: 0, max: 40, status: "NORMAL", trend: "STABLE", progressPct: 44.0 },
  { key: "vibration", name: "Vibration", value: 1.42, unit: "g", min: 0, max: 4.5, status: "NORMAL", trend: "STABLE", progressPct: 31.5 },
  { key: "bus_voltage", name: "Bus Voltage", value: 27.6, unit: "V", min: 18, max: 34, status: "NORMAL", trend: "STABLE", progressPct: 60.0 },
  { key: "injection_timing", name: "Injection Timing", value: 23.4, unit: "°CA", min: 10, max: 38, status: "NORMAL", trend: "STABLE", progressPct: 47.8 },
];

const DEFAULT_PAYLOAD: UnifiedTelemetryPayload = {
  cycle: 31,
  timestamp: new Date().toISOString(),
  vehicle: {
    vehicle_id: "UAV_ENG_001",
    mission_id: "ISR_PATROL_27",
    altitude: 15000,
    throttle: 75,
    update_rate: 1,
  },
  sensors: {},
  sensor_list: DEFAULT_SENSORS,
  prognostics: {
    predicted_rul: 117.4,
    actual_rul: 112.0,
    remaining_time_str: "01:57:32",
    current_cycle: 31,
    max_useful_life: 250,
    rul_unclipped: 117.4,
    rul_clipped: 117.4,
    degradation_trend: "Increasing",
    confidence: 92.4,
    abs_error: 5.4,
    model_mae: 10.08,
    window_size: 30,
    sensor_count: 15,
  },
  health_index: 72,
  risk: {
    level: "MEDIUM",
    anomaly: "NORMAL",
    action: "Monitor Closely",
  },
  contributing_features: [
    { name: "EGT", score: 0.218, impact: "increases thermal stress", direction: "UP" },
    { name: "CHT", score: 0.183, impact: "increases cylinder thermal gradient", direction: "UP" },
    { name: "Vibration", score: 0.142, impact: "indicates mechanical wear", direction: "UP" },
    { name: "Oil Pressure", score: 0.128, impact: "indicates lubrication concern", direction: "DOWN" },
    { name: "Oil Temperature", score: 0.096, impact: "indicates cooling oil degradation", direction: "STABLE" },
    { name: "Fuel Flow", score: 0.071, impact: "indicates mixture deviation", direction: "STABLE" },
    { name: "RPM", score: 0.062, impact: "indicates power output lag", direction: "STABLE" },
    { name: "Injection Timing", score: 0.050, impact: "indicates combustion phase shift", direction: "STABLE" },
  ],
  recent_trends: {
    points: Array.from({ length: 30 }, (_, i) => ({
      cycle: i + 2,
      egt: 602 + i * 0.45,
      oil_pressure: 70 - i * 0.08,
      vibration: 1.38 + i * 0.003,
      health_index: 85 - i * 0.45,
    })),
    deltas: {
      egt_delta: 12.6,
      oil_pressure_delta: -2.4,
      vibration_delta: 0.12,
      health_delta: -5.2,
    },
  },
  trajectory: Array.from({ length: 31 }, (_, i) => ({
    cycle: i + 1,
    actual_rul: 250 - (i + 1),
    predicted_rul: Math.max(0, 250 - (i + 1) + Math.sin(i / 3) * 4),
  })),
  alerts: [
    {
      id: "alt-1",
      level: "CAUTION",
      title: "ELEVATED EGT TREND",
      message: "EGT rising faster than normal baseline. Thermal gradient increasing.",
      time_ago: "2 min ago",
      timestamp: new Date(Date.now() - 120000).toISOString(),
    },
    {
      id: "alt-2",
      level: "INFO",
      title: "VIBRATION INCREASING",
      message: "Harmonic frequencies rising in high cylinder zone. Monitor bearing & valve train.",
      time_ago: "3 min ago",
      timestamp: new Date(Date.now() - 180000).toISOString(),
    },
    {
      id: "alt-3",
      level: "NORMAL",
      title: "ALL SYSTEMS NOMINAL",
      message: "Cross-sensor validation confirms genuine propulsion health baseline.",
      time_ago: "5 min ago",
      timestamp: new Date(Date.now() - 300000).toISOString(),
    },
  ],
  fault_label: "Normal",
  scenario: "Normal",
};

export default function Home() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [payload, setPayload] = useState<UnifiedTelemetryPayload>(DEFAULT_PAYLOAD);
  const [activeScenario, setActiveScenario] = useState<string>("Normal");

  const wsRef = useRef<WebSocket | null>(null);

  // Helper to ensure public.profiles row
  const ensureProfile = async (user: any) => {
    try {
      await supabase.from("profiles").upsert(
        {
          id: user.id,
          full_name: user.user_metadata?.full_name || user.user_metadata?.name || "",
          email: user.email || "",
          avatar_url: user.user_metadata?.avatar_url || user.user_metadata?.picture || "",
        },
        { onConflict: "id", ignoreDuplicates: true }
      );
    } catch (e) {
      console.warn("[AeroTwin] Profile ensure error:", e);
    }
  };

  // Auth Session Setup
  useEffect(() => {
    const initAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (session?.user) {
        await ensureProfile(session.user);
        setCurrentUser(session.user);
      }
      setAuthChecked(true);
    };

    initAuth();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === "SIGNED_IN" && session?.user) {
        await ensureProfile(session.user);
        setCurrentUser(session.user);
      } else if (event === "TOKEN_REFRESHED" && session?.user) {
        setCurrentUser(session.user);
      } else if (event === "SIGNED_OUT") {
        setCurrentUser(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Connect to Unified Telemetry WebSocket
  useEffect(() => {
    if (!currentUser) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      const wsHost =
        process.env.NEXT_PUBLIC_WS_URL ||
        (typeof window !== "undefined"
          ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:8000`
          : "ws://localhost:8000");
      const wsUrl = `${wsHost}/ws/telemetry`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          // If server sent unified packet
          if (raw.prognostics && raw.sensor_list) {
            setPayload(raw);
            if (raw.scenario) {
              setActiveScenario(raw.scenario);
            }
          }
        } catch (err) {
          console.error("Error parsing telemetry WebSocket frame", err);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimeout = setTimeout(connectWebSocket, 2000);
      };
    };

    connectWebSocket();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [currentUser]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setCurrentUser(null);
  };

  const handleInjectScenario = (scenarioName: string) => {
    setActiveScenario(scenarioName);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ scenario: scenarioName }));
    }
  };

  if (!authChecked) {
    return null;
  }

  return (
    <>
      {!currentUser && (
        <AuthScreen
          onAuthenticated={(user) => {
            setCurrentUser(user);
          }}
        />
      )}

      {currentUser && (
        <div className="gcs-app-container">
          {/* LAYER 1: Header / Mission Bar */}
          <Header
            userEmail={currentUser.email || "Operator"}
            isConnected={isConnected}
            vehicleId={payload.vehicle?.vehicle_id || "UAV_ENG_001"}
            missionId={payload.vehicle?.mission_id || "ISR_PATROL_27"}
            altitude={payload.vehicle?.altitude || 15000}
            throttle={payload.vehicle?.throttle || 75}
            remainingTimeStr={payload.prognostics?.remaining_time_str || "01:57:32"}
            onLogout={handleLogout}
          />

          <main id="app-main" className="gcs-main-content">
            {/* Mission Fault Injection Bar */}
            <ScenarioBar
              activeScenario={activeScenario}
              onSelectScenario={handleInjectScenario}
            />

            {/* LAYER 2: 3-Column Tactical Monitoring Deck */}
            <div className="gcs-three-col-deck">
              {/* Column 1: Engine Sensors (Live) */}
              <div className="gcs-col gcs-col-left">
                <EngineSensorsPanel sensors={payload.sensor_list || DEFAULT_SENSORS} />
              </div>

              {/* Column 2: Centerpiece RUL & Trajectory Deck */}
              <div className="gcs-col gcs-col-center">
                {/* UAV Airframe & Engine Digital Twin Model */}
                <DigitalTwinCenterpiece
                  telemetry={{
                    ...payload,
                    rpm: payload.sensors?.rpm?.value ?? payload.rpm ?? 2450,
                    cht_c: payload.sensors?.cht?.value ?? payload.cht_c ?? 142.0,
                    egt_c: payload.sensors?.egt?.value ?? payload.egt_c ?? 615.0,
                    oil_pressure_bar: payload.sensors?.oil_pressure?.value
                      ? payload.sensors.oil_pressure.value / 14.5038
                      : (payload.oil_pressure_bar ?? 4.7),
                    oil_temperature_c: payload.sensors?.oil_temperature?.value ?? payload.oil_temperature_c ?? 92.0,
                    fuel_flow_lh: payload.sensors?.fuel_flow?.value ?? payload.fuel_flow_lh ?? 17.6,
                    vibration_g: payload.sensors?.vibration?.value ?? payload.vibration_g ?? 1.42,
                    health_index: payload.health_index ?? 72,
                    fault_label: payload.fault_label ?? activeScenario,
                  }}
                  activeScenario={activeScenario}
                  onInjectScenario={handleInjectScenario}
                />

                {/* 1. RUL Gauge + Overview Card */}
                <RulPrognosticsGauge prognostics={payload.prognostics} />

                {/* 2. Actual vs Predicted RUL Trajectory Graph */}
                <RulTrajectoryChart
                  trajectory={payload.trajectory || []}
                  currentCycle={payload.cycle || 31}
                  currentActualRul={payload.prognostics?.actual_rul || 112}
                  currentPredictedRul={payload.prognostics?.predicted_rul || 117.4}
                />

                {/* 3. Recent 30-Cycle Trend Cards */}
                <RecentTrendsCard
                  points={payload.recent_trends?.points || []}
                  deltas={
                    payload.recent_trends?.deltas || {
                      egt_delta: 0,
                      oil_pressure_delta: 0,
                      vibration_delta: 0,
                      health_delta: 0,
                    }
                  }
                />
              </div>

              {/* Column 3: Health & Risk + LSTM Metrics */}
              <div className="gcs-col gcs-col-right">
                <HealthRiskPanel
                  healthIndex={payload.health_index || 72}
                  risk={payload.risk}
                />
                <LstmMetricsPanel prognostics={payload.prognostics} />
              </div>
            </div>

            {/* LAYER 3: Bottom Layer (Contributing Features & PHM Alerts) */}
            <div className="gcs-bottom-deck">
              <div className="bottom-col-features">
                <FeatureContributionPanel
                  features={payload.contributing_features || []}
                />
              </div>
              <div className="bottom-col-alerts">
                <PhmAlertsPanel alerts={payload.alerts || []} />
              </div>
            </div>
          </main>
        </div>
      )}
    </>
  );
}

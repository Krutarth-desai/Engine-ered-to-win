"use client";

import React, { useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { UnifiedTelemetryPayload, SensorItem } from "@/types/telemetry";
import AuthScreen from "@/components/AuthScreen";
import Header from "@/components/Header";
import Sidebar, { NavView } from "@/components/Sidebar";

// View Components
import MainDashboardView from "@/components/MainDashboardView";
import LiveTelemetryView from "@/components/LiveTelemetryView";
import DiagnosticsView from "@/components/DiagnosticsView";
import RulPrognosticsView from "@/components/RulPrognosticsView";
import RegressionTrendsView from "@/components/RegressionTrendsView";
import MaintenanceView from "@/components/MaintenanceView";
import AlertsView from "@/components/AlertsView";

// Default initial telemetry fallback matching nominal operational cruise
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
    degradation_trend: "Stable",
    confidence: 94.8,
    abs_error: 4.2,
    model_mae: 10.08,
    window_size: 30,
    sensor_count: 15,
  },
  health_index: 96,
  risk: {
    level: "LOW",
    anomaly: "NORMAL",
    action: "Nominal Cruise Profile - All Systems Normal",
  },
  contributing_features: [
    { name: "EGT", score: 0.142, impact: "combustion temperature stable", direction: "STABLE" },
    { name: "CHT", score: 0.138, impact: "cylinder thermal gradient balanced", direction: "STABLE" },
    { name: "Oil Pressure", score: 0.125, impact: "hydrodynamic film nominal", direction: "STABLE" },
    { name: "Vibration", score: 0.118, impact: "bearing balance nominal", direction: "STABLE" },
    { name: "Oil Temperature", score: 0.106, impact: "cooling circuit nominal", direction: "STABLE" },
    { name: "Fuel Flow", score: 0.091, impact: "mixture stoichiometry nominal", direction: "STABLE" },
    { name: "RPM", score: 0.082, impact: "governor regulation nominal", direction: "STABLE" },
    { name: "Injection Timing", score: 0.070, impact: "combustion phasing nominal", direction: "STABLE" },
  ],
  recent_trends: {
    points: Array.from({ length: 30 }, (_, i) => ({
      cycle: i + 2,
      egt: 610 + Math.sin(i / 4) * 2,
      oil_pressure: 68 + Math.cos(i / 4) * 0.5,
      vibration: 1.40 + Math.sin(i / 5) * 0.02,
      health_index: 96 - i * 0.05,
    })),
    deltas: {
      egt_delta: 0.4,
      oil_pressure_delta: -0.2,
      vibration_delta: 0.01,
      health_delta: -0.8,
    },
  },
  trajectory: Array.from({ length: 31 }, (_, i) => ({
    cycle: i + 1,
    actual_rul: 250 - (i + 1),
    predicted_rul: Math.max(0, 250 - (i + 1) + Math.sin(i / 3) * 2),
  })),
  alerts: [
    {
      id: "alt-1",
      level: "NORMAL",
      title: "ALL SYSTEMS NOMINAL",
      message: "Cross-sensor validation confirms genuine propulsion health baseline.",
      time_ago: "Just now",
      timestamp: new Date().toISOString(),
    },
    {
      id: "alt-2",
      level: "INFO",
      title: "VIBRATION & COMBUSTION NOMINAL",
      message: "Dynamic harmonics within standard rotational cruise envelope.",
      time_ago: "2 min ago",
      timestamp: new Date(Date.now() - 120000).toISOString(),
    },
  ],
  fault_label: "Normal",
  scenario: "Normal",
};

export default function Home() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [currentView, setCurrentView] = useState<NavView>("dashboard");
  const [selectedEngine, setSelectedEngine] = useState<string>("UAV_ENG_001");
  const [activeScenario, setActiveScenario] = useState<string>("Normal");
  const [payload, setPayload] = useState<UnifiedTelemetryPayload>(DEFAULT_PAYLOAD);

  const wsRef = useRef<WebSocket | null>(null);

  // Sync with browser hash on initial mount and hashchange
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.replace("#", "").toLowerCase() as NavView;
      const validViews: NavView[] = [
        "dashboard",
        "telemetry",
        "diagnostics",
        "rul",
        "regression",
        "maintenance",
        "alerts",
      ];
      if (validViews.includes(hash)) {
        setCurrentView(hash);
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  const handleNavigate = (view: NavView) => {
    setCurrentView(view);
    window.location.hash = view;
  };

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

  // Connect to Unified Telemetry WebSocket (Continuous 1 Hz Stream)
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
          if (raw.prognostics && raw.sensor_list) {
            setPayload(raw);
            if (raw.scenario) {
              setActiveScenario(raw.scenario);
            }
          }
        } catch (err) {
          console.error("Error parsing telemetry frame", err);
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

  const activeAlertsCount = payload.alerts
    ? payload.alerts.filter((a) => a.level === "ALERT" || a.level === "CAUTION").length
    : 0;

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
          {/* TOP MISSION HEADER */}
          <Header
            userEmail={currentUser.email || "Operator"}
            isConnected={isConnected}
            vehicleId={selectedEngine}
            missionId={payload.vehicle?.mission_id || "ISR_PATROL_27"}
            altitude={payload.vehicle?.altitude || 15000}
            throttle={payload.vehicle?.throttle || 75}
            remainingTimeStr={payload.prognostics?.remaining_time_str || "01:57:32"}
            onLogout={handleLogout}
          />

          {/* MAIN GCS WORKSPACE (SIDEBAR + ACTIVE DETAIL VIEW) */}
          <div className="gcs-workspace-layout">
            {/* Operational Navigation Sidebar */}
            <Sidebar
              currentView={currentView}
              onSelectView={handleNavigate}
              selectedEngine={selectedEngine}
              onSelectEngine={setSelectedEngine}
              activeAlertCount={activeAlertsCount}
            />

            {/* Active Operational View */}
            <main id="app-main" className="gcs-view-area">
              {currentView === "dashboard" && (
                <MainDashboardView
                  payload={payload}
                  activeScenario={activeScenario}
                  onInjectScenario={handleInjectScenario}
                  onNavigate={handleNavigate}
                />
              )}

              {currentView === "telemetry" && (
                <LiveTelemetryView payload={payload} />
              )}

              {currentView === "diagnostics" && (
                <DiagnosticsView payload={payload} />
              )}

              {currentView === "rul" && (
                <RulPrognosticsView payload={payload} />
              )}

              {currentView === "regression" && (
                <RegressionTrendsView payload={payload} />
              )}

              {currentView === "maintenance" && (
                <MaintenanceView payload={payload} />
              )}

              {currentView === "alerts" && (
                <AlertsView
                  alerts={payload.alerts || []}
                  activeScenario={activeScenario}
                  onInjectScenario={handleInjectScenario}
                />
              )}
            </main>
          </div>
        </div>
      )}
    </>
  );
}

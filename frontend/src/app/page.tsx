"use client";

import React, { useEffect, useRef, useState } from "react";
import { supabase } from "@/lib/supabase";
import { TelemetryData } from "@/types/telemetry";
import AuthScreen from "@/components/AuthScreen";
import Header from "@/components/Header";
import HealthPanel from "@/components/HealthPanel";
import DigitalTwinCenterpiece from "@/components/DigitalTwinCenterpiece";
import TelemetryGauges from "@/components/TelemetryGauges";
import TelemetryChart from "@/components/TelemetryChart";
import SensorDiagnosisPanel from "@/components/SensorDiagnosisPanel";
import DiagnosisPanel from "@/components/DiagnosisPanel";
import RulPrognosticsPanel from "@/components/RulPrognosticsPanel";

export default function Home() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isRulView, setIsRulView] = useState(false);
  const [telemetry, setTelemetry] = useState<TelemetryData | null>(null);
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

  // Check initial Supabase auth session
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

  // Connect to Primary Telemetry WebSocket
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
          const data: TelemetryData = JSON.parse(event.data);
          setTelemetry(data);
          if (data.fault_label) {
            setActiveScenario(data.fault_label);
          }
        } catch (err) {
          console.error("Error parsing telemetry message", err);
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
    return null; // Avoid flicker before session is read
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
        <>
          <Header
            userEmail={currentUser.email || "Operator"}
            isConnected={isConnected}
            isRulView={isRulView}
            onToggleRulView={() => setIsRulView((prev) => !prev)}
            onLogout={handleLogout}
          />

          <main id="app-main">
            {/* Main Dashboard View */}
            <div
              className={`main-dashboard-content ${isRulView ? "hidden" : ""}`}
              id="main-dashboard"
            >
              {/* Top Operational Deck */}
              <div className="top-deck">
                <HealthPanel telemetry={telemetry} />
                <DigitalTwinCenterpiece
                  telemetry={telemetry}
                  activeScenario={activeScenario}
                  onInjectScenario={handleInjectScenario}
                />
              </div>

              {/* Split Deck */}
              <div className="split-deck">
                <div className="split-col">
                  <TelemetryGauges telemetry={telemetry} />
                  <TelemetryChart telemetry={telemetry} />
                  <SensorDiagnosisPanel telemetry={telemetry} />
                </div>
                <div className="split-col">
                  <DiagnosisPanel telemetry={telemetry} />
                </div>
              </div>
            </div>

            {/* RUL Prognostics View */}
            <RulPrognosticsPanel isVisible={isRulView} />
          </main>
        </>
      )}
    </>
  );
}

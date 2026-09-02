"use client";

import React, { useEffect, useRef, useState } from "react";
import { Chart, registerables } from "chart.js";
import { RulTickData, RulEngineListMsg, RulResetMsg } from "@/types/telemetry";

Chart.register(...registerables);

interface RulPrognosticsPanelProps {
  isVisible: boolean;
}

export default function RulPrognosticsPanel({ isVisible }: RulPrognosticsPanelProps) {
  const [engineUnits, setEngineUnits] = useState<number[]>([]);
  const [selectedUnit, setSelectedUnit] = useState<number>(1);
  const [predictedRul, setPredictedRul] = useState<number | null>(null);
  const [actualRul, setActualRul] = useState<number | null>(null);
  const [absError, setAbsError] = useState<string>("--");
  const [cycleCounter, setCycleCounter] = useState<number>(0);
  const [logText, setLogText] = useState<string>("Connecting to RUL Prognostics stream...");
  const [badgeState, setBadgeState] = useState<{
    text: string;
    bg: string;
    color: string;
    border: string;
  }>({
    text: "LSTM AI",
    bg: "rgba(168, 85, 247, 0.2)",
    color: "var(--accent-purple)",
    border: "var(--accent-purple)",
  });

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartRef = useRef<Chart | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const labelsRef = useRef<number[]>([]);
  const actualDataRef = useRef<number[]>([]);
  const predictedDataRef = useRef<(number | null)[]>([]);

  // Initialize Chart
  useEffect(() => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labelsRef.current,
        datasets: [
          {
            label: "Actual RUL",
            data: actualDataRef.current,
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56, 189, 248, 0.1)",
            tension: 0.3,
            borderWidth: 2.5,
            pointRadius: 0,
            fill: true,
          },
          {
            label: "LSTM Predicted RUL",
            data: predictedDataRef.current,
            borderColor: "#a855f7",
            backgroundColor: "rgba(168, 85, 247, 0.1)",
            tension: 0.3,
            borderWidth: 2.5,
            pointRadius: 0,
            borderDash: [6, 3],
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: {
            labels: {
              color: "#94a3b8",
              font: { family: "Inter", size: 11 },
            },
          },
        },
        scales: {
          x: {
            title: { display: true, text: "Cycle", color: "#64748b" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: {
              color: "#64748b",
              font: { family: "JetBrains Mono", size: 10 },
              maxTicksLimit: 20,
            },
          },
          y: {
            title: { display: true, text: "RUL (Cycles)", color: "#64748b" },
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: {
              color: "#64748b",
              font: { family: "JetBrains Mono", size: 10 },
            },
            min: 0,
          },
        },
      },
    });

    chartRef.current = chart;

    return () => {
      chart.destroy();
      chartRef.current = null;
    };
  }, []);

  // Connect WebSocket to /ws/rul
  useEffect(() => {
    let reconnectTimeout: NodeJS.Timeout;

    const connectRulWebSocket = () => {
      const wsHost =
        process.env.NEXT_PUBLIC_WS_URL ||
        (typeof window !== "undefined"
          ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:8000`
          : "ws://localhost:8000");
      const wsUrl = `${wsHost}/ws/rul`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setLogText("Connected to RUL Prognostics stream.");
        // Request engine 1 by default
        ws.send(JSON.stringify({ unit: selectedUnit }));
      };

      ws.onmessage = (event) => {
        try {
          const data: RulTickData | RulEngineListMsg | RulResetMsg = JSON.parse(event.data);

          if (data.type === "engine_list") {
            setEngineUnits(data.units);
            return;
          }

          if (data.type === "reset") {
            labelsRef.current.length = 0;
            actualDataRef.current.length = 0;
            predictedDataRef.current.length = 0;
            if (chartRef.current) chartRef.current.update();
            setPredictedRul(null);
            setActualRul(null);
            setAbsError("--");
            setLogText(`Loading engine unit ${data.unit}...`);
            return;
          }

          if (data.type === "rul_tick") {
            const cycle = data.cycle;
            const actual = data.actual_rul;
            const predicted = data.predicted_rul;
            const err =
              predicted !== null ? Math.abs(actual - predicted).toFixed(1) : "--";

            labelsRef.current.push(cycle);
            actualDataRef.current.push(actual);
            predictedDataRef.current.push(predicted !== null ? predicted : null);

            // Keep max 300 points
            if (labelsRef.current.length > 300) {
              labelsRef.current.shift();
              actualDataRef.current.shift();
              predictedDataRef.current.shift();
            }

            if (chartRef.current) chartRef.current.update();

            setCycleCounter(cycle);
            setPredictedRul(predicted);
            setActualRul(actual);
            setAbsError(err);

            if (predicted !== null && predicted < 30) {
              setBadgeState({
                text: "CRITICAL RUL",
                bg: "rgba(239, 68, 68, 0.2)",
                color: "var(--accent-rose)",
                border: "var(--accent-rose)",
              });
            } else if (predicted !== null && predicted < 60) {
              setBadgeState({
                text: "LOW RUL",
                bg: "rgba(245, 158, 11, 0.2)",
                color: "var(--accent-amber)",
                border: "var(--accent-amber)",
              });
            } else {
              setBadgeState({
                text: "LSTM AI",
                bg: "rgba(168, 85, 247, 0.2)",
                color: "var(--accent-purple)",
                border: "var(--accent-purple)",
              });
            }

            setLogText(
              `Cycle ${cycle} | Actual: ${actual.toFixed(0)} | Pred: ${predicted !== null ? predicted.toFixed(1) : "buffering"} | Err: ${err}`
            );
          }
        } catch (e) {
          // ignore parse err
        }
      };

      ws.onclose = () => {
        setLogText("RUL stream disconnected. Reconnecting...");
        reconnectTimeout = setTimeout(connectRulWebSocket, 3000);
      };
    };

    connectRulWebSocket();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [selectedUnit]);

  const handleSelectEngine = (unitId: number) => {
    setSelectedUnit(unitId);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ unit: unitId }));
    }
  };

  return (
    <div className={`rul-panel-wrapper ${isVisible ? "visible" : ""}`} id="rul-panel">
      <div className="rul-hero">
        {/* Left: Hourglass Logo & Big RUL Number */}
        <div className="panel rul-logo-panel">
          <div className="panel-header" style={{ width: "100%" }}>
            <span className="panel-title">
              <span>⏳</span> Remaining Time
            </span>
            <span
              className="status-badge-lg"
              id="rul-status-badge"
              style={{
                background: badgeState.bg,
                color: badgeState.color,
                border: `1px solid ${badgeState.border}`,
              }}
            >
              {badgeState.text}
            </span>
          </div>

          <svg
            className="rul-hourglass-svg"
            viewBox="0 0 100 100"
            xmlns="http://www.w3.org/2000/svg"
          >
            <defs>
              <linearGradient id="hgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#a855f7" />
                <stop offset="100%" stopColor="#38bdf8" />
              </linearGradient>
            </defs>
            {/* Top plate */}
            <rect x="20" y="8" width="60" height="5" rx="2" fill="url(#hgGrad)" opacity="0.9" />
            {/* Bottom plate */}
            <rect x="20" y="87" width="60" height="5" rx="2" fill="url(#hgGrad)" opacity="0.9" />
            {/* Top glass */}
            <path
              d="M28 13 L28 35 L50 55 L72 35 L72 13 Z"
              fill="rgba(168,85,247,0.08)"
              stroke="url(#hgGrad)"
              strokeWidth="2"
            />
            {/* Bottom glass */}
            <path
              d="M28 87 L28 65 L50 45 L72 65 L72 87 Z"
              fill="rgba(168,85,247,0.08)"
              stroke="url(#hgGrad)"
              strokeWidth="2"
            />
            {/* Sand top */}
            <path
              d="M35 13 L35 30 L50 45 L65 30 L65 13 Z"
              fill="rgba(168,85,247,0.15)"
            >
              <animate
                attributeName="d"
                dur="3s"
                repeatCount="indefinite"
                values="M35 13 L35 30 L50 45 L65 30 L65 13 Z;M35 13 L35 22 L50 37 L65 22 L65 13 Z;M35 13 L35 30 L50 45 L65 30 L65 13 Z"
              />
            </path>
            {/* Sand bottom */}
            <path
              d="M38 87 L38 78 L50 65 L62 78 L62 87 Z"
              fill="rgba(56,189,248,0.2)"
            >
              <animate
                attributeName="d"
                dur="3s"
                repeatCount="indefinite"
                values="M38 87 L38 78 L50 65 L62 78 L62 87 Z;M35 87 L35 70 L50 57 L65 70 L65 87 Z;M38 87 L38 78 L50 65 L62 78 L62 87 Z"
              />
            </path>
            {/* Falling stream */}
            <line
              x1="50"
              y1="45"
              x2="50"
              y2="65"
              stroke="url(#hgGrad)"
              strokeWidth="1.5"
              strokeDasharray="3,3"
            >
              <animate
                attributeName="stroke-dashoffset"
                from="0"
                to="-12"
                dur="0.8s"
                repeatCount="indefinite"
              />
            </line>
          </svg>

          <div className="rul-big-number" id="rul-big-val">
            {predictedRul !== null ? predictedRul.toFixed(0) : "--"}
          </div>
          <div className="rul-big-label">Predicted RUL (Cycles)</div>
          <div style={{ marginTop: "0.5rem" }}>
            <div className="rul-big-label">ENGINE UNIT</div>
            <div className="rul-engine-selector" id="rul-engine-selector">
              {engineUnits.map((u) => (
                <button
                  key={u}
                  className={`rul-engine-btn ${selectedUnit === u ? "active" : ""}`}
                  onClick={() => handleSelectEngine(u)}
                >
                  E{u}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Center: Live RUL Chart */}
        <div className="panel rul-chart-panel">
          <div className="panel-header">
            <span className="panel-title">
              <span>📈</span> Actual vs Predicted RUL — CMAPSS FD001 Live Inference
            </span>
            <span
              className="metric-tag"
              style={{
                fontSize: "0.75rem",
                fontFamily: "'JetBrains Mono', monospace",
              }}
              id="rul-cycle-counter"
            >
              CYCLE: {cycleCounter}
            </span>
          </div>
          <div className="rul-chart-container">
            <canvas id="rulChart" ref={canvasRef}></canvas>
          </div>
        </div>

        {/* Right: RUL Metrics */}
        <div className="panel">
          <div className="panel-header">
            <span className="panel-title">
              <span>🧠</span> LSTM Prognostic Metrics
            </span>
          </div>
          <div className="rul-metrics-grid">
            <div className="rul-metric-card">
              <div className="rul-metric-label">Predicted RUL</div>
              <div className="rul-metric-val" id="rul-m-predicted">
                {predictedRul !== null ? predictedRul.toFixed(1) : "--"}
              </div>
            </div>
            <div className="rul-metric-card">
              <div className="rul-metric-label">Actual RUL</div>
              <div
                className="rul-metric-val"
                id="rul-m-actual"
                style={{ color: "var(--accent-cyan)" }}
              >
                {actualRul !== null ? actualRul.toFixed(1) : "--"}
              </div>
            </div>
            <div className="rul-metric-card">
              <div className="rul-metric-label">Abs Error</div>
              <div
                className="rul-metric-val"
                id="rul-m-error"
                style={{ color: "var(--accent-amber)" }}
              >
                {absError}
              </div>
            </div>
            <div className="rul-metric-card">
              <div className="rul-metric-label">Model MAE</div>
              <div className="rul-metric-val" id="rul-m-mae">
                10.08
              </div>
            </div>
            <div className="rul-metric-card">
              <div className="rul-metric-label">Window Size</div>
              <div className="rul-metric-val" id="rul-m-window">
                30
              </div>
            </div>
            <div className="rul-metric-card">
              <div className="rul-metric-label">Sensors Used</div>
              <div className="rul-metric-val" id="rul-m-sensors">
                15
              </div>
            </div>
          </div>
          <div className="diag-log-container" style={{ marginTop: "0.85rem" }}>
            <span style={{ color: "var(--accent-purple)", fontWeight: 700 }}>
              RUL LOG:
            </span>
            <span id="rul-log-text">{logText}</span>
          </div>
          <div style={{ marginTop: "0.85rem" }}>
            <div
              className="advisory-box"
              id="rul-advisory"
              style={{ borderLeftColor: "var(--accent-purple)" }}
            >
              <div
                className="advisory-title"
                style={{ color: "var(--accent-purple)" }}
              >
                ⏳ CMAPSS FD001 Prognostic Dataset
              </div>
              <div className="advisory-desc">
                The LSTM model was trained on the NASA C-MAPSS turbofan engine
                degradation dataset. It predicts Remaining Useful Life from a rolling
                30-cycle sensor window. RUL is clipped at 125 cycles.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

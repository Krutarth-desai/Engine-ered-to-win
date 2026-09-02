"use client";

import React, { useEffect, useRef } from "react";
import { Chart, registerables } from "chart.js";
import { TelemetryData } from "@/types/telemetry";

Chart.register(...registerables);

interface TelemetryChartProps {
  telemetry: TelemetryData | null;
}

export default function TelemetryChart({ telemetry }: TelemetryChartProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstanceRef = useRef<Chart | null>(null);
  const chartLabelsRef = useRef<string[]>([]);
  const dataCHTRef = useRef<number[]>([]);
  const dataEGTRef = useRef<number[]>([]);
  const dataOilTRef = useRef<number[]>([]);

  useEffect(() => {
    if (!canvasRef.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: chartLabelsRef.current,
        datasets: [
          {
            label: "CHT (°C)",
            data: dataCHTRef.current,
            borderColor: "#38bdf8",
            backgroundColor: "rgba(56, 189, 248, 0.1)",
            tension: 0.3,
            borderWidth: 2,
            pointRadius: 0,
          },
          {
            label: "EGT (°C)",
            data: dataEGTRef.current,
            borderColor: "#ef4444",
            backgroundColor: "transparent",
            tension: 0.3,
            borderWidth: 2,
            pointRadius: 0,
          },
          {
            label: "Oil Temp (°C)",
            data: dataOilTRef.current,
            borderColor: "#f59e0b",
            backgroundColor: "transparent",
            tension: 0.3,
            borderWidth: 2,
            pointRadius: 0,
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
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: {
              color: "#64748b",
              font: { family: "JetBrains Mono", size: 10 },
            },
          },
          y: {
            grid: { color: "rgba(255, 255, 255, 0.05)" },
            ticks: {
              color: "#64748b",
              font: { family: "JetBrains Mono", size: 10 },
            },
          },
        },
      },
    });

    chartInstanceRef.current = chart;

    return () => {
      chart.destroy();
      chartInstanceRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!telemetry || !chartInstanceRef.current) return;

    const maxDataPoints = 30;
    const timeLabel = new Date(telemetry.timestamp).toLocaleTimeString([], {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

    if (chartLabelsRef.current.length >= maxDataPoints) {
      chartLabelsRef.current.shift();
      dataCHTRef.current.shift();
      dataEGTRef.current.shift();
      dataOilTRef.current.shift();
    }

    chartLabelsRef.current.push(timeLabel);
    dataCHTRef.current.push(telemetry.cht_c);
    dataEGTRef.current.push(telemetry.egt_c);
    dataOilTRef.current.push(telemetry.oil_temperature_c);

    chartInstanceRef.current.update();
  }, [telemetry]);

  return (
    <div className="panel">
      <div className="panel-header">
        <span className="panel-title">Real-Time Thermal & Combustion Dynamics</span>
        <span className="metric-tag">Live 30-Second Buffer</span>
      </div>
      <div className="chart-container">
        <canvas id="telemetryChart" ref={canvasRef}></canvas>
      </div>
    </div>
  );
}

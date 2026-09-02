"use client";

import React, { useEffect, useRef } from "react";
import Chart from "chart.js/auto";
import { TrajectoryPoint } from "../types/telemetry";

interface RulTrajectoryChartProps {
  trajectory: TrajectoryPoint[];
  currentCycle: number;
  currentActualRul: number;
  currentPredictedRul: number;
}

export default function RulTrajectoryChart({
  trajectory,
  currentCycle,
  currentActualRul,
  currentPredictedRul,
}: RulTrajectoryChartProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const chartInstanceRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;

    const labels = trajectory.map((pt) => `C${pt.cycle}`);
    const actualData = trajectory.map((pt) => pt.actual_rul);
    const predictedData = trajectory.map((pt) => pt.predicted_rul);

    if (chartInstanceRef.current) {
      chartInstanceRef.current.data.labels = labels;
      chartInstanceRef.current.data.datasets[0].data = actualData;
      chartInstanceRef.current.data.datasets[1].data = predictedData;
      chartInstanceRef.current.update("none");
      return;
    }

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    chartInstanceRef.current = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Actual RUL (Ground Truth)",
            data: actualData,
            borderColor: "#10b981", // Emerald Green
            backgroundColor: "transparent",
            borderWidth: 2.5,
            pointRadius: 0,
            pointHoverRadius: 4,
            tension: 0.1,
          },
          {
            label: "LSTM Predicted RUL",
            data: predictedData,
            borderColor: "#38bdf8", // Sky Blue
            borderDash: [6, 4],
            backgroundColor: "rgba(56, 189, 248, 0.05)",
            borderWidth: 2,
            pointRadius: (context) => {
              // Highlight the last point (current operating cycle)
              return context.dataIndex === actualData.length - 1 ? 6 : 0;
            },
            pointBackgroundColor: "#38bdf8",
            pointBorderColor: "#ffffff",
            pointBorderWidth: 2,
            tension: 0.2,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          legend: {
            display: true,
            position: "top",
            labels: {
              color: "#94a3b8",
              font: { family: "monospace", size: 11 },
              boxWidth: 16,
            },
          },
          tooltip: {
            backgroundColor: "rgba(15, 23, 42, 0.95)",
            titleColor: "#38bdf8",
            bodyColor: "#f8fafc",
            borderColor: "rgba(56, 189, 248, 0.3)",
            borderWidth: 1,
            padding: 8,
            titleFont: { family: "monospace", weight: "bold" },
            bodyFont: { family: "monospace" },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(255, 255, 255, 0.04)" },
            ticks: {
              color: "#64748b",
              font: { family: "monospace", size: 10 },
              maxTicksLimit: 12,
            },
            title: {
              display: true,
              text: "ENGINE OPERATING CYCLES",
              color: "#64748b",
              font: { size: 10, family: "monospace" },
            },
          },
          y: {
            min: 0,
            max: 250,
            grid: { color: "rgba(255, 255, 255, 0.04)" },
            ticks: {
              color: "#64748b",
              font: { family: "monospace", size: 10 },
              stepSize: 50,
            },
            title: {
              display: true,
              text: "RUL (CYCLES)",
              color: "#64748b",
              font: { size: 10, family: "monospace" },
            },
          },
        },
      },
    });

    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
        chartInstanceRef.current = null;
      }
    };
  }, [trajectory]);

  return (
    <div className="panel rul-trajectory-panel">
      <div className="panel-header">
        <div className="panel-title">
          <strong>ACTUAL VS PREDICTED RUL TRAJECTORY</strong>
        </div>
        <div className="trajectory-current-badge">
          <span><strong>CURRENT: CYCLE {currentCycle}</strong></span>
          <span className="bullet">●</span>
          <span className="text-cyan"><strong>RUL: {Math.round(currentPredictedRul)}</strong></span>
        </div>
      </div>

      {/* Chart Canvas Area */}
      <div className="chart-wrapper-trajectory">
        <canvas ref={canvasRef} />
      </div>

      {/* Degradation Zones Strip Underneath */}
      <div className="degradation-zones-strip">
        <div className="zone-bar-segment zone-healthy">
          <span className="zone-bar-title">HEALTHY</span>
          <span className="zone-bar-range">125 - 250 CYCLES</span>
        </div>
        <div className="zone-bar-segment zone-degrading">
          <span className="zone-bar-title">DEGRADING</span>
          <span className="zone-bar-range">50 - 125 CYCLES</span>
        </div>
        <div className="zone-bar-segment zone-critical">
          <span className="zone-bar-title">CRITICAL</span>
          <span className="zone-bar-range">15 - 50 CYCLES</span>
        </div>
        <div className="zone-bar-segment zone-failure">
          <span className="zone-bar-title">FAILURE</span>
          <span className="zone-bar-range">0 - 15 CYCLES</span>
        </div>
      </div>
    </div>
  );
}

import asyncio
import json
import numpy as np
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="MALE UAV Digital Twin Telemetry Server")

# Allow CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AeroTwin | MALE UAV Aero Piston Engine Digital Twin GCS</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #F3F0E9;
            --bg-surface: #E8E4DA;
            --bg-glass: rgba(255, 252, 245, 0.60);
            --border-glass: rgba(70, 65, 55, 0.10);
            --border-subtle: rgba(70, 65, 55, 0.07);
            --accent-amber: #C47A3C;
            --accent-blue: #4A607A;
            --accent-emerald: #4F8068;
            --accent-warn: #B88A45;
            --accent-rose: #B85C52;
            --text-primary: #292722;
            --text-secondary: #69645B;
            --text-muted: #918B80;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 15% 15%, rgba(220, 212, 198, 0.35) 0px, transparent 50%),
                radial-gradient(at 85% 85%, rgba(210, 202, 188, 0.40) 0px, transparent 50%),
                linear-gradient(rgba(70, 65, 55, 0.045) 1px, transparent 1px),
                linear-gradient(90deg, rgba(70, 65, 55, 0.045) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 32px 32px, 32px 32px;
            background-attachment: fixed;
            color: var(--text-primary);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background: rgba(243, 240, 233, 0.85);
            backdrop-filter: blur(20px) saturate(110%);
            -webkit-backdrop-filter: blur(20px) saturate(110%);
            border-bottom: 1px solid var(--border-glass);
            padding: 0.85rem 1.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .logo-badge {
            background: rgba(41, 39, 34, 0.90);
            border: 1px solid rgba(70, 65, 55, 0.15);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-family: 'Chakra Petch', sans-serif;
            font-weight: 700;
            font-size: 1.05rem;
            letter-spacing: 1.5px;
            color: #F3F0E9;
        }

        .brand-title {
            font-family: 'Chakra Petch', sans-serif;
            font-size: 1.3rem;
            font-weight: 750;
            letter-spacing: 0.5px;
            color: #1E2022;
        }

        .brand-subtitle {
            font-size: 0.75rem;
            color: var(--accent-amber);
            letter-spacing: 1px;
            text-transform: uppercase;
            font-weight: 600;
        }

        .mission-status-bar {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(79, 128, 104, 0.10);
            color: var(--accent-emerald);
            border: 1px solid rgba(79, 128, 104, 0.25);
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: currentColor;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        .metric-tag {
            color: #69645B;
            font-weight: 500;
        }
        .metric-val {
            color: #1E2022;
            font-weight: 700;
        }

        main {
            padding: 1.25rem 1.75rem 2rem 1.75rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            flex: 1;
            max-width: 1600px;
            margin: 0 auto;
            width: 100%;
        }

        .panel {
            background: var(--bg-glass);
            backdrop-filter: blur(20px) saturate(110%);
            -webkit-backdrop-filter: blur(20px) saturate(110%);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 1.15rem;
            position: relative;
            box-shadow: 0 10px 30px rgba(50, 45, 35, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.65);
            display: flex;
            flex-direction: column;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.85rem;
            border-bottom: 1px solid var(--border-subtle);
            padding-bottom: 0.5rem;
        }

        .panel-title {
            font-family: 'Chakra Petch', sans-serif;
            font-size: 0.96rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #1E2022;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ==================================================== */
        /* 1. TOP — ENGINE HEALTH / STATUS HERO DECK            */
        /* ==================================================== */
        .top-status-deck {
            width: 100%;
            display: flex;
            justify-content: center;
        }

        .status-hero-card {
            background: var(--bg-glass);
            backdrop-filter: blur(20px) saturate(110%);
            -webkit-backdrop-filter: blur(20px) saturate(110%);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 10px 30px rgba(50, 45, 35, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.65);
            display: flex;
            align-items: center;
            align-content: center;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            box-sizing: border-box;
            width: 100%;
        }

        .status-hero-left {
            display: flex;
            align-items: center;
            align-content: center;
            justify-content: center;
            gap: 2.25rem;
            flex-wrap: wrap;
            margin: 0 auto;
            padding: 0;
            max-width: 100%;
        }

        .health-display-hero {
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 0;
            flex-shrink: 0;
        }

        .health-circle-wrapper {
            position: relative;
            width: 140px;
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin: 0;
            padding: 0;
        }

        .health-circle-svg {
            transform: rotate(-90deg);
            width: 100%;
            height: 100%;
            display: block;
        }

        .health-circle-bg {
            fill: none;
            stroke: rgba(70, 65, 55, 0.08);
            stroke-width: 10;
        }

        .health-circle-bar {
            fill: none;
            stroke: var(--accent-emerald);
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 440;
            stroke-dashoffset: 44;
            transition: stroke-dashoffset 0.8s ease, stroke 0.5s ease;
        }

        .health-inner-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            padding: 0;
        }

        .health-number {
            font-family: 'Chakra Petch', sans-serif;
            font-size: 2.4rem;
            font-weight: 750;
            line-height: 1;
            color: #1E2022;
        }

        .health-unit {
            font-size: 0.65rem;
            color: #69645B;
            letter-spacing: 1px;
            margin-top: 4px;
            font-weight: 500;
        }

        .status-hero-meta {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: flex-start;
            gap: 0.85rem;
            margin: 0;
            padding: 0;
        }

        .status-badge-row {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin: 0;
            padding: 0;
        }

        .status-stats-row {
            display: flex;
            align-items: center;
            gap: 1.25rem;
            flex-wrap: wrap;
            margin: 0;
            padding: 0;
        }

        .hero-stat-box {
            background: rgba(255, 255, 255, 0.55);
            padding: 0.65rem 1.15rem;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
            min-width: 150px;
        }

        .meta-label {
            font-size: 0.68rem;
            color: #5C574E;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        .meta-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 2px;
            color: var(--accent-amber);
        }

        .meta-val.hero-val {
            font-size: 1.35rem;
        }

        /* ==================================================== */
        /* 2. CENTER — DIGITAL TWIN MAIN CENTERPIECE            */
        /* ==================================================== */
        .center-twin-deck {
            width: 100%;
        }

        .hero-twin-card {
            min-height: 460px;
        }

        .uav-twin-panel {
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .uav-hud-container {
            flex: 1;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(235, 230, 220, 0.50);
            border-radius: 8px;
            border: 1px solid rgba(70, 65, 55, 0.08);
            min-height: 380px;
            overflow: hidden;
            padding: 1rem;
        }

        /* Tactical HUD Grid and Reticle */
        .uav-hud-grid {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-size: 24px 24px;
            background-image: 
                linear-gradient(to right, rgba(70, 65, 55, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(70, 65, 55, 0.03) 1px, transparent 1px);
            pointer-events: none;
        }

        .uav-hud-radar {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 380px;
            height: 380px;
            transform: translate(-50%, -50%);
            border: 1px dashed rgba(70, 65, 55, 0.10);
            border-radius: 50%;
            pointer-events: none;
        }

        .uav-hud-radar::before {
            content: "";
            position: absolute;
            top: 50%;
            left: 50%;
            width: 220px;
            height: 220px;
            transform: translate(-50%, -50%);
            border: 1px solid rgba(70, 65, 55, 0.06);
            border-radius: 50%;
        }

        .uav-svg-model {
            width: 100%;
            max-height: 330px;
            z-index: 10;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* ==================================================== */
        /* 3. BOTTOM — EXISTING DATA DECK                       */
        /* ==================================================== */
        .bottom-data-deck {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            width: 100%;
        }

        .fault-matrix-panel .scenarios-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.6rem;
        }

        /* SVG Dynamic Styling for Subsystems (Warm Graphite & Sage Green CAD Palette) */
        .uav-hull {
            fill: url(#fuselageGrad);
            stroke: #6B655A;
            stroke-width: 1.5;
            transition: all 0.3s ease;
        }

        .uav-wing-structure {
            fill: url(#wingGrad);
            stroke: #6B655A;
            stroke-width: 1.5;
        }

        .uav-subsystem {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .uav-subsystem:hover {
            opacity: 0.90;
        }

        /* Normal State */
        .part-nominal {
            fill: rgba(79, 128, 104, 0.28);
            stroke: #4F8068;
            stroke-width: 1.5;
        }

        /* Warning State */
        .part-warning {
            fill: rgba(184, 138, 69, 0.35) !important;
            stroke: #B88A45 !important;
            stroke-width: 1.8 !important;
            animation: pulse-warn 1.5s infinite alternate;
        }

        /* Critical / Anomaly State */
        .part-critical {
            fill: rgba(184, 92, 82, 0.40) !important;
            stroke: #B85C52 !important;
            stroke-width: 2.2 !important;
            animation: pulse-crit 1.0s infinite alternate;
        }

        /* Thermal Wave Glow for Overheating */
        .part-thermal {
            fill: rgba(196, 122, 60, 0.40) !important;
            stroke: #C47A3C !important;
            stroke-width: 2.2 !important;
            animation: pulse-thermal 0.9s infinite alternate;
        }

        @keyframes pulse-warn {
            0% { opacity: 0.75; }
            100% { opacity: 1; }
        }

        @keyframes pulse-crit {
            0% { opacity: 0.65; transform: scale(0.99); }
            100% { opacity: 1; transform: scale(1.01); }
        }

        @keyframes pulse-thermal {
            0% { opacity: 0.75; fill: rgba(184, 92, 82, 0.35); }
            100% { opacity: 1; fill: rgba(196, 122, 60, 0.50); }
        }

        /* Spinning Propeller Animation */
        @keyframes spinProp {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .propeller-blade {
            transform-origin: 472px 135px;
            animation: spinProp 0.25s linear infinite;
        }

        /* Anomaly Callout Banner */
        .uav-fault-banner {
            position: absolute;
            bottom: 8px;
            left: 10px;
            right: 10px;
            background: rgba(255, 252, 245, 0.90);
            border: 1px solid var(--border-glass);
            border-radius: 6px;
            padding: 0.4rem 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            backdrop-filter: blur(12px);
            z-index: 20;
        }

        .fault-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }

        .uav-view-controls {
            display: flex;
            gap: 0.35rem;
        }

        .uav-btn-mini {
            background: rgba(255, 255, 255, 0.50);
            border: 1px solid rgba(70, 65, 55, 0.10);
            color: var(--text-secondary);
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.68rem;
            cursor: pointer;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s ease;
        }

        .uav-btn-mini:hover, .uav-btn-mini.active {
            background: rgba(196, 122, 60, 0.12);
            color: var(--text-primary);
            border-color: #C47A3C;
        }

        /* Hover Subsystem Tooltip */
        .uav-tooltip {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(41, 39, 34, 0.95);
            border: 1px solid rgba(70, 65, 55, 0.20);
            border-radius: 6px;
            padding: 0.35rem 0.6rem;
            font-size: 0.72rem;
            font-family: 'JetBrains Mono', monospace;
            color: #F3F0E9;
            pointer-events: none;
            z-index: 30;
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
            display: none;
        }

        /* Telemetry Grid */
        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
        }

        .telemetry-card {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(70, 65, 55, 0.08);
            border-radius: 8px;
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .telemetry-card:hover {
            border-color: #C47A3C;
            background: rgba(255, 255, 255, 0.75);
        }

        .card-top {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }

        .card-name {
            font-size: 0.72rem;
            color: #3F3C34;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 650;
        }

        .card-unit {
            font-size: 0.65rem;
            color: #7E786D;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 500;
        }

        .card-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 700;
            color: #1E2022;
            margin: 0.3rem 0 0.15rem 0;
            letter-spacing: -0.5px;
        }

        .card-progress-bar {
            height: 4px;
            background: rgba(70, 65, 55, 0.08);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 0.35rem;
        }

        .card-progress-fill {
            height: 100%;
            background: var(--accent-amber);
            width: 50%;
            transition: width 0.4s ease, background 0.3s ease;
        }

        /* Fault Injection Simulator Deck */
        .scenarios-container {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }

        .scenario-btn {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(70, 65, 55, 0.08);
            color: #292722;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 650;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
            text-align: left;
        }

        .scenario-btn:hover {
            border-color: var(--accent-amber);
            color: #1E2022;
            background: rgba(196, 122, 60, 0.08);
        }

        .scenario-btn.active {
            border-color: var(--accent-rose);
            background: rgba(184, 92, 82, 0.12);
            color: #1E2022;
        }

        .scenario-btn.active.normal {
            border-color: var(--accent-emerald);
            background: rgba(79, 128, 104, 0.12);
            color: #1E2022;
        }

        .scenario-tag {
            font-size: 0.65rem;
            padding: 0.12rem 0.4rem;
            border-radius: 4px;
            background: rgba(70, 65, 55, 0.08);
            color: #3F3C34;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }

        /* Main Split Deck: Left Half (Sensors & Charts) | Right Half (Digital Twin Diagnostics) */
        .split-deck {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
            align-items: stretch;
        }

        .split-col {
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        @media (max-width: 1200px) {
            .split-deck {
                grid-template-columns: 1fr;
            }
        }

        .chart-container {
            height: 180px;
            position: relative;
        }

        .advisory-box {
            background: rgba(255, 255, 255, 0.55);
            border-radius: 8px;
            border-left: 4px solid var(--accent-emerald);
            border-top: 1px solid rgba(70, 65, 55, 0.08);
            border-right: 1px solid rgba(70, 65, 55, 0.08);
            border-bottom: 1px solid rgba(70, 65, 55, 0.08);
            padding: 0.85rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            transition: all 0.3s ease;
        }

        .advisory-box.warning {
            border-left-color: var(--accent-warn);
            background: rgba(184, 138, 69, 0.08);
        }

        .advisory-box.critical {
            border-left-color: var(--accent-rose);
            background: rgba(184, 92, 82, 0.08);
        }

        .advisory-title {
            font-family: 'Chakra Petch', sans-serif;
            font-size: 0.95rem;
            font-weight: 750;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            text-transform: uppercase;
            color: #1E2022;
        }

        .advisory-desc {
            font-size: 0.8rem;
            color: var(--text-secondary);
            line-height: 1.45;
        }

        .advisory-actions {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.74rem;
            color: var(--accent-amber);
            background: rgba(70, 65, 55, 0.06);
            padding: 0.4rem 0.6rem;
            border-radius: 4px;
            font-weight: 600;
        }

        /* Subsystem PHM & Diagnostics List */
        .diag-section-header {
            font-family: 'Chakra Petch', sans-serif;
            font-size: 0.84rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #1E2022;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .diag-subsystems-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .diag-subsystem-item {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(70, 65, 55, 0.08);
            border-radius: 6px;
            padding: 0.5rem 0.7rem;
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
            transition: all 0.2s ease;
        }

        .diag-subsystem-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.74rem;
        }

        .diag-subsystem-name {
            font-weight: 650;
            color: #292722;
            font-size: 0.76rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .diag-subsystem-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--accent-emerald);
        }

        .diag-progress-bar {
            height: 4px;
            background: rgba(70, 65, 55, 0.08);
            border-radius: 2px;
            overflow: hidden;
        }

        .diag-progress-fill {
            height: 100%;
            background: var(--accent-emerald);
            width: 98%;
            transition: width 0.4s ease, background 0.3s ease;
        }

        .diag-phm-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.55rem;
            margin-top: 0.6rem;
        }

        .diag-phm-card {
            background: rgba(255, 255, 255, 0.45);
            border: 1px solid rgba(70, 65, 55, 0.08);
            border-radius: 6px;
            padding: 0.5rem 0.65rem;
        }

        .diag-phm-label {
            font-size: 0.65rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .diag-phm-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            font-weight: 700;
            margin-top: 0.15rem;
            color: var(--accent-amber);
        }

        .diag-log-container {
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid rgba(70, 65, 55, 0.08);
            border-radius: 6px;
            padding: 0.45rem 0.65rem;
            margin-top: 0.6rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-badge-lg {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-family: 'JetBrains Mono', monospace;
        }

        .badge-optimal { background: rgba(79, 128, 104, 0.12); color: var(--accent-emerald); border: 1px solid rgba(79, 128, 104, 0.3); }
        .badge-warning { background: rgba(184, 138, 69, 0.12); color: var(--accent-warn); border: 1px solid rgba(184, 138, 69, 0.3); }
        .badge-critical { background: rgba(184, 92, 82, 0.12); color: var(--accent-rose); border: 1px solid rgba(184, 92, 82, 0.3); }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <div class="logo-badge">AEROTWIN</div>
            <div>
                <div class="brand-title">MALE UAV PISTON ENGINE DIGITAL TWIN</div>
                <div class="brand-subtitle">Ground Control Station Telemetry & PHM Suite</div>
            </div>
        </div>

        <div class="mission-status-bar">
            <div><span class="metric-tag">VEHICLE:</span> <span class="metric-val" id="val-engine">ENG_001</span></div>
            <div><span class="metric-tag">MISSION:</span> <span class="metric-val" id="val-mission">LIVE_SIM_001</span></div>
            <div><span class="metric-tag">ALTITUDE:</span> <span class="metric-val" id="val-alt">15,000 FT</span></div>
            <div><span class="metric-tag">THROTTLE:</span> <span class="metric-val" id="val-throttle">75%</span></div>
            <div id="conn-badge" class="status-pill">
                <span class="status-dot"></span>
                <span id="conn-text">LIVE 1 Hz</span>
            </div>
        </div>
    </header>

    <main>
        <!-- 1. TOP — EXISTING ENGINE HEALTH / STATUS -->
        <div class="top-status-deck">
            <div class="status-hero-card">
                <div class="status-hero-left">
                    <div class="health-display-hero">
                        <div class="health-circle-wrapper">
                            <svg class="health-circle-svg" viewBox="0 0 160 160">
                                <circle class="health-circle-bg" cx="80" cy="80" r="70"></circle>
                                <circle id="health-circle-bar" class="health-circle-bar" cx="80" cy="80" r="70"></circle>
                            </svg>
                            <div class="health-inner-text">
                                <span id="health-val" class="health-number">100</span>
                                <span class="health-unit">HEALTH INDEX</span>
                            </div>
                        </div>
                    </div>

                    <div class="status-hero-meta">
                        <div class="status-badge-row">
                            <span class="panel-title">Engine Health Index</span>
                            <span id="health-badge" class="status-badge-lg badge-optimal">OPTIMAL</span>
                        </div>
                        <div class="status-stats-row">
                            <div class="hero-stat-box">
                                <div class="meta-label">Est. RUL</div>
                                <div class="meta-val hero-val" id="val-rul">160 hrs</div>
                            </div>
                            <div class="hero-stat-box">
                                <div class="meta-label">Anomaly State</div>
                                <div class="meta-val hero-val" id="val-state" style="color: var(--accent-emerald);">NORMAL</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. CENTER — DIGITAL TWIN ENGINE MAIN VISUAL FOCUS -->
        <div class="center-twin-deck">
            <div class="panel uav-twin-panel hero-twin-card">
                <div class="panel-header">
                    <span class="panel-title">
                        MALE UAV Airframe & Subsystem Mini-Clone
                    </span>
                    <div class="uav-view-controls">
                        <button class="uav-btn-mini active" id="btn-view-all" onclick="setViewMode('full')">Full Drone</button>
                        <button class="uav-btn-mini" id="btn-view-engine" onclick="setViewMode('engine')">Engine Bay</button>
                        <button class="uav-btn-mini" id="btn-view-thermal" onclick="setViewMode('thermal')">Thermal HUD</button>
                    </div>
                </div>

                <div class="uav-hud-container" id="uav-hud">
                    <div class="uav-hud-grid"></div>
                    <div class="uav-hud-radar"></div>
                    <div class="uav-tooltip" id="uav-tooltip">Subsystem Diagnostic</div>

                    <!-- Vector Graphic of MALE UAV Digital Twin -->
                    <svg class="uav-svg-model" id="uav-svg" viewBox="0 0 540 270" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <!-- Engineering CAD Warm Neutral Gradients -->
                            <linearGradient id="fuselageGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#363430" />
                                <stop offset="50%" stop-color="#4D4942" />
                                <stop offset="100%" stop-color="#363430" />
                            </linearGradient>
                            <linearGradient id="wingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                                <stop offset="0%" stop-color="#3F3C36" />
                                <stop offset="50%" stop-color="#545048" />
                                <stop offset="100%" stop-color="#3F3C36" />
                            </linearGradient>
                        </defs>

                        <!-- High-Aspect-Ratio MALE UAV Glider Wings -->
                        <g id="uav-wings" class="uav-wing-structure">
                            <!-- Left Wing -->
                            <polygon points="180,135 210,25 240,25 230,135" fill="url(#wingGrad)" stroke="#6B655A" stroke-width="1.5" />
                            <!-- Right Wing -->
                            <polygon points="180,135 210,245 240,245 230,135" fill="url(#wingGrad)" stroke="#6B655A" stroke-width="1.5" />
                            <!-- Wing Internal Fuel Tanks -->
                            <line x1="200" y1="55" x2="225" y2="55" stroke="rgba(196, 122, 60, 0.40)" stroke-dasharray="3,2" />
                            <line x1="200" y1="215" x2="225" y2="215" stroke="rgba(196, 122, 60, 0.40)" stroke-dasharray="3,2" />
                        </g>

                        <!-- Inverted V-Tail Empennage -->
                        <g id="uav-tail">
                            <polygon points="380,135 440,75 455,75 420,135" fill="#3F3C36" stroke="#6B655A" stroke-width="1.5" />
                            <polygon points="380,135 440,195 455,195 420,135" fill="#3F3C36" stroke="#6B655A" stroke-width="1.5" />
                        </g>

                        <!-- Main Fuselage Contour -->
                        <path class="uav-hull" d="M 60,135 C 75,115 150,118 360,122 L 440,128 L 470,135 L 440,142 L 360,148 C 150,152 75,155 60,135 Z" fill="url(#fuselageGrad)" />

                        <!-- Nose Avionics & CHT Telemetry Probe Subsystem -->
                        <g id="part-avionics" class="uav-subsystem" 
                           onmouseenter="showTooltip('Avionics & Sensor Bay (Nose)', 'Dual-redundant Flight Computer & CHT Sensor Bus')" 
                           onmouseleave="hideTooltip()">
                            <path d="M 60,135 C 68,122 100,122 110,135 C 100,148 68,148 60,135 Z" class="part-nominal" id="svg-part-avionics" />
                            <circle cx="85" cy="135" r="3.5" fill="#C47A3C" />
                            <text x="85" y="112" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">AVIONICS/PROBE</text>
                            <line x1="85" y1="116" x2="85" y2="126" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Mid-Fuselage Payload / Fuel Cell -->
                        <rect x="135" y="126" width="60" height="18" rx="3" fill="rgba(196, 122, 60, 0.12)" stroke="rgba(196, 122, 60, 0.35)" stroke-width="1" />

                        <!-- Coolant Radiator & Ram-Air Intake Subsystem -->
                        <g id="part-radiator" class="uav-subsystem"
                           onmouseenter="showTooltip('Cooling System & Radiator', 'Ram-air cooling scoop, liquid coolant jacket & CHT heat sink')" 
                           onmouseleave="hideTooltip()">
                            <rect x="235" y="115" width="28" height="40" rx="3" class="part-nominal" id="svg-part-radiator" />
                            <line x1="240" y1="119" x2="240" y2="151" stroke="rgba(255,255,255,0.3)" stroke-width="1" />
                            <line x1="249" y1="119" x2="249" y2="151" stroke="rgba(255,255,255,0.3)" stroke-width="1" />
                            <line x1="258" y1="119" x2="258" y2="151" stroke="rgba(255,255,255,0.3)" stroke-width="1" />
                            <text x="249" y="105" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">RADIATOR/COOLING</text>
                            <line x1="249" y1="107" x2="249" y2="114" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Piston Engine Block (4-Cylinder Boxer Engine) -->
                        <g id="part-engine-block" class="uav-subsystem"
                           onmouseenter="showTooltip('Aero Piston Engine Block', '4-Cylinder 4-Stroke Turbocharged Boxer Engine (CHT/EGT core)')" 
                           onmouseleave="hideTooltip()">
                            <!-- Engine Crankcase -->
                            <rect x="280" y="123" width="70" height="24" rx="4" class="part-nominal" id="svg-part-engine" />
                            <!-- Cylinder 1 & 3 (Top) -->
                            <rect x="290" y="112" width="22" height="11" rx="2" class="part-nominal" id="svg-cyl-top1" />
                            <rect x="320" y="112" width="22" height="11" rx="2" class="part-nominal" id="svg-cyl-top2" />
                            <!-- Cylinder 2 & 4 (Bottom) -->
                            <rect x="290" y="147" width="22" height="11" rx="2" class="part-nominal" id="svg-cyl-bot1" />
                            <rect x="320" y="147" width="22" height="11" rx="2" class="part-nominal" id="svg-cyl-bot2" />
                            <text x="315" y="98" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">PISTON ENGINE BLOCK</text>
                            <line x1="315" y1="100" x2="315" y2="111" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Fuel Injection Rail Subsystem -->
                        <g id="part-fuel-system" class="uav-subsystem"
                           onmouseenter="showTooltip('Fuel Injection Rail', 'High-pressure electronic fuel rail & port injectors')" 
                           onmouseleave="hideTooltip()">
                            <path d="M 215,135 L 285,130 M 285,130 L 345,130" stroke="#C47A3C" stroke-width="1.8" fill="none" id="svg-part-fuel" />
                            <circle cx="301" cy="130" r="2.5" fill="#C47A3C" id="svg-inj-1" />
                            <circle cx="331" cy="130" r="2.5" fill="#C47A3C" id="svg-inj-2" />
                            <text x="300" y="174" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">FUEL RAIL</text>
                            <line x1="300" y1="166" x2="300" y2="135" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Lubrication Sump & Oil Lines Subsystem -->
                        <g id="part-oil-system" class="uav-subsystem"
                           onmouseenter="showTooltip('Lubrication & Oil Circuit', 'Oil sump, mechanical scavenge pump & oil cooling lines')" 
                           onmouseleave="hideTooltip()">
                            <rect x="360" y="125" width="26" height="20" rx="3" class="part-nominal" id="svg-part-oil" />
                            <path d="M 350,140 L 360,140" stroke="#4F8068" stroke-width="1.5" />
                            <text x="373" y="174" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">OIL SUMP/PUMP</text>
                            <line x1="373" y1="166" x2="373" y2="147" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Vibration Dampening Mounts -->
                        <g id="part-mounts" class="uav-subsystem"
                           onmouseenter="showTooltip('Engine Dynafocal Mounts', 'Vibration isolation dampers & airframe structural nacelle')" 
                           onmouseleave="hideTooltip()">
                            <circle cx="282" cy="120" r="3" fill="#6E685D" id="svg-mount-1" />
                            <circle cx="282" cy="150" r="3" fill="#6E685D" id="svg-mount-2" />
                            <circle cx="352" cy="120" r="3" fill="#6E685D" id="svg-mount-3" />
                            <circle cx="352" cy="150" r="3" fill="#6E685D" id="svg-mount-4" />
                        </g>

                        <!-- Exhaust Header & Turbocharger -->
                        <g id="part-exhaust" class="uav-subsystem"
                           onmouseenter="showTooltip('Exhaust & Turbocharger', 'Inconel exhaust headers & variable geometry turbine (EGT sensor zone)')" 
                           onmouseleave="hideTooltip()">
                            <path d="M 345,123 C 375,116 395,118 410,124" stroke="#B85C52" stroke-width="2" fill="none" id="svg-part-exhaust" />
                            <circle cx="412" cy="124" r="4.5" fill="#B85C52" opacity="0.8" />
                        </g>

                        <!-- Pusher Propeller Assembly (Rear) -->
                        <g id="part-propeller" class="uav-subsystem"
                           onmouseenter="showTooltip('Pusher Propeller Hub', 'Variable-pitch composite pusher propeller assembly')" 
                           onmouseleave="hideTooltip()">
                            <!-- Propeller Hub -->
                            <circle cx="472" cy="135" r="5" fill="#C47A3C" stroke="#ffffff" stroke-width="1" id="svg-part-propeller" />
                            <!-- Rotating Blade Disc Effect -->
                            <ellipse cx="472" cy="135" rx="3" ry="50" fill="rgba(196, 122, 60, 0.15)" stroke="rgba(196, 122, 60, 0.3)" stroke-dasharray="4,2" />
                            <!-- Propeller Blades with dynamic spin -->
                            <g class="propeller-blade" id="prop-blades">
                                <line x1="472" y1="90" x2="472" y2="180" stroke="#3F3C36" stroke-width="3" stroke-linecap="round" />
                                <circle cx="472" cy="90" r="2.5" fill="#B85C52" />
                                <circle cx="472" cy="180" r="2.5" fill="#B85C52" />
                            </g>
                            <text x="472" y="75" fill="#3F3C34" font-weight="600" font-size="7" font-family="JetBrains Mono" text-anchor="middle">PUSHER PROP</text>
                            <line x1="472" y1="78" x2="472" y2="88" stroke="#6E685D" stroke-width="1.0" />
                        </g>

                        <!-- Anomaly Targeting Crosshair / Hotspot Pin -->
                        <g id="anomaly-reticle" style="display: none;">
                            <circle cx="315" cy="135" r="24" fill="none" stroke="#B85C52" stroke-width="1.5" stroke-dasharray="4,3">
                                <animateTransform attributeName="transform" type="rotate" from="0 315 135" to="360 315 135" dur="4s" repeatCount="indefinite" />
                            </circle>
                            <circle cx="315" cy="135" r="4" fill="#B85C52" />
                        </g>
                    </svg>

                    <!-- Real-Time Anomaly Status Ribbon -->
                    <div class="uav-fault-banner">
                        <div class="fault-indicator" id="uav-fault-text">
                            <span class="status-dot" style="color: var(--accent-emerald);" id="uav-status-dot"></span>
                            <span id="uav-anomaly-title">ALL PROPULSION SUBSYSTEMS NOMINAL</span>
                        </div>
                        <div style="color: var(--text-muted); font-size: 0.68rem; font-family: 'JetBrains Mono', monospace;" id="uav-anomaly-part">
                            PIN: PROPULSION BAY [OK]
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. BOTTOM — EXISTING TELEMETRY, CHARTS & DIAGNOSTICS DATA -->
        <div class="bottom-data-deck">
            <!-- Fault Injection Simulator (Interactive Demo) -->
            <div class="panel fault-matrix-panel">
                <div class="panel-header">
                    <span class="panel-title">Fault Injection Matrix</span>
                    <span class="scenario-tag" id="active-scenario-tag">NORMAL</span>
                </div>
                <div class="scenarios-container">
                    <button class="scenario-btn active normal" onclick="injectScenario('Normal')">
                        <span>Nominal Operation</span>
                        <span class="scenario-tag">HEALTHY</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Overheating')">
                        <span>Cooling / Overheating</span>
                        <span class="scenario-tag">THERMAL</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Injector_Degradation')">
                        <span>Injector Degradation</span>
                        <span class="scenario-tag">COMBUSTION</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Lubrication')">
                        <span>Lubrication Starvation</span>
                        <span class="scenario-tag">HYDRAULIC</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Vibration_Fault')">
                        <span>Abnormal Vibration</span>
                        <span class="scenario-tag">MECHANICAL</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Sensor_Drift')">
                        <span>CHT Sensor Drift</span>
                        <span class="scenario-tag">AVIONICS</span>
                    </button>
                    <button class="scenario-btn" onclick="injectScenario('Misfire')">
                        <span>Cylinder Misfire</span>
                        <span class="scenario-tag">IGNITION</span>
                    </button>
                </div>
            </div>

            <!-- Split Deck: Left Half (Sensors & Waveforms) | Right Half (Digital Twin Predictive Diagnostics) -->
            <div class="split-deck">
                <!-- LEFT HALF: Live Sensor Telemetry Bars & Dynamics Waveform Chart -->
                <div class="split-col">
                    <!-- Live Piston Engine Sensor Telemetry -->
                    <div class="panel">
                        <div class="panel-header">
                            <span class="panel-title">Live Sensor Telemetry Gauges</span>
                            <span class="metric-tag" style="font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;" id="val-timestamp">--:--:--</span>
                        </div>
                        <div class="telemetry-grid">
                            <!-- RPM -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Rotational Speed</span>
                                    <span class="card-unit">RPM</span>
                                </div>
                                <div class="card-val" id="val-rpm">6100</div>
                                <div class="card-progress-bar">
                                    <div id="prog-rpm" class="card-progress-fill" style="width: 75%;"></div>
                                </div>
                            </div>

                            <!-- CHT -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Cylinder Head (CHT)</span>
                                    <span class="card-unit">°C</span>
                                </div>
                                <div class="card-val" id="val-cht">150.0</div>
                                <div class="card-progress-bar">
                                    <div id="prog-cht" class="card-progress-fill" style="width: 60%;"></div>
                                </div>
                            </div>

                            <!-- EGT -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Exhaust Gas (EGT)</span>
                                    <span class="card-unit">°C</span>
                                </div>
                                <div class="card-val" id="val-egt">700.0</div>
                                <div class="card-progress-bar">
                                    <div id="prog-egt" class="card-progress-fill" style="width: 70%;"></div>
                                </div>
                            </div>

                            <!-- Oil Pressure -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Oil Pressure</span>
                                    <span class="card-unit">BAR</span>
                                </div>
                                <div class="card-val" id="val-oil-p">4.30</div>
                                <div class="card-progress-bar">
                                    <div id="prog-oil-p" class="card-progress-fill" style="width: 80%;"></div>
                                </div>
                            </div>

                            <!-- Oil Temp -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Oil Temperature</span>
                                    <span class="card-unit">°C</span>
                                </div>
                                <div class="card-val" id="val-oil-t">95.0</div>
                                <div class="card-progress-bar">
                                    <div id="prog-oil-t" class="card-progress-fill" style="width: 55%;"></div>
                                </div>
                            </div>

                            <!-- Fuel Flow -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Fuel Flow</span>
                                    <span class="card-unit">L/H</span>
                                </div>
                                <div class="card-val" id="val-fuel">18.5</div>
                                <div class="card-progress-bar">
                                    <div id="prog-fuel" class="card-progress-fill" style="width: 65%;"></div>
                                </div>
                            </div>

                            <!-- Vibration -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Vibration RMS</span>
                                    <span class="card-unit">g</span>
                                </div>
                                <div class="card-val" id="val-vib">0.200</div>
                                <div class="card-progress-bar">
                                    <div id="prog-vib" class="card-progress-fill" style="width: 25%;"></div>
                                </div>
                            </div>

                            <!-- Battery -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Bus Voltage</span>
                                    <span class="card-unit">V</span>
                                </div>
                                <div class="card-val" id="val-battery">28.0</div>
                                <div class="card-progress-bar">
                                    <div id="prog-battery" class="card-progress-fill" style="width: 90%;"></div>
                                </div>
                            </div>

                            <!-- Timing -->
                            <div class="telemetry-card">
                                <div class="card-top">
                                    <span class="card-name">Injection Timing</span>
                                    <span class="card-unit">° BTDC</span>
                                </div>
                                <div class="card-val" id="val-timing">22.0</div>
                                <div class="card-progress-bar">
                                    <div id="prog-timing" class="card-progress-fill" style="width: 60%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Dynamic Telemetry Waveform Chart -->
                    <div class="panel">
                        <div class="panel-header">
                            <span class="panel-title">Real-Time Thermal & Combustion Dynamics</span>
                            <span class="metric-tag">Live 30-Second Buffer</span>
                        </div>
                        <div class="chart-container">
                            <canvas id="telemetryChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- RIGHT HALF: Digital Twin Predictive Diagnostics -->
                <div class="split-col">
                    <div class="panel" style="flex: 1;">
                        <div class="panel-header">
                            <span class="panel-title">
                                Digital Twin Predictive Diagnostics
                            </span>
                            <span class="status-badge-lg badge-optimal" id="phm-mode-badge">PHM AI: ACTIVE</span>
                        </div>

                        <!-- AI Diagnostic & Action Advisory Card -->
                        <div id="advisory-card" class="advisory-box">
                            <div class="advisory-title" id="advisory-title">
                                Propulsion Health: Nominal
                            </div>
                            <div class="advisory-desc" id="advisory-desc">
                                All thermal, combustion, and lubrication parameters are operating within baseline tolerances. Digital Twin physics residuals are &lt; 2.5%.
                            </div>
                            <div class="advisory-actions" id="advisory-action">
                                RECOMMENDATION: Continue planned mission profile. No maintenance required.
                            </div>
                        </div>

                        <!-- Subsystem Degradation & Physics Deviations -->
                        <div class="diag-section-header">
                            <span>Subsystem Physics Health & Integrity</span>
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: var(--accent-amber);">Cross-Residual Validation</span>
                        </div>
                        <div class="diag-subsystems-list">
                            <!-- Thermal -->
                            <div class="diag-subsystem-item">
                                <div class="diag-subsystem-header">
                                    <span class="diag-subsystem-name">Thermal Core & Cooling Jacket</span>
                                    <span class="diag-subsystem-val" id="diag-val-thermal">98% NOMINAL</span>
                                </div>
                                <div class="diag-progress-bar">
                                    <div class="diag-progress-fill" id="diag-prog-thermal" style="width: 98%;"></div>
                                </div>
                            </div>

                            <!-- Fuel & Combustion -->
                            <div class="diag-subsystem-item">
                                <div class="diag-subsystem-header">
                                    <span class="diag-subsystem-name">Fuel Rail & Combustion Balance</span>
                                    <span class="diag-subsystem-val" id="diag-val-fuel">97% NOMINAL</span>
                                </div>
                                <div class="diag-progress-bar">
                                    <div class="diag-progress-fill" id="diag-prog-fuel" style="width: 97%;"></div>
                                </div>
                            </div>

                            <!-- Lubrication -->
                            <div class="diag-subsystem-item">
                                <div class="diag-subsystem-header">
                                    <span class="diag-subsystem-name">Lubrication Circuit & Sump</span>
                                    <span class="diag-subsystem-val" id="diag-val-oil">99% NOMINAL</span>
                                </div>
                                <div class="diag-progress-bar">
                                    <div class="diag-progress-fill" id="diag-prog-oil" style="width: 99%;"></div>
                                </div>
                            </div>

                            <!-- Mechanical / Vibration -->
                            <div class="diag-subsystem-item">
                                <div class="diag-subsystem-header">
                                    <span class="diag-subsystem-name">Mechanical Balance & Mounts</span>
                                    <span class="diag-subsystem-val" id="diag-val-vib">96% NOMINAL</span>
                                </div>
                                <div class="diag-progress-bar">
                                    <div class="diag-progress-fill" id="diag-prog-vib" style="width: 96%;"></div>
                                </div>
                            </div>

                            <!-- Avionics & Sensor Channel Fusion -->
                            <div class="diag-subsystem-item">
                                <div class="diag-subsystem-header">
                                    <span class="diag-subsystem-name">Avionics Sensor Channel Fusion</span>
                                    <span class="diag-subsystem-val" id="diag-val-avionics">100% NOMINAL</span>
                                </div>
                                <div class="diag-progress-bar">
                                    <div class="diag-progress-fill" id="diag-prog-avionics" style="width: 100%;"></div>
                                </div>
                            </div>
                        </div>

                        <!-- PHM Prognostics & Maintenance Matrix -->
                        <div class="diag-section-header">
                            <span>PHM Prognostic Matrix</span>
                        </div>
                        <div class="diag-phm-grid">
                            <div class="diag-phm-card">
                                <div class="diag-phm-label">Anomaly Confidence</div>
                                <div class="diag-phm-val" id="diag-stat-conf">99.4%</div>
                            </div>
                            <div class="diag-phm-card">
                                <div class="diag-phm-label">Physics Residual</div>
                                <div class="diag-phm-val" id="diag-stat-residual">&lt; 2.1% RMS</div>
                            </div>
                            <div class="diag-phm-card">
                                <div class="diag-phm-label">Maintenance Priority</div>
                                <div class="diag-phm-val" id="diag-stat-priority" style="color: var(--accent-emerald);">ROUTINE</div>
                            </div>
                            <div class="diag-phm-card">
                                <div class="diag-phm-label">Degradation Trend</div>
                                <div class="diag-phm-val" id="diag-stat-trend" style="color: var(--accent-amber);">STABLE CRUISE</div>
                            </div>
                        </div>

                        <!-- Live PHM Diagnostic Event Stream -->
                        <div class="diag-log-container" id="diag-log-box">
                            <span style="color: var(--accent-amber); font-weight: 700;">PHM LOG:</span>
                            <span id="diag-log-text">Physics-informed digital twin estimation in progress...</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script>
        let ws = null;
        let chart = null;
        const maxDataPoints = 30;
        const chartLabels = [];
        const dataCHT = [];
        const dataEGT = [];
        const dataOilT = [];

        // Setup Chart.js
        function initChart() {
            const ctx = document.getElementById('telemetryChart').getContext('2d');
            chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartLabels,
                    datasets: [
                        {
                            label: 'CHT (°C)',
                            data: dataCHT,
                            borderColor: '#C47A3C',
                            backgroundColor: 'rgba(196, 122, 60, 0.1)',
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 0
                        },
                        {
                            label: 'EGT (°C)',
                            data: dataEGT,
                            borderColor: '#B85C52',
                            backgroundColor: 'transparent',
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 0
                        },
                        {
                            label: 'Oil Temp (°C)',
                            data: dataOilT,
                            borderColor: '#B88A45',
                            backgroundColor: 'transparent',
                            tension: 0.3,
                            borderWidth: 2,
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: false,
                    plugins: {
                        legend: {
                            labels: { color: '#292722', font: { family: 'Inter', size: 11 } }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: 'rgba(70, 65, 55, 0.08)' },
                            ticks: { color: '#69645B', font: { family: 'JetBrains Mono', size: 10 } }
                        },
                        y: {
                            grid: { color: 'rgba(70, 65, 55, 0.08)' },
                            ticks: { color: '#69645B', font: { family: 'JetBrains Mono', size: 10 } }
                        }
                    }
                }
            });
        }

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`;
            
            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                document.getElementById('conn-text').innerText = 'LIVE 1 Hz';
                document.getElementById('conn-badge').style.borderColor = 'rgba(79, 128, 104, 0.25)';
                document.getElementById('conn-badge').style.color = '#4F8068';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            ws.onclose = () => {
                document.getElementById('conn-text').innerText = 'RECONNECTING...';
                document.getElementById('conn-badge').style.borderColor = 'rgba(184, 92, 82, 0.25)';
                document.getElementById('conn-badge').style.color = '#B85C52';
                setTimeout(connectWebSocket, 2000);
            };
        }

        function updateDashboard(data) {
            // Update Text Values
            document.getElementById('val-rpm').innerText = data.rpm.toFixed(0);
            document.getElementById('val-cht').innerText = data.cht_c.toFixed(1);
            document.getElementById('val-egt').innerText = data.egt_c.toFixed(1);
            document.getElementById('val-oil-p').innerText = data.oil_pressure_bar.toFixed(2);
            document.getElementById('val-oil-t').innerText = data.oil_temperature_c.toFixed(1);
            document.getElementById('val-fuel').innerText = data.fuel_flow_lh.toFixed(1);
            document.getElementById('val-vib').innerText = data.vibration_g.toFixed(3);
            document.getElementById('val-battery').innerText = data.battery_voltage_v.toFixed(1);
            document.getElementById('val-timing').innerText = data.injection_timing_deg.toFixed(1);
            document.getElementById('val-timestamp').innerText = new Date(data.timestamp).toLocaleTimeString();

            // Update Progress Fills
            document.getElementById('prog-rpm').style.width = `${Math.min((data.rpm / 7000) * 100, 100)}%`;
            document.getElementById('prog-cht').style.width = `${Math.min((data.cht_c / 250) * 100, 100)}%`;
            document.getElementById('prog-egt').style.width = `${Math.min((data.egt_c / 900) * 100, 100)}%`;
            document.getElementById('prog-oil-p').style.width = `${Math.min((data.oil_pressure_bar / 6) * 100, 100)}%`;
            document.getElementById('prog-oil-t').style.width = `${Math.min((data.oil_temperature_c / 150) * 100, 100)}%`;
            document.getElementById('prog-fuel').style.width = `${Math.min((data.fuel_flow_lh / 30) * 100, 100)}%`;
            document.getElementById('prog-vib').style.width = `${Math.min((data.vibration_g / 1.5) * 100, 100)}%`;

            // Adjust Propeller Spin Speed based on RPM
            const bladeEl = document.getElementById('prop-blades');
            if (bladeEl) {
                const spinPeriod = Math.max(0.08, 60 / Math.max(data.rpm, 1000));
                bladeEl.style.animationDuration = `${spinPeriod.toFixed(2)}s`;
            }

            // Update Health Index Arc
            const health = Math.max(Math.min(data.health_index, 100), 0);
            document.getElementById('health-val').innerText = health.toFixed(0);
            
            const circumference = 2 * Math.PI * 70; // ~440
            const offset = circumference - (health / 100) * circumference;
            const healthBar = document.getElementById('health-circle-bar');
            healthBar.style.strokeDashoffset = offset;

            // Health Badge & RUL
            const healthBadge = document.getElementById('health-badge');
            const rulEl = document.getElementById('val-rul');
            const stateEl = document.getElementById('val-state');
            
            const estRulHours = data.rul !== undefined ? data.rul : Math.round((health / 100) * 160);
            rulEl.innerText = `${estRulHours} hrs`;

            if (health > 85) {
                healthBar.style.stroke = '#4F8068';
                healthBadge.className = 'status-badge-lg badge-optimal';
                healthBadge.innerText = 'OPTIMAL';
                stateEl.innerText = data.fault_label.toUpperCase();
                stateEl.style.color = '#4F8068';
            } else if (health > 60) {
                healthBar.style.stroke = '#B88A45';
                healthBadge.className = 'status-badge-lg badge-warning';
                healthBadge.innerText = 'DEGRADED';
                stateEl.innerText = data.fault_label.toUpperCase();
                stateEl.style.color = '#B88A45';
            } else {
                healthBar.style.stroke = '#B85C52';
                healthBadge.className = 'status-badge-lg badge-critical';
                healthBadge.innerText = 'CRITICAL';
                stateEl.innerText = data.fault_label.toUpperCase();
                stateEl.style.color = '#B85C52';
            }

            // Update UAV Mini-Clone Model Highlighting & Hotspots
            updateUavModelAnomalies(data);

            // Update Advisory Card
            updateAdvisory(data);

            // Update Chart
            const timeLabel = new Date(data.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
            if (chartLabels.length >= maxDataPoints) {
                chartLabels.shift();
                dataCHT.shift();
                dataEGT.shift();
                dataOilT.shift();
            }
            chartLabels.push(timeLabel);
            dataCHT.push(data.cht_c);
            dataEGT.push(data.egt_c);
            dataOilT.push(data.oil_temperature_c);
            chart.update();
        }

        // =========================================================
        // MALE UAV DIGITAL TWIN ANOMALY LOCALIZATION ENGINE
        // =========================================================
        function updateUavModelAnomalies(data) {
            const scenario = data.fault_label;
            const health = data.health_index;
            
            // Subsystem SVG Element References
            const elAvionics = document.getElementById('svg-part-avionics');
            const elRadiator = document.getElementById('svg-part-radiator');
            const elEngine = document.getElementById('svg-part-engine');
            const elCyl1 = document.getElementById('svg-cyl-top1');
            const elCyl2 = document.getElementById('svg-cyl-top2');
            const elCyl3 = document.getElementById('svg-cyl-bot1');
            const elCyl4 = document.getElementById('svg-cyl-bot2');
            const elFuel = document.getElementById('svg-part-fuel');
            const elOil = document.getElementById('svg-part-oil');
            const elExhaust = document.getElementById('svg-part-exhaust');
            const elProp = document.getElementById('svg-part-propeller');
            const elReticle = document.getElementById('anomaly-reticle');
            
            const dotEl = document.getElementById('uav-status-dot');
            const titleEl = document.getElementById('uav-anomaly-title');
            const partEl = document.getElementById('uav-anomaly-part');

            // Reset all parts to nominal base styling
            [elAvionics, elRadiator, elEngine, elCyl1, elCyl2, elCyl3, elCyl4, elOil].forEach(el => {
                if (el) el.className.baseVal = 'part-nominal';
            });
            if (elFuel) elFuel.setAttribute('stroke', '#C47A3C');
            if (elExhaust) elExhaust.setAttribute('stroke', '#B85C52');
            if (elProp) elProp.setAttribute('fill', '#C47A3C');
            [1, 2, 3, 4].forEach(i => {
                const m = document.getElementById(`svg-mount-${i}`);
                if (m) m.setAttribute('fill', '#918B80');
            });

            if (scenario === 'Normal' || health > 90) {
                elReticle.style.display = 'none';
                dotEl.style.color = '#4F8068';
                titleEl.innerText = 'ALL PROPULSION SUBSYSTEMS NOMINAL';
                titleEl.style.color = '#4F8068';
                partEl.innerText = 'PIN: PROPULSION BAY [OK]';
            } 
            else if (scenario === 'Overheating') {
                // Highlight Radiator & Engine Cylinders in Thermal Flare
                if (elRadiator) elRadiator.className.baseVal = 'part-thermal';
                if (elEngine) elEngine.className.baseVal = 'part-thermal';
                if (elCyl1) elCyl1.className.baseVal = 'part-thermal';
                if (elCyl2) elCyl2.className.baseVal = 'part-thermal';
                if (elCyl3) elCyl3.className.baseVal = 'part-thermal';
                if (elCyl4) elCyl4.className.baseVal = 'part-thermal';
                
                positionReticle(280, 135);
                dotEl.style.color = '#B85C52';
                titleEl.innerText = `THERMAL ANOMALY: CHT ${data.cht_c.toFixed(1)}°C / OIL ${data.oil_temperature_c.toFixed(1)}°C`;
                titleEl.style.color = '#C47A3C';
                partEl.innerText = 'HOTSPOT: CYLINDER HEADS & COOLING RADIATOR';
            } 
            else if (scenario === 'Injector_Degradation') {
                // Highlight Fuel Delivery Rail & Injector Nozzles
                if (elFuel) elFuel.setAttribute('stroke', '#B88A45');
                if (elEngine) elEngine.className.baseVal = 'part-warning';
                
                positionReticle(305, 130);
                dotEl.style.color = '#B88A45';
                titleEl.innerText = `COMBUSTION DEGRADATION: FUEL FLOW ${data.fuel_flow_lh.toFixed(1)} L/H`;
                titleEl.style.color = '#B88A45';
                partEl.innerText = 'HOTSPOT: HIGH-PRESSURE FUEL INJECTION RAIL';
            } 
            else if (scenario === 'Lubrication') {
                // Highlight Oil Sump & Lubrication Channels
                if (elOil) elOil.className.baseVal = 'part-critical';
                if (elEngine) elEngine.className.baseVal = 'part-warning';
                
                positionReticle(373, 135);
                dotEl.style.color = '#B85C52';
                titleEl.innerText = `HYDRAULIC ANOMALY: OIL PRESSURE CRITICAL (${data.oil_pressure_bar.toFixed(2)} BAR)`;
                titleEl.style.color = '#B85C52';
                partEl.innerText = 'HOTSPOT: LUBRICATION SUMP & OIL SCAVENGE PUMP';
            } 
            else if (scenario === 'Vibration_Fault') {
                // Highlight Engine Mounts, Crankcase & Propeller Shaft
                if (elProp) elProp.setAttribute('fill', '#B88A45');
                if (elEngine) elEngine.className.baseVal = 'part-warning';
                [1, 2, 3, 4].forEach(i => {
                    const m = document.getElementById(`svg-mount-${i}`);
                    if (m) m.setAttribute('fill', '#B85C52');
                });

                positionReticle(350, 135);
                dotEl.style.color = '#B88A45';
                titleEl.innerText = `MECHANICAL ANOMALY: VIBRATION SPIKE (${data.vibration_g.toFixed(3)} g RMS)`;
                titleEl.style.color = '#B88A45';
                partEl.innerText = 'HOTSPOT: CRANKSHAFT & DYNAFOCAL ENGINE MOUNTS';
            } 
            else if (scenario === 'Sensor_Drift') {
                // Highlight Avionics Nose / CHT Telemetry Harness
                if (elAvionics) elAvionics.className.baseVal = 'part-warning';
                
                positionReticle(85, 135);
                dotEl.style.color = '#B88A45';
                titleEl.innerText = `AVIONICS HARNESS: CHT SENSOR DRIFT DETECTED (${data.cht_c.toFixed(1)}°C)`;
                titleEl.style.color = '#C47A3C';
                partEl.innerText = 'HOTSPOT: NOSE AVIONICS & CHT SENSOR HARNESS';
            } 
            else if (scenario === 'Misfire') {
                // Highlight Cylinder 1 & Exhaust Header
                if (elCyl1) elCyl1.className.baseVal = 'part-critical';
                if (elCyl3) elCyl3.className.baseVal = 'part-warning';
                if (elExhaust) elExhaust.setAttribute('stroke', '#B85C52');
                
                positionReticle(310, 120);
                dotEl.style.color = '#B85C52';
                titleEl.innerText = `IGNITION FAULT: INTERMITTENT CYLINDER MISFIRE`;
                titleEl.style.color = '#B85C52';
                partEl.innerText = 'HOTSPOT: CYLINDER #1 SPARK & EXHAUST RUNNER';
            }
        }

        function positionReticle(cx, cy) {
            const reticle = document.getElementById('anomaly-reticle');
            if (reticle) {
                reticle.style.display = 'block';
                const circles = reticle.querySelectorAll('circle');
                circles.forEach(c => {
                    c.setAttribute('cx', cx);
                    c.setAttribute('cy', cy);
                });
                const anim = reticle.querySelector('animateTransform');
                if (anim) {
                    anim.setAttribute('from', `0 ${cx} ${cy}`);
                    anim.setAttribute('to', `360 ${cx} ${cy}`);
                }
            }
        }

        // View Mode Camera Controller
        function setViewMode(mode) {
            document.querySelectorAll('.uav-btn-mini').forEach(b => b.classList.remove('active'));
            const svg = document.getElementById('uav-svg');
            
            if (mode === 'full') {
                document.getElementById('btn-view-all').classList.add('active');
                svg.style.transform = 'scale(1) translate(0, 0)';
            } else if (mode === 'engine') {
                document.getElementById('btn-view-engine').classList.add('active');
                svg.style.transform = 'scale(1.85) translate(-100px, 0)';
            } else if (mode === 'thermal') {
                document.getElementById('btn-view-thermal').classList.add('active');
                svg.style.transform = 'scale(1.35) translate(-40px, 0)';
            }
        }

        // Tooltip handler
        function showTooltip(title, desc) {
            const tip = document.getElementById('uav-tooltip');
            tip.innerHTML = `<span style="color: var(--accent-amber); font-weight:700;">${title}</span><br><span style="color: #918B80; font-size: 0.65rem;">${desc}</span>`;
            tip.style.display = 'block';
        }

        function hideTooltip() {
            document.getElementById('uav-tooltip').style.display = 'none';
        }

        function updateAdvisory(data) {
            const card = document.getElementById('advisory-card');
            const title = document.getElementById('advisory-title');
            const desc = document.getElementById('advisory-desc');
            const action = document.getElementById('advisory-action');
            const badge = document.getElementById('phm-mode-badge');

            // Elements for Subsystem Diagnostics
            const valThermal = document.getElementById('diag-val-thermal');
            const progThermal = document.getElementById('diag-prog-thermal');
            const valFuel = document.getElementById('diag-val-fuel');
            const progFuel = document.getElementById('diag-prog-fuel');
            const valOil = document.getElementById('diag-val-oil');
            const progOil = document.getElementById('diag-prog-oil');
            const valVib = document.getElementById('diag-val-vib');
            const progVib = document.getElementById('diag-prog-vib');
            const valAvionics = document.getElementById('diag-val-avionics');
            const progAvionics = document.getElementById('diag-prog-avionics');

            // Elements for PHM Matrix
            const statConf = document.getElementById('diag-stat-conf');
            const statResidual = document.getElementById('diag-stat-residual');
            const statPriority = document.getElementById('diag-stat-priority');
            const statTrend = document.getElementById('diag-stat-trend');
            const logText = document.getElementById('diag-log-text');

            // Reset Subsystems to Nominal Baseline
            const setSubsystem = (valEl, progEl, pct, text, color) => {
                if (valEl) {
                    valEl.innerText = text;
                    valEl.style.color = color;
                }
                if (progEl) {
                    progEl.style.width = `${pct}%`;
                    progEl.style.background = color;
                }
            };

            setSubsystem(valThermal, progThermal, 98, '98% NOMINAL', 'var(--accent-emerald)');
            setSubsystem(valFuel, progFuel, 97, '97% NOMINAL', 'var(--accent-emerald)');
            setSubsystem(valOil, progOil, 99, '99% NOMINAL', 'var(--accent-emerald)');
            setSubsystem(valVib, progVib, 96, '96% NOMINAL', 'var(--accent-emerald)');
            setSubsystem(valAvionics, progAvionics, 100, '100% NOMINAL', 'var(--accent-emerald)');

            if (data.fault_label === 'Normal') {
                card.className = 'advisory-box';
                title.innerText = 'Propulsion Health: Nominal';
                desc.innerText = 'All thermal, combustion, and lubrication parameters are operating within baseline tolerances. Digital Twin physics residuals are < 2.5%.';
                action.innerText = 'RECOMMENDATION: Continue planned mission profile. No maintenance required.';
                if (badge) { badge.className = 'status-badge-lg badge-optimal'; badge.innerText = 'PHM AI: OPTIMAL'; }
                if (statConf) statConf.innerText = '99.4%';
                if (statResidual) statResidual.innerText = '< 2.1% RMS';
                if (statPriority) { statPriority.innerText = 'ROUTINE'; statPriority.style.color = 'var(--accent-emerald)'; }
                if (statTrend) { statTrend.innerText = 'STABLE CRUISE'; statTrend.style.color = 'var(--accent-amber)'; }
                if (logText) logText.innerText = 'PHYSICS ENGINE: Telemetry parity matched across 9 sensor channels with zero divergence.';
            } else if (data.fault_label === 'Overheating') {
                card.className = 'advisory-box critical';
                title.innerText = 'ALERT: Engine Overheating Trend Detected';
                desc.innerText = `CHT reached ${data.cht_c.toFixed(1)}°C and Oil Temp reached ${data.oil_temperature_c.toFixed(1)}°C. Physics residual exceeds +35°C thermal model boundary.`;
                action.innerText = 'ACTION: Reduce cruise throttle to 55%. Plan altitude descent for enhanced ram-air cooling. Inspect radiator fins post-flight.';
                if (badge) { badge.className = 'status-badge-lg badge-critical'; badge.innerText = 'PHM AI: CRITICAL ALERT'; }
                setSubsystem(valThermal, progThermal, 28, '28% CRITICAL HEAT', 'var(--accent-rose)');
                setSubsystem(valOil, progOil, 54, '54% HIGH TEMP', 'var(--accent-warn)');
                if (statConf) statConf.innerText = '98.9%';
                if (statResidual) statResidual.innerText = '+38.4°C CHT DIV';
                if (statPriority) { statPriority.innerText = 'URGENT (P1)'; statPriority.style.color = 'var(--accent-rose)'; }
                if (statTrend) { statTrend.innerText = 'HEAT DISSIPATION LOSS'; statTrend.style.color = 'var(--accent-rose)'; }
                if (logText) logText.innerText = `THERMAL ANOMALY: Cylinder jacket heat transfer deficit detected (${data.cht_c.toFixed(1)}°C).`;
            } else if (data.fault_label === 'Injector_Degradation') {
                card.className = 'advisory-box warning';
                title.innerText = 'WARNING: Fuel Injector Delivery Degradation';
                desc.innerText = `Fuel flow elevated (${data.fuel_flow_lh.toFixed(1)} L/h) with abnormal EGT and RPM fluctuations. Flow coefficient dropped 18%.`;
                action.innerText = 'ACTION: Monitor fuel consumption vs endurance margin. Schedule injector ultrasonic cleaning at next turnaround.';
                if (badge) { badge.className = 'status-badge-lg badge-warning'; badge.innerText = 'PHM AI: DEGRADED'; }
                setSubsystem(valFuel, progFuel, 42, '42% FLOW DEVIATION', 'var(--accent-warn)');
                if (statConf) statConf.innerText = '96.8%';
                if (statResidual) statResidual.innerText = '+4.6 L/H BIAS';
                if (statPriority) { statPriority.innerText = 'ACTION REQ'; statPriority.style.color = 'var(--accent-warn)'; }
                if (statTrend) { statTrend.innerText = 'COMBUSTION IMBALANCE'; statTrend.style.color = 'var(--accent-warn)'; }
                if (logText) logText.innerText = `COMBUSTION DIAGNOSTIC: Fuel mass flow residual divergence on rail (+${(data.fuel_flow_lh - 18.5).toFixed(1)} L/h).`;
            } else if (data.fault_label === 'Lubrication') {
                card.className = 'advisory-box critical';
                title.innerText = 'URGENT: Lubrication Starvation & Pressure Loss';
                desc.innerText = `Oil pressure dropped to ${data.oil_pressure_bar.toFixed(2)} bar while friction vibration is climbing (${data.vibration_g.toFixed(3)} g).`;
                action.innerText = 'CRITICAL ADVISORY: Potential bearing wear/pump cavitation. Abort mission if pressure drops below 3.0 bar. Divert to nearest recovery base.';
                if (badge) { badge.className = 'status-badge-lg badge-critical'; badge.innerText = 'PHM AI: HYDRAULIC ALARM'; }
                setSubsystem(valOil, progOil, 18, '18% STARVATION', 'var(--accent-rose)');
                setSubsystem(valVib, progVib, 58, '58% FRICTION RISE', 'var(--accent-warn)');
                if (statConf) statConf.innerText = '99.5%';
                if (statResidual) statResidual.innerText = '-1.85 BAR DEFICIT';
                if (statPriority) { statPriority.innerText = 'EMERGENCY'; statPriority.style.color = 'var(--accent-rose)'; }
                if (statTrend) { statTrend.innerText = 'HYDRODYNAMIC LOSS'; statTrend.style.color = 'var(--accent-rose)'; }
                if (logText) logText.innerText = `HYDRAULIC FAILURE: Main gallery oil pressure collapsed below 3.5 bar margin.`;
            } else if (data.fault_label === 'Vibration_Fault') {
                card.className = 'advisory-box warning';
                title.innerText = 'MECHANICAL ANOMALY: High Vibration Signature';
                desc.innerText = `Spectral energy spikes detected in 1X-2X crankshaft harmonics (${data.vibration_g.toFixed(3)} g RMS). Probable propeller imbalance or mount looseness.`;
                action.innerText = 'ACTION: Avoid resonant RPM bands. Restrict maximum continuous power. Perform mechanical mount inspection.';
                if (badge) { badge.className = 'status-badge-lg badge-warning'; badge.innerText = 'PHM AI: VIBRATION SPIKE'; }
                setSubsystem(valVib, progVib, 25, '25% HARMONIC SPIKE', 'var(--accent-rose)');
                if (statConf) statConf.innerText = '97.6%';
                if (statResidual) statResidual.innerText = `+${(data.vibration_g - 0.2).toFixed(3)}g RMS`;
                if (statPriority) { statPriority.innerText = 'INSPECTION'; statPriority.style.color = 'var(--accent-warn)'; }
                if (statTrend) { statTrend.innerText = 'DYNAMIC UNBALANCE'; statTrend.style.color = 'var(--accent-warn)'; }
                if (logText) logText.innerText = `ROTORDYNAMICS: 1X crankshaft fundamental frequency vibration spike detected.`;
            } else if (data.fault_label === 'Sensor_Drift') {
                card.className = 'advisory-box warning';
                title.innerText = 'AVIONICS ALERT: CHT Sensor Drift / Calibration Error';
                desc.innerText = `CHT reading (${data.cht_c.toFixed(1)}°C) diverges from physics-informed estimation, while EGT & Oil Temp remain normal. Engine is healthy.`;
                action.innerText = 'INTELLIGENT DIAGNOSIS: Sensor failure detected via cross-sensor fusion. Engine safe to operate. Replace CHT probe on return.';
                if (badge) { badge.className = 'status-badge-lg badge-warning'; badge.innerText = 'PHM AI: SENSOR FAULT'; }
                setSubsystem(valAvionics, progAvionics, 35, '35% SENSOR BIAS', 'var(--accent-warn)');
                if (statConf) statConf.innerText = '99.8%';
                if (statResidual) statResidual.innerText = `+${(data.cht_c - 150).toFixed(1)}°C DRIFT`;
                if (statPriority) { statPriority.innerText = 'POST-FLIGHT'; statPriority.style.color = 'var(--accent-amber)'; }
                if (statTrend) { statTrend.innerText = 'SENSOR BIAS ONLY'; statTrend.style.color = 'var(--accent-amber)'; }
                if (logText) logText.innerText = `ANOMALY ISOLATION: Digital Twin neural estimator verified mechanical engine core is 100% healthy.`;
            } else if (data.fault_label === 'Misfire') {
                card.className = 'advisory-box critical';
                title.innerText = 'COMBUSTION INSTABILITY: Intermittent Cylinder Misfire';
                desc.innerText = `Combustion irregularity detected with sudden RPM drops and unburnt exhaust gas temperature dips.`;
                action.innerText = 'ACTION: Check ignition coil & spark plug telemetry. Adjust mixture trim. If misfires persist, abort climb.';
                if (badge) { badge.className = 'status-badge-lg badge-critical'; badge.innerText = 'PHM AI: MISFIRE FAULT'; }
                setSubsystem(valFuel, progFuel, 22, '22% MISFIRE UNSTABLE', 'var(--accent-rose)');
                setSubsystem(valVib, progVib, 45, '45% COMBUSTION ROUGH', 'var(--accent-warn)');
                if (statConf) statConf.innerText = '98.5%';
                if (statResidual) statResidual.innerText = 'ΔRPM -280 / ΔEGT -50°';
                if (statPriority) { statPriority.innerText = 'URGENT'; statPriority.style.color = 'var(--accent-rose)'; }
                if (statTrend) { statTrend.innerText = 'CYLINDER #1 MISFIRE'; statTrend.style.color = 'var(--accent-rose)'; }
                if (logText) logText.innerText = `IGNITION FAULT: Power stroke torque pulsation detected on Cylinder #1.`;
            }
        }

        function injectScenario(scenarioName) {
            // Update button UI
            document.querySelectorAll('.scenario-btn').forEach(btn => {
                btn.classList.remove('active', 'normal');
                if (btn.innerText.includes(scenarioName) || (scenarioName === 'Normal' && btn.innerText.includes('Nominal'))) {
                    btn.classList.add('active');
                    if (scenarioName === 'Normal') btn.classList.add('normal');
                }
            });

            document.getElementById('active-scenario-tag').innerText = scenarioName.toUpperCase();

            // Send command over WebSocket to Python Server
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ scenario: scenarioName }));
            }
        }

        window.onload = () => {
            initChart();
            connectWebSocket();
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the complete interactive MALE UAV Digital Twin GCS Dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)

# Global simulation state
simulation_state = {
    "is_running": True,  # Auto-start for convenience
    "scenario": "Normal",
    "tick": 0,
    "throttle": 75.0,
    "altitude": 15000.0,
    "ambient_temp": 15.0
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

def generate_live_data_tick(tick: int, scenario: str):
    """Generates a single point in time telemetry tick."""
    RUL_DATA = sorted([112, 98, 69, 82, 91, 93, 91, 95, 111, 96, 97, 124, 95, 107, 83, 84, 50, 28, 87, 16, 57, 111, 113, 20, 145, 119, 66, 97, 90, 115, 8, 48, 106, 7, 11, 19, 21, 50, 142, 28, 18, 10, 59, 109, 114, 47, 135, 92, 21, 79, 114, 29, 26, 97, 137, 15, 103, 37, 114, 100, 21, 54, 72, 28, 128, 14, 77, 8, 121, 94, 118, 50, 131, 126, 113, 10, 34, 107, 63, 90, 8, 9, 137, 58, 118, 89, 116, 115, 136, 28, 38, 20, 85, 55, 128, 137, 82, 59, 117, 20, 18, 79, 106, 110, 15, 155, 6, 90, 11, 79, 6, 73, 30, 11, 37, 67, 68, 99, 22, 54, 97, 10, 142, 77, 88, 163, 126, 138, 83, 78, 75, 11, 53, 173, 63, 100, 151, 55, 48, 37, 44, 27, 18, 6, 15, 112, 131, 13, 122, 13, 98, 53, 52, 106, 103, 152, 123, 26, 178, 73, 169, 39, 39, 14, 11, 121, 86, 56, 115, 17, 148, 104, 78, 86, 98, 36, 94, 52, 91, 15, 141, 74, 146, 17, 47, 194, 21, 79, 97, 8, 9, 73, 183, 97, 73, 49, 31, 97, 9, 14, 106, 8, 8, 106, 116, 120, 61, 168, 35, 80, 9, 50, 151, 78, 91, 7, 181, 150, 106, 15, 67, 145, 180, 7, 179, 124, 82, 108, 79, 121, 120, 39, 38, 9, 167, 87, 88, 7, 51, 55, 155, 47, 81, 43, 98, 10, 92, 11, 165, 34, 115, 59, 99, 103, 108, 83, 171, 15, 9, 42, 13, 41, 88, 14, 155, 188, 96, 82, 135, 182, 36, 107, 14, 95, 142, 23, 6, 144, 35, 97, 68, 14, 67, 191, 19, 10, 158, 183, 43, 12, 148, 13, 37, 122, 80, 93, 132, 32, 103, 174, 111, 68, 192, 121, 134, 48, 85, 8, 23, 8, 6, 57, 83, 172, 101, 81, 86, 165, 73, 121, 139, 75, 151, 145, 11, 108, 14, 126, 61, 85, 8, 101, 153, 89, 190, 12, 62, 134, 101, 121, 167, 17, 161, 181, 16, 152, 148, 56, 111, 23, 84, 12, 43, 48, 122, 191, 56, 131, 51, 44, 51, 27, 120, 101, 99, 71, 55, 55, 66, 77, 115, 115, 31, 108, 56, 136, 132, 85, 56, 18, 119, 78, 9, 58, 11, 88, 144, 124, 89, 79, 55, 71, 65, 87, 137, 145, 22, 8, 41, 131, 115, 128, 69, 111, 7, 137, 55, 135, 11, 78, 120, 87, 87, 55, 93, 88, 40, 49, 128, 129, 58, 117, 28, 115, 87, 92, 103, 100, 63, 35, 45, 99, 117, 45, 27, 86, 20, 18, 133, 15, 6, 145, 104, 56, 25, 68, 144, 41, 51, 81, 14, 67, 10, 127, 113, 123, 17, 8, 28], reverse=True)
    # Base engine parameters with normal operational noise
    rpm = np.random.normal(6100, 20)
    cht = np.random.normal(150, 2)
    egt = np.random.normal(700, 5)
    oil_pressure = np.random.normal(4.3, 0.1)
    oil_temperature = np.random.normal(95, 2)
    fuel_flow = np.random.normal(18.5, 0.2)
    vibration = np.random.normal(0.2, 0.02)
    battery_voltage = np.random.normal(28.0, 0.1)
    injection_timing = np.random.normal(22.0, 0.1)
    
    health_index = 100.0
    fault_label = "Normal"
    
    # Fault injection based on time progression (tick)
    degradation = min(tick / 60.0, 1.0)
    
    if scenario == "Overheating" and tick > 5:
        cht += degradation * 40
        egt += degradation * 60
        oil_temperature += degradation * 30
        health_index -= degradation * 30
        fault_label = "Overheating"
        
    elif scenario == "Injector_Degradation" and tick > 5:
        fuel_flow += degradation * 5
        egt += degradation * 40
        rpm += np.random.normal(0, degradation * 50)
        health_index -= degradation * 40
        fault_label = "Injector_Degradation"
        
    elif scenario == "Lubrication" and tick > 5:
        oil_pressure -= degradation * 1.5
        oil_temperature += degradation * 25
        vibration += degradation * 0.3
        health_index -= degradation * 50
        fault_label = "Lubrication"
        
    elif scenario == "Vibration_Fault" and tick > 5:
        vibration += degradation * 0.8
        health_index -= degradation * 25
        fault_label = "Vibration_Fault"
        
    elif scenario == "Sensor_Drift" and tick > 5:
        cht += degradation * 30
        health_index -= degradation * 10
        fault_label = "Sensor_Drift"
        
    elif scenario == "Misfire" and tick > 5:
        misfire_severity = degradation
        rpm -= np.random.uniform(0, misfire_severity * 300)
        vibration += misfire_severity * 0.5
        egt -= misfire_severity * 50
        health_index -= misfire_severity * 45
        fault_label = "Misfire"

    data = {
        "timestamp": datetime.now().isoformat(),
        "engine_id": "ENG_001",
        "mission_id": "LIVE_SIM_001",
        "scenario": scenario,
        "tick": tick,
        "rpm": round(rpm, 1),
        "throttle_pct": simulation_state["throttle"],
        "altitude_ft": simulation_state["altitude"],
        "ambient_temp_c": simulation_state["ambient_temp"],
        "cht_c": round(cht, 1),
        "egt_c": round(egt, 1),
        "oil_pressure_bar": round(oil_pressure, 2),
        "oil_temperature_c": round(oil_temperature, 1),
        "fuel_flow_lh": round(fuel_flow, 1),
        "vibration_g": round(vibration, 3),
        "battery_voltage_v": round(battery_voltage, 1),
        "injection_timing_deg": round(injection_timing, 1),
        "health_index": round(health_index, 1),
        "rul": RUL_DATA[tick % len(RUL_DATA)],
        "fault_label": fault_label
    }
    return data

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry streaming."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                cmd = json.loads(data)
                if "scenario" in cmd:
                    simulation_state["scenario"] = cmd["scenario"]
                    simulation_state["tick"] = 0
                    print(f"*** Injected scenario: {cmd['scenario']} ***")
                if "is_running" in cmd:
                    simulation_state["is_running"] = cmd["is_running"]
            except Exception as e:
                print(f"Error parsing command: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def simulation_loop():
    """Background task that ticks the simulation and broadcasts data at 1 Hz."""
    while True:
        if simulation_state["is_running"] and len(manager.active_connections) > 0:
            data = generate_live_data_tick(simulation_state["tick"], simulation_state["scenario"])
            await manager.broadcast(json.dumps(data))
            simulation_state["tick"] += 1
        await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_loop())
    print("\n=======================================================")
    print("MALE UAV Live Telemetry Server Started!")
    print("Open your browser and navigate to: http://localhost:8000")
    print("=======================================================\n")

if __name__ == "__main__":
    uvicorn.run("live_telemetry_server:app", host="0.0.0.0", port=8000, reload=True)

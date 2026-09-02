@echo off
title AeroTwin Launcher
echo ==================================================
echo   AeroTwin Digital Twin Launcher
echo   Starting Backend and Next.js Frontend...
echo ==================================================

REM 1. Start Python Backend in background window
start "AeroTwin Backend (Port 8000)" cmd /k ".\venv\Scripts\activate && python live_telemetry_server.py"

REM 2. Start Next.js Frontend in background window
start "AeroTwin Frontend (Port 3000)" cmd /k "cd frontend && npm run dev"

REM 3. Wait 3 seconds and open browser
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo All services launched!
echo GCS Dashboard is opening at http://localhost:3000
echo.

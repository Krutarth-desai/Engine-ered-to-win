# AeroTwin | MALE UAV Digital Twin Telemetry Server ✈️

> **Aero Piston Engine Digital Twin Ground Control Station (GCS) & Live Telemetry Simulator** built with FastAPI, WebSockets, and modern web visualization.

---

## 📋 Prerequisites

Make sure the target machine has the following installed:
- **Python 3.10+** (Python 3.10, 3.11, 3.12, etc.)
- **Git** (optional, to clone the repo)
- Modern web browser (Chrome, Edge, Firefox, Safari)

---

## 🚀 Setup & Run Instructions (For Any Device)

Follow these steps on Windows, macOS, or Linux:

### 1. Clone the Repository
```bash
git clone https://github.com/Krutarth-desai/Engine-ered-to-win.git
cd Engine-ered-to-win
```

### 2. Create and Activate a Virtual Environment

* **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If you get a script execution policy error on PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then activate again)*

* **Windows (Command Prompt):**
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Everything in One Command (Recommended) 🚀

You can start both the **FastAPI Backend** and **Next.js Frontend** together and automatically launch the dashboard in your browser:

* **Using Python:**
  ```bash
  python run.py
  ```
* **Or on Windows (One-Click):**
  Double-click `run.bat`

---

### Manual Two-Terminal Startup (Alternative)

If you prefer to run services in separate terminals:

* **Terminal 1 (Backend):**
  ```bash
  python live_telemetry_server.py
  ```
* **Terminal 2 (Frontend):**
  ```bash
  cd frontend
  npm run dev
  ```

---

### 5. Open the Dashboard
👉 **[http://localhost:3000](http://localhost:3000)** (Next.js GCS Frontend)  
*(Backend API & WebSockets run on [http://localhost:8000](http://localhost:8000))*

---

## 🌐 Accessing from Another Device on the Same Network (LAN / Wi-Fi)

The application allows cross-device access from tablets, laptops, and phones on the same local network:

1. Find the host machine's Local IP Address:
   - **Windows:** Run `ipconfig` (look for `IPv4 Address`, e.g. `192.168.1.50`)
   - **macOS / Linux:** Run `ifconfig` or `ip a`
2. On any other device connected to the same Wi-Fi/LAN, open:
   ```text
   http://<HOST_IP_ADDRESS>:3000
   ```
   *(e.g., `http://192.168.1.50:3000`)*

---

## 🛠️ Tech Stack
- **Frontend / GCS:** React, Next.js (App Router), TypeScript, Chart.js, `@supabase/supabase-js`, CSS Custom Properties (Aerospace HUD / Glassmorphism)
- **Backend:** FastAPI, Uvicorn, WebSockets, NumPy, Pandas, Scikit-learn, TensorFlow / Keras (LSTM)
- **Streaming:** Real-time bi-directional WebSockets (1 Hz live telemetry stream on `/ws/telemetry`, 6.7 Hz CMAPSS RUL stream on `/ws/rul`)
- **Database & Auth:** Supabase (Cloud PostgreSQL)
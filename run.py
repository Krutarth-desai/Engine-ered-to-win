import subprocess
import sys
import os
import time
import webbrowser
import signal

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(root_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    print("==================================================")
    print("🚁 Launching AeroTwin GCS (Backend + Frontend)")
    print("==================================================")
    
    # 1. Start Backend
    print("[1/2] Starting Python FastAPI Telemetry & ML Backend on port 8000...")
    backend_proc = subprocess.Popen(
        [python_exe, "live_telemetry_server.py"],
        cwd=root_dir
    )
    
    # 2. Start Frontend
    print("[2/2] Starting Next.js React GCS Frontend on port 3000...")
    frontend_dir = os.path.join(root_dir, "frontend")
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        shell=True
    )
    
    # Wait for servers to initialize
    time.sleep(3)
    print("\n" + "=" * 50)
    print("✅ All services online!")
    print("👉 Frontend Dashboard: http://localhost:3000")
    print("👉 Backend Telemetry:  http://localhost:8000")
    print("=" * 50)
    print("\nPress Ctrl+C to terminate all services.\n")
    
    # Automatically open browser
    try:
        webbrowser.open("http://localhost:3000")
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None or frontend_proc.poll() is not None:
                break
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down AeroTwin services...")
    finally:
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=2)
        except Exception:
            backend_proc.kill()
            
        try:
            # On Windows, killing npm task tree
            subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
        except Exception:
            pass
        print("✅ Shutdown complete.")

if __name__ == "__main__":
    main()

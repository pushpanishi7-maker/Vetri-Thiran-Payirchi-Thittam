"""
LegalEase Unified Runner
Runs both FastAPI Backend and Streamlit Frontend concurrently in the same terminal.
All real-time logging, AI generation steps, and progress outputs stream directly to your console.
"""

import os
import sys
import time
import subprocess

def main():
    # Force unbuffered output across Python processes so progress logs appear instantly
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    python_exe = sys.executable

    print("=" * 70)
    print("  LEGALEASE - Single-Terminal Unified Launcher")
    print("=" * 70)

    # 1. Start FastAPI Backend (Uvicorn)
    print("\n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_cmd = [
        python_exe, "-m", "uvicorn", "legalEaseAPI.main:app",
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ]
    # Direct console binding: stdout=None, stderr=None preserves real-time unbuffered logs
    backend_proc = subprocess.Popen(backend_cmd)

    # Short delay so Uvicorn can initialize its port cleanly
    time.sleep(2)

    # 2. Start Streamlit Frontend
    print("\n[2/2] Starting Streamlit Frontend on http://localhost:8501 ...")
    frontend_cmd = [
        python_exe, "-m", "streamlit", "run", "frontend/app.py"
    ]
    frontend_proc = subprocess.Popen(frontend_cmd)

    print("\n" + "-" * 70)
    print("[*] Both services are live in this terminal!")
    print("[*] Backend:  http://127.0.0.1:8000")
    print("[*] Frontend: http://localhost:8501")
    print("[*] AI generation logs & progress steps will stream directly below.")
    print("[*] Press Ctrl+C to cleanly stop both services together.")
    print("-" * 70 + "\n")

    try:
        # Keep parent script running while both services are active
        while backend_proc.poll() is None and frontend_proc.poll() is None:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n[!] Received Ctrl+C. Gracefully stopping LegalEase services...")
    finally:
        for name, proc in [("Frontend", frontend_proc), ("Backend", backend_proc)]:
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=3)
                except Exception:
                    proc.kill()
        print("[OK] Both services stopped cleanly.\n")

if __name__ == "__main__":
    main()

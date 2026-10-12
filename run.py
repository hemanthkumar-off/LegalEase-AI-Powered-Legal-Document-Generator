"""Single-command runner script for LegalEase.

Starts both the FastAPI backend and the Streamlit frontend simultaneously,
monitors their health, and shuts them down gracefully upon exit (Ctrl+C).

Usage:
    python run.py
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from pathlib import Path
import urllib.request
import urllib.error

# Project base directory
BASE_DIR = Path(__file__).resolve().parent

BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "8501"))

BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"


def print_banner():
    banner = f"""
=============================================================================
              ⚖️  LegalEase - AI Legal Document Generator
=============================================================================
  🚀 Initializing services:
     • FastAPI Backend Server  -> {BACKEND_URL}
     • Swagger Documentation   -> {BACKEND_URL}/docs
     • Streamlit Frontend UI   -> {FRONTEND_URL}
=============================================================================
  💡 Press Ctrl+C at any time to safely shut down both servers.
=============================================================================
"""
    print(banner)


def wait_for_backend(timeout: int = 15) -> bool:
    """Poll the backend health endpoint until it is ready."""
    print("⏳ Waiting for FastAPI backend to initialize...", end="", flush=True)
    start_time = time.time()
    health_url = f"{BACKEND_URL}/health"

    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "LegalEase-Runner"})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    print(" [READY]")
                    return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        print(".", end="", flush=True)
        time.sleep(0.5)

    print(" [TIMEOUT]")
    return False


def main():
    print_banner()

    # 1. Start FastAPI backend subprocess
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        BACKEND_HOST,
        "--port",
        str(BACKEND_PORT),
    ]

    print(f"📦 Starting FastAPI backend on port {BACKEND_PORT}...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(BASE_DIR),
        stdout=None,
        stderr=None,
    )

    # 2. Wait for backend to be ready
    is_ready = wait_for_backend()
    if not is_ready:
        print("⚠️  Backend took longer than expected to report healthy, proceeding anyway...")

    # 3. Start Streamlit frontend subprocess
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "frontend/app.py",
        "--server.port",
        str(FRONTEND_PORT),
        "--server.headless",
        "true",
    ]

    print(f"🎨 Starting Streamlit frontend on port {FRONTEND_PORT}...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(BASE_DIR),
        stdout=None,
        stderr=None,
    )

    time.sleep(2)
    print("\n✨ All systems operational!")
    print(f"👉 Open your browser at: {FRONTEND_URL}\n")

    # Attempt to open browser automatically
    try:
        webbrowser.open(FRONTEND_URL)
    except Exception:
        pass

    def shutdown(signum=None, frame=None):
        print("\n\n🛑 Shutting down LegalEase servers...")
        try:
            frontend_proc.terminate()
            frontend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()

        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=3)
        except Exception:
            backend_proc.kill()

        print("✅ LegalEase shutdown complete. Goodbye!")
        sys.exit(0)

    # Register signal handlers for clean exit
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep runner alive while processes run
    try:
        while True:
            # Check if backend crashed
            b_poll = backend_proc.poll()
            if b_poll is not None:
                print(f"⚠️ FastAPI backend process exited unexpectedly with code {b_poll}.")
                break

            # Check if frontend crashed
            f_poll = frontend_proc.poll()
            if f_poll is not None:
                print(f"⚠️ Streamlit frontend process exited unexpectedly with code {f_poll}.")
                break

            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()
    finally:
        shutdown()


if __name__ == "__main__":
    main()

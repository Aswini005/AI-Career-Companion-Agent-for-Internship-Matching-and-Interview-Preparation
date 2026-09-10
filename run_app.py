import os
import sys
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

def get_python_executable():
    # Check for backend virtual environment
    if sys.platform == "win32":
        venv_python = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
        env_python = os.path.join(BACKEND_DIR, "env", "Scripts", "python.exe")
        root_venv = os.path.join(BASE_DIR, "..", ".venv", "Scripts", "python.exe")
    else:
        venv_python = os.path.join(BACKEND_DIR, "venv", "bin", "python")
        env_python = os.path.join(BACKEND_DIR, "env", "bin", "python")
        root_venv = os.path.join(BASE_DIR, "..", ".venv", "bin", "python")

    for py in [venv_python, env_python, root_venv]:
        if os.path.exists(py):
            return py
    return sys.executable

def build_frontend():
    print("🔨 Building frontend assets...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True, shell=sys.platform == "win32")
        print("✅ Frontend build completed successfully.")
    except Exception as e:
        print(f"❌ Frontend build failed: {e}")
        sys.exit(1)

def run_backend():
    python_exe = get_python_executable()
    print(f"🚀 Starting FastAPI backend using {python_exe}...")
    cmd = [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"]
    subprocess.run(cmd, cwd=BACKEND_DIR)

def run_dev():
    python_exe = get_python_executable()
    print("⚡ Starting Backend (port 8000) and Frontend Vite Dev Server (port 5173)...")
    
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "app"],
        cwd=BACKEND_DIR
    )
    frontend_proc = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=sys.platform == "win32"
    )

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping development servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Career Companion Application Runner")
    parser.add_argument("--build", action="store_true", help="Build frontend before starting FastAPI unified server")
    parser.add_argument("--dev", action="store_true", help="Run both FastAPI backend and Vite frontend dev server concurrently")
    parser.add_argument("--backend-only", action="store_true", help="Run backend uvicorn server only")

    args = parser.parse_args()

    if args.dev:
        run_dev()
    else:
        if args.build or not os.path.exists(os.path.join(FRONTEND_DIR, "dist")):
            build_frontend()
        run_backend()

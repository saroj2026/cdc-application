"""Automatically restart backend and monitor pipeline status."""

import sys
import time
import requests
import subprocess
import os
import signal
from pathlib import Path

# Configure encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def print_status(message: str, status: str = "INFO"):
    """Print colored status message."""
    colors = {
        "INFO": "\033[94m", "SUCCESS": "\033[92m", "ERROR": "\033[91m", 
        "WARNING": "\033[93m", "RESET": "\033[0m"
    }
    symbol = {"INFO": "ℹ", "SUCCESS": "✓", "ERROR": "✗", "WARNING": "⚠"}
    print(f"{colors.get(status, '')}{symbol.get(status, '')} {message}{colors['RESET']}")

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/connections", timeout=5)
        return response.status_code == 200
    except:
        return False

def find_backend_process():
    """Find backend process."""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'uvicorn' in ' '.join(cmdline).lower():
                    return proc.info['pid']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        # psutil not available, try alternative method
        pass
    return None

def stop_backend():
    """Stop backend if running."""
    print_status("Step 1: Stopping backend...", "INFO")
    
    if not check_backend():
        print_status("Backend is not running", "INFO")
        return True
    
    # Try to find and kill the process
    pid = find_backend_process()
    if pid:
        try:
            os.kill(pid, signal.SIGTERM)
            print_status(f"Sent termination signal to process {pid}", "INFO")
            time.sleep(3)
        except Exception as e:
            print_status(f"Could not stop process: {e}", "WARNING")
    
    # Wait for backend to stop
    for i in range(10):
        if not check_backend():
            print_status("Backend stopped", "SUCCESS")
            return True
        time.sleep(1)
    
    print_status("Backend may still be running - please stop it manually (Ctrl+C)", "WARNING")
    return False

def start_backend():
    """Start backend server."""
    print_status("\nStep 2: Starting backend...", "INFO")
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    try:
        # Start uvicorn in background
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "ingestion.api:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print_status(f"Backend started with PID: {process.pid}", "SUCCESS")
        
        # Wait for backend to be ready
        print_status("Waiting for backend to be ready...", "INFO")
        for i in range(30):
            if check_backend():
                print_status("Backend is ready!", "SUCCESS")
                time.sleep(2)  # Give it a moment to fully initialize
                return process
            time.sleep(1)
            if i % 5 == 0:
                print_status(f"Still waiting... ({i+1}/30)", "INFO")
        
        print_status("Backend did not start in time", "ERROR")
        return None
        
    except Exception as e:
        print_status(f"Failed to start backend: {e}", "ERROR")
        return None

def main():
    """Main function."""
    print("\n" + "="*60)
    print("AUTOMATIC BACKEND RESTART AND MONITORING".center(60))
    print("="*60 + "\n")
    
    # Step 1: Stop backend
    stop_backend()
    time.sleep(2)
    
    # Step 2: Start backend
    backend_process = start_backend()
    if not backend_process:
        print_status("Failed to start backend. Please start manually.", "ERROR")
        return 1
    
    # Step 3: Run monitoring script
    print_status("\nStep 3: Running monitoring script...", "INFO")
    print_status("="*60, "INFO")
    
    try:
        # Import and run the monitoring script
        import monitor_pipeline_after_restart
        exit_code = monitor_pipeline_after_restart.main()
        return exit_code
    except Exception as e:
        print_status(f"Failed to run monitoring script: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_status("\nProcess interrupted", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)


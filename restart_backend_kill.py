"""Kill existing backend processes and restart the backend."""

import subprocess
import sys
import time
import os
import signal

print("=" * 70)
print("Restarting Backend Server")
print("=" * 70)

# Step 1: Find and kill Python processes
print("\n1. Stopping existing backend processes...")

try:
    # On Windows, use tasklist and taskkill
    if sys.platform == "win32":
        # Find Python processes
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            python_processes = []
            for line in lines[1:]:  # Skip header
                if line.strip():
                    parts = line.split(',')
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        try:
                            python_processes.append(int(pid))
                        except ValueError:
                            pass
            
            if python_processes:
                print(f"   Found {len(python_processes)} Python process(es)")
                for pid in python_processes:
                    try:
                        # Try to get process command line to check if it's the backend
                        cmd_result = subprocess.run(
                            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine", "/format:list"],
                            capture_output=True,
                            text=True
                        )
                        cmd_line = cmd_result.stdout
                        
                        # Check if it's uvicorn or the backend
                        if "uvicorn" in cmd_line.lower() or "ingestion.api" in cmd_line.lower():
                            print(f"   Killing backend process (PID: {pid})...")
                            subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                                         capture_output=True)
                            print(f"   ✓ Killed process {pid}")
                        else:
                            print(f"   Skipping non-backend process (PID: {pid})")
                    except Exception as e:
                        print(f"   ⚠️  Could not kill process {pid}: {e}")
            else:
                print("   No Python processes found")
        else:
            print("   No Python processes found")
    else:
        # On Linux/Mac, use ps and kill
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if "uvicorn" in line or "ingestion.api" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        pid = int(parts[1])
                        print(f"   Killing backend process (PID: {pid})...")
                        try:
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(1)
                            # Force kill if still running
                            try:
                                os.kill(pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            print(f"   ✓ Killed process {pid}")
                        except ProcessLookupError:
                            print(f"   Process {pid} already terminated")
                        except Exception as e:
                            print(f"   ⚠️  Could not kill process {pid}: {e}")

except Exception as e:
    print(f"   ⚠️  Error finding/killing processes: {e}")

# Wait a moment for processes to terminate
print("\n2. Waiting 3 seconds for processes to terminate...")
time.sleep(3)

# Step 2: Start the backend
print("\n3. Starting backend server...")
print("   Command: python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000")

try:
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Start backend in background
    if sys.platform == "win32":
        # On Windows, use START command to open new window
        subprocess.Popen(
            ["start", "cmd", "/k", "python", "-m", "uvicorn", "ingestion.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            shell=True,
            cwd=script_dir
        )
        print("   ✅ Backend started in new window")
    else:
        # On Linux/Mac, use nohup or screen
        with open("backend.log", "w") as log_file:
            process = subprocess.Popen(
                ["python", "-m", "uvicorn", "ingestion.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=script_dir
            )
        print(f"   ✅ Backend started (PID: {process.pid})")
        print(f"   Logs: backend.log")

except Exception as e:
    print(f"   ❌ Failed to start backend: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Wait and verify
print("\n4. Waiting 5 seconds for backend to initialize...")
time.sleep(5)

print("\n5. Verifying backend is running...")
try:
    import requests
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend is healthy and responding!")
        print(f"   Response: {response.text[:200]}")
    else:
        print(f"   ⚠️  Backend responded with status {response.status_code}")
except requests.exceptions.Timeout:
    print("   ⚠️  Backend is starting but not yet ready (timeout)")
    print("   This is normal - it may take a few more seconds")
except requests.exceptions.ConnectionError:
    print("   ⚠️  Backend is starting but not yet ready (connection refused)")
    print("   This is normal - it may take a few more seconds")
except Exception as e:
    print(f"   ⚠️  Could not verify backend: {e}")

print("\n" + "=" * 70)
print("✅ Backend restart completed!")
print("=" * 70)
print("\nBackend should be running at: http://localhost:8000")
print("API Docs: http://localhost:8000/docs")
print("\nIf the backend didn't start, check the window/logs for errors.")



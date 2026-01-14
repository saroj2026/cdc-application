"""Kill all Python processes and restart backend."""

import subprocess
import sys
import time
import os

print("=" * 70)
print("Killing All Python Processes and Restarting Backend")
print("=" * 70)

# Step 1: Kill all Python processes
print("\n1. Killing all Python processes...")

if sys.platform == "win32":
    try:
        # Kill all python.exe processes
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✅ Killed all Python processes")
        else:
            if "not found" in result.stderr.lower() or "not found" in result.stdout.lower():
                print("   ℹ️  No Python processes found to kill")
            else:
                print(f"   ⚠️  {result.stderr}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
else:
    try:
        subprocess.run(["pkill", "-9", "python"], capture_output=True)
        print("   ✅ Killed all Python processes")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

# Wait for processes to terminate
print("\n2. Waiting 3 seconds...")
time.sleep(3)

# Step 2: Start backend
print("\n3. Starting backend in new window...")
print("   This will open a new command window")

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

if sys.platform == "win32":
    # Use START to open new window
    cmd = f'cd /d "{script_dir}" && python -m uvicorn ingestion.api:app --reload --host 0.0.0.0 --port 8000'
    subprocess.Popen(
        ["cmd", "/c", "start", "cmd", "/k", cmd],
        shell=True
    )
    print("   ✅ Backend starting in new window")
    print("   Please check the new window for any errors")
else:
    # Linux/Mac
    with open("backend.log", "w") as log_file:
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "ingestion.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
    print(f"   ✅ Backend started (PID: {process.pid})")

print("\n" + "=" * 70)
print("✅ Process completed!")
print("=" * 70)
print("\nThe backend should be starting in a new window.")
print("Wait 10-15 seconds for it to fully start, then try accessing:")
print("  - Health: http://localhost:8000/health")
print("  - API: http://localhost:8000/api/v1/pipelines")



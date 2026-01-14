"""Restart backend on Windows and start Oracle pipeline full load."""

import subprocess
import sys
import os
import time
import requests
import signal

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Restart Backend and Start Oracle Pipeline Full Load")
print("=" * 70)

# Step 1: Stop existing backend
print("\n1. Stopping existing backend...")
try:
    # Try to find and kill uvicorn/python processes on port 8000
    result = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True,
        text=True
    )
    
    # Find process using port 8000
    for line in result.stdout.split('\n'):
        if ':8000' in line and 'LISTENING' in line:
            parts = line.split()
            if len(parts) > 0:
                pid = parts[-1]
                try:
                    print(f"   Found process on port 8000: PID {pid}")
                    subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                    print(f"   ✅ Stopped process {pid}")
                    time.sleep(2)
                except:
                    pass
except Exception as e:
    print(f"   ⚠️  Could not stop existing backend: {e}")

# Step 2: Set environment variables
print("\n2. Setting environment variables...")
env_vars = {
    "KAFKA_CONNECT_URL": "http://72.61.233.209:8083",
    "KAFKA_BOOTSTRAP_SERVERS": "72.61.233.209:9092",
    "DATABASE_URL": "postgresql://cdc_user:cdc_pass@72.61.233.209:5432/cdctest",
    "API_HOST": "0.0.0.0",
    "API_PORT": "8000"
}

for key, value in env_vars.items():
    os.environ[key] = value
    print(f"   {key}={value}")

# Step 3: Start backend
print("\n3. Starting backend...")
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Check if venv exists
venv_python = os.path.join(project_root, "venv", "Scripts", "python.exe")
if os.path.exists(venv_python):
    python_cmd = venv_python
    print(f"   Using venv Python: {python_cmd}")
else:
    python_cmd = sys.executable
    print(f"   Using system Python: {python_cmd}")

# Start backend in background
print(f"   Starting: {python_cmd} -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")
process = subprocess.Popen(
    [python_cmd, "-m", "uvicorn", "ingestion.api:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=project_root,
    env=os.environ.copy()
)

print(f"   ✅ Backend started with PID: {process.pid}")
print(f"   Process will run in background")

# Step 4: Wait for backend to be ready
print("\n4. Waiting for backend to be ready...")
max_attempts = 30
backend_ready = False

for i in range(max_attempts):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend is ready!")
            backend_ready = True
            break
    except:
        if i < max_attempts - 1:
            print(f"   ⏳ Waiting... ({i+1}/{max_attempts})")
            time.sleep(2)
        else:
            print("   ❌ Backend did not start in time")
            print("   Check if there are any errors")
            sys.exit(1)

if not backend_ready:
    sys.exit(1)

# Step 5: Update pipeline to full_load_only
print("\n5. Updating pipeline to full_load_only mode...")
try:
    response = requests.get(f"{API_BASE_URL}/pipelines", timeout=10)
    pipelines = response.json() if response.status_code == 200 else []
    
    pipeline = None
    for p in pipelines:
        if p.get("name") == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"   ❌ Pipeline '{PIPELINE_NAME}' not found")
        sys.exit(1)
    
    pipeline_id = pipeline.get("id")
    
    update_data = {
        "mode": "full_load_only",
        "enable_full_load": True,
        "target_schema": "public"  # Ensure lowercase
    }
    
    response = requests.put(
        f"{API_BASE_URL}/pipelines/{pipeline_id}",
        json=update_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Pipeline updated to full_load_only mode")
    else:
        print(f"   ⚠️  Update response: {response.status_code}")
        
except Exception as e:
    print(f"   ⚠️  Error updating pipeline: {e}")

# Step 6: Start pipeline
print("\n6. Starting pipeline with full load...")
try:
    response = requests.post(f"{API_BASE_URL}/pipelines/{pipeline_id}/start", timeout=60)
    
    if response.status_code in [200, 201, 202]:
        result = response.json()
        print(f"   ✅ Pipeline started successfully!")
        print(f"   Response: {result.get('message', 'Started')}")
    else:
        print(f"   ⚠️  Start response: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   ⚠️  Error starting pipeline: {e}")

# Step 7: Check status
print("\n7. Checking pipeline status...")
time.sleep(3)
try:
    response = requests.get(f"{API_BASE_URL}/pipelines/{pipeline_id}", timeout=10)
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   Mode: {pipeline.get('mode')}")
except Exception as e:
    print(f"   ⚠️  Error checking status: {e}")

print("\n" + "=" * 70)
print("✅ Backend Restarted and Pipeline Started!")
print("=" * 70)
print(f"\nBackend PID: {process.pid}")
print(f"Pipeline ID: {pipeline_id}")
print(f"\nMonitor backend logs in the terminal")
print(f"Check pipeline status: GET {API_BASE_URL}/pipelines/{pipeline_id}")


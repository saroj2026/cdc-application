"""Restart backend and start Oracle pipeline with full load only."""

import requests
import time
import subprocess
import sys
import os

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Restart Backend and Start Full Load")
print("=" * 70)

# Step 1: Check if backend is running
print("\n1. Checking if backend is running...")
try:
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend is running")
        backend_running = True
    else:
        print("   ⚠️  Backend responded with status:", response.status_code)
        backend_running = True
except Exception as e:
    print("   ⚠️  Backend is not responding:", str(e))
    backend_running = False

# Step 2: Restart backend
if backend_running:
    print("\n2. Restarting backend...")
    print("   (Note: On Windows, you may need to manually restart the backend)")
    print("   Please stop the backend (Ctrl+C) and restart it with:")
    print("   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")
    print("\n   Or if using a script:")
    print("   ./start_backend.sh")
    print("\n   Waiting 5 seconds for you to restart...")
    time.sleep(5)
else:
    print("\n2. Starting backend...")
    print("   Please start the backend manually:")
    print("   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")

# Step 3: Wait for backend to be ready
print("\n3. Waiting for backend to be ready...")
max_attempts = 30
for i in range(max_attempts):
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Backend is ready!")
            break
    except:
        if i < max_attempts - 1:
            print(f"   ⏳ Waiting... ({i+1}/{max_attempts})")
            time.sleep(2)
        else:
            print("   ❌ Backend did not start in time")
            print("   Please start it manually and run this script again")
            sys.exit(1)

# Step 4: Get pipeline
print(f"\n4. Finding pipeline '{PIPELINE_NAME}'...")
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
    print(f"   ✅ Found pipeline: {pipeline_id}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 5: Update pipeline to full_load_only mode
print("\n5. Updating pipeline to full_load_only mode...")
try:
    update_data = {
        "mode": "full_load_only",
        "enable_full_load": True
    }
    
    response = requests.put(
        f"{API_BASE_URL}/pipelines/{pipeline_id}",
        json=update_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        updated = response.json()
        print(f"   ✅ Pipeline updated to full_load_only mode")
        print(f"   Mode: {updated.get('mode')}")
    else:
        print(f"   ⚠️  Update response: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ⚠️  Error updating pipeline: {e}")

# Step 6: Start pipeline
print("\n6. Starting pipeline with full load...")
try:
    response = requests.post(f"{API_BASE_URL}/pipelines/{pipeline_id}/start", timeout=60)
    
    if response.status_code in [200, 201, 202]:
        result = response.json()
        print(f"   ✅ Pipeline started successfully!")
        print(f"   Response: {result}")
    else:
        print(f"   ⚠️  Start response: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   ⚠️  Error starting pipeline: {e}")
    import traceback
    traceback.print_exc()

# Step 7: Check pipeline status
print("\n7. Checking pipeline status...")
time.sleep(3)
try:
    response = requests.get(f"{API_BASE_URL}/pipelines/{pipeline_id}", timeout=10)
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Mode: {pipeline.get('mode')}")
    else:
        print(f"   ⚠️  Could not get pipeline status: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Error checking status: {e}")

print("\n" + "=" * 70)
print("✅ Process Complete!")
print("=" * 70)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Name: {PIPELINE_NAME}")
print("\nMonitor pipeline status:")
print(f"  GET {API_BASE_URL}/pipelines/{pipeline_id}")


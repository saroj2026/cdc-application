"""Start Oracle pipeline full load after backend restart."""

import requests
import time

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Start Oracle Pipeline Full Load")
print("=" * 70)

# Wait for backend
print("\n1. Checking if backend is running...")
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
            print("   ❌ Backend is not running")
            print("   Please start the backend first:")
            print("   python -m uvicorn ingestion.api:app --host 0.0.0.0 --port 8000")
            exit(1)

if not backend_ready:
    exit(1)

# Get pipeline
print(f"\n2. Finding pipeline '{PIPELINE_NAME}'...")
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
        exit(1)
    
    pipeline_id = pipeline.get("id")
    print(f"   ✅ Found pipeline: {pipeline_id}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Update pipeline
print("\n3. Updating pipeline to full_load_only mode...")
try:
    update_data = {
        "mode": "full_load_only",
        "enable_full_load": True,
        "target_schema": "public"
    }
    
    response = requests.put(
        f"{API_BASE_URL}/pipelines/{pipeline_id}",
        json=update_data,
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Pipeline updated")
    else:
        print(f"   ⚠️  Update response: {response.status_code}")
        
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# Start pipeline
print("\n4. Starting pipeline with full load...")
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
    print(f"   ⚠️  Error: {e}")

# Check status
print("\n5. Checking pipeline status...")
time.sleep(3)
try:
    response = requests.get(f"{API_BASE_URL}/pipelines/{pipeline_id}", timeout=10)
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   Mode: {pipeline.get('mode')}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 70)
print("✅ Complete!")
print("=" * 70)


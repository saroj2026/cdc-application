"""Start the Oracle to Snowflake pipeline."""

import requests
import time

API_BASE_URL = "http://localhost:8000/api/v1"
PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("Starting Oracle to Snowflake Pipeline")
print("=" * 70)

# Step 1: Get pipeline
print(f"\n1. Finding pipeline '{PIPELINE_NAME}'...")
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
    print(f"   Status: {pipeline.get('status')}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 2: Try different start endpoints
print("\n2. Starting pipeline...")

# Try endpoint 1: /pipelines/{id}/start
try:
    response = requests.post(f"{API_BASE_URL}/pipelines/{pipeline_id}/start", timeout=30)
    if response.status_code in [200, 201, 202]:
        print(f"   ✅ Pipeline started via /start endpoint")
        result = response.json()
        print(f"   Response: {result}")
    else:
        print(f"   ⚠️  /start endpoint returned: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ⚠️  /start endpoint error: {e}")

# Try endpoint 2: /pipelines/{id}/trigger
try:
    response = requests.post(
        f"{API_BASE_URL}/pipelines/{pipeline_id}/trigger",
        json={"runType": "full_load"},
        timeout=30
    )
    if response.status_code in [200, 201, 202]:
        print(f"   ✅ Pipeline started via /trigger endpoint")
        result = response.json()
        print(f"   Response: {result}")
    else:
        print(f"   ⚠️  /trigger endpoint returned: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ⚠️  /trigger endpoint error: {e}")

# Try endpoint 3: PUT /pipelines/{id} with status
try:
    response = requests.put(
        f"{API_BASE_URL}/pipelines/{pipeline_id}",
        json={"status": "RUNNING"},
        timeout=30
    )
    if response.status_code in [200, 201, 202]:
        print(f"   ✅ Pipeline started via PUT endpoint")
        result = response.json()
        print(f"   Response: {result}")
    else:
        print(f"   ⚠️  PUT endpoint returned: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ⚠️  PUT endpoint error: {e}")

# Step 3: Check pipeline status
print("\n3. Checking pipeline status...")
time.sleep(2)
try:
    response = requests.get(f"{API_BASE_URL}/pipelines/{pipeline_id}", timeout=10)
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Current status: {pipeline.get('status')}")
        print(f"   Full load status: {pipeline.get('full_load_status')}")
        print(f"   CDC status: {pipeline.get('cdc_status')}")
    else:
        print(f"   ⚠️  Could not get pipeline status: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Error checking status: {e}")

print("\n" + "=" * 70)
print("✅ Pipeline start attempt complete!")
print("=" * 70)
print(f"\nPipeline ID: {pipeline_id}")
print(f"Name: {PIPELINE_NAME}")
print("\nCheck pipeline status:")
print(f"  GET {API_BASE_URL}/pipelines/{pipeline_id}")


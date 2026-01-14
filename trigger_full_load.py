"""Trigger a new full load for the final_test pipeline."""

import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Triggering Full Load for final_test Pipeline")
print("=" * 80)

pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

# Step 1: Stop the pipeline
print("\n1. Stopping pipeline...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
    if response.status_code in [200, 404]:
        print("   [OK] Pipeline stopped")
    else:
        print(f"   [WARNING] Status: {response.status_code}")
except Exception as e:
    print(f"   [WARNING] Exception: {e}")

print("\n2. Waiting 5 seconds...")
time.sleep(5)

# Step 2: Start the pipeline (this will run full load again)
print("\n3. Starting pipeline (will run full load + CDC)...")
print("   This may take a few minutes...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=120)
    if response.status_code == 200:
        result = response.json()
        print("   [OK] Pipeline started")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
    else:
        print(f"   [ERROR] Failed to start: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n4. Waiting 30 seconds for full load to complete...")
time.sleep(30)

# Step 3: Check status again
print("\n5. Checking full load status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Pipeline Status: {pipeline.get('status')}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Full Load Triggered!")
print("=" * 80)
print("\nRun 'python check_full_load_status.py' to verify data transfer.")


import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Triggering Full Load for final_test Pipeline")
print("=" * 80)

pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

# Step 1: Stop the pipeline
print("\n1. Stopping pipeline...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
    if response.status_code in [200, 404]:
        print("   [OK] Pipeline stopped")
    else:
        print(f"   [WARNING] Status: {response.status_code}")
except Exception as e:
    print(f"   [WARNING] Exception: {e}")

print("\n2. Waiting 5 seconds...")
time.sleep(5)

# Step 2: Start the pipeline (this will run full load again)
print("\n3. Starting pipeline (will run full load + CDC)...")
print("   This may take a few minutes...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=120)
    if response.status_code == 200:
        result = response.json()
        print("   [OK] Pipeline started")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
    else:
        print(f"   [ERROR] Failed to start: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n4. Waiting 30 seconds for full load to complete...")
time.sleep(30)

# Step 3: Check status again
print("\n5. Checking full load status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
        print(f"   Pipeline Status: {pipeline.get('status')}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Full Load Triggered!")
print("=" * 80)
print("\nRun 'python check_full_load_status.py' to verify data transfer.")


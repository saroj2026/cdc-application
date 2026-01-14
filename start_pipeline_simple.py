"""Start the ps_sn_p pipeline."""

import requests
import json
import sys
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"

print("=" * 70)
print("Starting Pipeline: ps_sn_p")
print("=" * 70)

# Wait for backend
print("\n1. Waiting for backend to be ready...")
for i in range(10):
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ Backend is ready!")
            break
    except:
        if i < 9:
            print(f"   Waiting... ({i+1}/10)")
            time.sleep(2)
        else:
            print("   ⚠️  Backend not ready, proceeding anyway...")

# Start pipeline
print(f"\n2. Starting pipeline {PIPELINE_ID}...")
try:
    start_response = requests.post(
        f"{API_BASE}/pipelines/{PIPELINE_ID}/start",
        timeout=180
    )
    
    if start_response.status_code == 200:
        result = start_response.json()
        print("   ✅ Pipeline start requested!")
        print(f"   Response: {json.dumps(result, indent=6)}")
    else:
        error_detail = start_response.text
        print(f"   ⚠️  Status: {start_response.status_code}")
        print(f"   Response: {error_detail[:500]}")
except requests.exceptions.Timeout:
    print("   ⚠️  Request timed out (pipeline may still be starting)")
    print("   This is normal if Kafka Connect is slow to respond")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check status after a delay
print(f"\n3. Waiting 5 seconds and checking status...")
time.sleep(5)

try:
    status_response = requests.get(f"{API_BASE}/pipelines/{PIPELINE_ID}/status", timeout=15)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"   Pipeline Status: {status_data.get('status', 'unknown')}")
        
        dbz = status_data.get('debezium_connector', {})
        if dbz and isinstance(dbz, dict):
            dbz_conn = dbz.get('connector', {})
            if isinstance(dbz_conn, dict):
                print(f"   Debezium: {dbz_conn.get('state', 'unknown')}")
        
        sink = status_data.get('sink_connector', {})
        if sink and isinstance(sink, dict):
            sink_conn = sink.get('connector', {})
            if isinstance(sink_conn, dict):
                print(f"   Sink: {sink_conn.get('state', 'unknown')}")
except Exception as e:
    print(f"   ⚠️  Could not get status: {e}")

print(f"\n✅ Pipeline start process completed!")
print(f"\nMonitor the pipeline in the UI or check status with:")
print(f"   GET {API_BASE}/pipelines/{PIPELINE_ID}/status")



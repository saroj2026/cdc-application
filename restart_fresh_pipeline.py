"""Restart the fresh pipeline."""

import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Restarting Fresh Pipeline")
print("=" * 80)

# Get pipeline
print("\n1. Finding final_test pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if pipeline:
            pipeline_id = pipeline.get('id')
            print(f"   [OK] Pipeline found: {pipeline_id}")
            print(f"   Current Status: {pipeline.get('status')}")
        else:
            print("   [ERROR] Pipeline not found")
            exit(1)
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Start pipeline
print("\n2. Starting pipeline...")
print("   This will run full load + CDC")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=180)
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] Pipeline started!")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
        
        debezium = result.get('debezium_connector', {})
        if debezium.get('name'):
            print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
            print(f"      Status: {debezium.get('status', 'N/A')}")
        
        sink = result.get('sink_connector', {})
        if sink.get('name'):
            print(f"\n   ✅ Sink Connector: {sink.get('name')}")
            print(f"      Status: {sink.get('status', 'N/A')}")
    else:
        print(f"   [ERROR] Failed to start: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Waiting 30 seconds for full load to complete...")
time.sleep(30)

# Check status
print("\n4. Checking final status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
except Exception as e:
    print(f"   [WARNING] Failed to check status: {e}")

print("\n" + "=" * 80)
print("Pipeline Restarted!")
print("=" * 80)
print(f"\nPipeline ID: {pipeline_id}")
print("Run 'python check_full_load_status.py' to verify data transfer")


import requests
import time

API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Restarting Fresh Pipeline")
print("=" * 80)

# Get pipeline
print("\n1. Finding final_test pipeline...")
try:
    response = requests.get(f"{API_URL}/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        pipeline = next((p for p in pipelines if p.get('name') == 'final_test'), None)
        
        if pipeline:
            pipeline_id = pipeline.get('id')
            print(f"   [OK] Pipeline found: {pipeline_id}")
            print(f"   Current Status: {pipeline.get('status')}")
        else:
            print("   [ERROR] Pipeline not found")
            exit(1)
    else:
        print(f"   [ERROR] Failed to get pipelines: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    exit(1)

# Start pipeline
print("\n2. Starting pipeline...")
print("   This will run full load + CDC")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=180)
    if response.status_code == 200:
        result = response.json()
        print(f"   [OK] Pipeline started!")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        full_load = result.get('full_load', {})
        if full_load.get('success'):
            print(f"\n   ✅ Full Load: SUCCESS")
            print(f"      Tables transferred: {full_load.get('tables_transferred', 'N/A')}")
            print(f"      Total rows: {full_load.get('total_rows', 'N/A')}")
        else:
            print(f"\n   ⚠️  Full Load: {full_load.get('error', 'Unknown error')}")
        
        debezium = result.get('debezium_connector', {})
        if debezium.get('name'):
            print(f"\n   ✅ Debezium Connector: {debezium.get('name')}")
            print(f"      Status: {debezium.get('status', 'N/A')}")
        
        sink = result.get('sink_connector', {})
        if sink.get('name'):
            print(f"\n   ✅ Sink Connector: {sink.get('name')}")
            print(f"      Status: {sink.get('status', 'N/A')}")
    else:
        print(f"   [ERROR] Failed to start: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Waiting 30 seconds for full load to complete...")
time.sleep(30)

# Check status
print("\n4. Checking final status...")
try:
    response = requests.get(f"{API_URL}/pipelines/{pipeline_id}")
    if response.status_code == 200:
        pipeline = response.json()
        print(f"   Status: {pipeline.get('status')}")
        print(f"   Full Load Status: {pipeline.get('full_load_status')}")
        print(f"   CDC Status: {pipeline.get('cdc_status')}")
except Exception as e:
    print(f"   [WARNING] Failed to check status: {e}")

print("\n" + "=" * 80)
print("Pipeline Restarted!")
print("=" * 80)
print(f"\nPipeline ID: {pipeline_id}")
print("Run 'python check_full_load_status.py' to verify data transfer")


"""Check and start the ps_as_p pipeline."""

import requests
import json
import sys

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "ps_as_p"

print("=" * 70)
print(f"Checking Pipeline: {PIPELINE_NAME}")
print("=" * 70)

try:
    # Get all pipelines
    print(f"\n1. Fetching pipelines...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
    
    pipelines = response.json()
    print(f"   ✅ Found {len(pipelines)} pipeline(s)")
    
    # Find the pipeline by name
    pipeline = None
    for p in pipelines:
        if p.get('name') == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"\n   ❌ Pipeline '{PIPELINE_NAME}' not found!")
        print(f"\n   Available pipelines:")
        for p in pipelines:
            print(f"      - {p.get('name')} (ID: {p.get('id')}, Status: {p.get('status')}, CDC: {p.get('cdc_status')})")
        sys.exit(1)
    
    pipeline_id = pipeline.get('id')
    pipeline_status = pipeline.get('status', 'unknown')
    cdc_status = pipeline.get('cdc_status', 'unknown')
    full_load_status = pipeline.get('full_load_status', 'unknown')
    mode = pipeline.get('mode', 'unknown')
    
    print(f"\n2. Found pipeline:")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   ID: {pipeline_id}")
    print(f"   Status: {pipeline_status}")
    print(f"   CDC Status: {cdc_status}")
    print(f"   Full Load Status: {full_load_status}")
    print(f"   Mode: {mode}")
    print(f"   Source: {pipeline.get('source_database')}.{pipeline.get('source_schema')}")
    print(f"   Target: {pipeline.get('target_database')}.{pipeline.get('target_schema')}")
    
    # Check why CDC is stopped
    print(f"\n3. Checking CDC status...")
    if cdc_status == 'STOPPED':
        print(f"   ⚠️  CDC is STOPPED")
        print(f"   Possible reasons:")
        print(f"      - Pipeline status is not RUNNING")
        print(f"      - Debezium connector is not running")
        print(f"      - Sink connector is not running")
        print(f"      - Pipeline needs to be started")
    
    # Get detailed status
    print(f"\n4. Getting detailed status...")
    status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"   Status details:")
        print(f"      Pipeline Status: {status_data.get('status', 'unknown')}")
        if 'debezium_connector' in status_data:
            dbz = status_data['debezium_connector']
            print(f"      Debezium Connector: {dbz.get('connector', {}).get('state', 'unknown')}")
        if 'sink_connector' in status_data:
            sink = status_data['sink_connector']
            print(f"      Sink Connector: {sink.get('connector', {}).get('state', 'unknown')}")
    
    # Start the pipeline
    print(f"\n5. Starting pipeline...")
    if pipeline_status == 'RUNNING':
        print(f"   ℹ️  Pipeline is already RUNNING")
        print(f"   Attempting to restart to ensure CDC is active...")
    else:
        print(f"   Starting pipeline from {pipeline_status} state...")
    
    trigger_response = requests.post(
        f"{API_BASE}/pipelines/{pipeline_id}/start",
        timeout=60
    )
    
    if trigger_response.status_code == 200:
        result = trigger_response.json()
        print(f"   ✅ Pipeline start requested!")
        print(f"   Response: {json.dumps(result, indent=6)}")
        
        # Wait a bit and check status
        import time
        print(f"\n6. Waiting 3 seconds and checking status...")
        time.sleep(3)
        
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   Current Status:")
            print(f"      Pipeline: {status_data.get('status', 'unknown')}")
            if 'debezium_connector' in status_data:
                dbz = status_data['debezium_connector']
                print(f"      Debezium: {dbz.get('connector', {}).get('state', 'unknown')}")
            if 'sink_connector' in status_data:
                sink = status_data['sink_connector']
                print(f"      Sink: {sink.get('connector', {}).get('state', 'unknown')}")
        
        print(f"\n✅ Pipeline start process completed!")
        print(f"\nMonitor with:")
        print(f"   GET {API_BASE}/pipelines/{pipeline_id}/status")
        
    else:
        error_detail = trigger_response.text
        print(f"   ❌ Failed to start pipeline: {trigger_response.status_code}")
        print(f"   Error: {error_detail}")
        sys.exit(1)
        
except requests.exceptions.Timeout:
    print("❌ Request timed out")
    sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to API server")
    print("   Make sure the backend server is running on http://localhost:8000")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



"""Check and start the ps_sn_p pipeline."""

import requests
import json
import sys
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "ps_sn_p"

print("=" * 70)
print(f"Checking and Starting Pipeline: {PIPELINE_NAME}")
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
        sys.exit(1)
    
    pipeline_id = pipeline.get('id')
    pipeline_status = pipeline.get('status', 'unknown')
    cdc_status = pipeline.get('cdc_status', 'unknown')
    full_load_status = pipeline.get('full_load_status', 'unknown')
    mode = pipeline.get('mode', 'unknown')
    
    print(f"\n2. Pipeline Details:")
    print(f"   Name: {pipeline.get('name')}")
    print(f"   ID: {pipeline_id}")
    print(f"   Status: {pipeline_status}")
    print(f"   CDC Status: {cdc_status}")
    print(f"   Full Load Status: {full_load_status}")
    print(f"   Mode: {mode}")
    print(f"   Source: {pipeline.get('source_database')}.{pipeline.get('source_schema')}")
    print(f"   Target: {pipeline.get('target_database')}.{pipeline.get('target_schema')}")
    
    # Get detailed status
    print(f"\n3. Getting detailed connector status...")
    status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"   Detailed Status:")
        print(f"      Pipeline Status: {status_data.get('status', 'unknown')}")
        if 'debezium_connector' in status_data and status_data['debezium_connector']:
            dbz = status_data['debezium_connector']
            dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
            dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
            print(f"      Debezium Connector: {dbz_state}")
            if dbz_state != 'RUNNING':
                print(f"         ⚠️  Debezium connector is not RUNNING")
        if 'sink_connector' in status_data and status_data['sink_connector']:
            sink = status_data['sink_connector']
            sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
            sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
            print(f"      Sink Connector: {sink_state}")
            if sink_state != 'RUNNING':
                print(f"         ⚠️  Sink connector is not RUNNING")
    
    # Check why CDC is stopped
    print(f"\n4. Analysis:")
    if cdc_status == 'STOPPED':
        print(f"   ⚠️  CDC Status is STOPPED")
        print(f"   Reasons:")
        if pipeline_status != 'RUNNING':
            print(f"      - Pipeline status is {pipeline_status} (needs to be RUNNING)")
        if mode != 'full_load_and_cdc' and mode != 'cdc_only':
            print(f"      - Pipeline mode is {mode} (should be 'full_load_and_cdc' or 'cdc_only' for CDC)")
    
    # Start the pipeline
    print(f"\n5. Starting pipeline...")
    if pipeline_status == 'RUNNING':
        print(f"   ℹ️  Pipeline is already RUNNING, but CDC is STOPPED")
        print(f"   This might indicate connector issues. Attempting restart...")
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
        
        # Wait and check status multiple times
        print(f"\n6. Monitoring pipeline startup (checking every 3 seconds)...")
        for i in range(5):
            time.sleep(3)
            status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
            if status_response.status_code == 200:
                status_data = status_response.json()
                pipeline_stat = status_data.get('status', 'unknown')
                dbz = status_data.get('debezium_connector')
                dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
                dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
                sink = status_data.get('sink_connector')
                sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
                sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
                
                print(f"   Check {i+1}/5:")
                print(f"      Pipeline: {pipeline_stat}")
                print(f"      Debezium: {dbz_state}")
                print(f"      Sink: {sink_state}")
                
                if pipeline_stat == 'RUNNING' and dbz_state == 'RUNNING' and sink_state == 'RUNNING':
                    print(f"\n   ✅ All components are RUNNING!")
                    break
        
        # Final status check
        print(f"\n7. Final Status Check...")
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"   Final Status:")
            print(f"      Pipeline: {status_data.get('status', 'unknown')}")
            if 'debezium_connector' in status_data and status_data['debezium_connector']:
                dbz = status_data['debezium_connector']
                dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
                print(f"      Debezium: {dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'}")
            if 'sink_connector' in status_data and status_data['sink_connector']:
                sink = status_data['sink_connector']
                sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
                print(f"      Sink: {sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'}")
        
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


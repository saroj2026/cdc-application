"""Start pipeline and verify CDC is working."""

import requests
import json
import sys
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_NAME = "ps_sn_p"

print("=" * 70)
print("Starting Pipeline and Verifying CDC")
print("=" * 70)

try:
    # Step 1: Check backend health
    print("\n1. Checking backend health...")
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ⚠️  Backend responded with status {health_response.status_code}")
    except Exception as e:
        print(f"   ❌ Backend is not responding: {e}")
        print("   Please ensure the backend is running")
        sys.exit(1)
    
    # Step 2: Get pipeline
    print(f"\n2. Finding pipeline: {PIPELINE_NAME}...")
    response = requests.get(f"{API_BASE}/pipelines", timeout=10)
    
    if response.status_code != 200:
        print(f"   ❌ Error: {response.status_code}")
        sys.exit(1)
    
    pipelines = response.json()
    pipeline = None
    for p in pipelines:
        if p.get('name') == PIPELINE_NAME:
            pipeline = p
            break
    
    if not pipeline:
        print(f"   ❌ Pipeline '{PIPELINE_NAME}' not found!")
        sys.exit(1)
    
    pipeline_id = pipeline.get('id')
    print(f"   ✅ Found pipeline: {pipeline_id}")
    print(f"      Current Status: {pipeline.get('status')}")
    print(f"      CDC Status: {pipeline.get('cdc_status')}")
    print(f"      Mode: {pipeline.get('mode')}")
    
    # Step 3: Get current status
    print(f"\n3. Getting current pipeline status...")
    status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"   Pipeline Status: {status_data.get('status', 'unknown')}")
        
        # Check connectors
        dbz = status_data.get('debezium_connector', {})
        if dbz:
            dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
            dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
            print(f"   Debezium Connector: {dbz_state}")
        
        sink = status_data.get('sink_connector', {})
        if sink:
            sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
            sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
            print(f"   Sink Connector: {sink_state}")
    
    # Step 4: Start pipeline
    print(f"\n4. Starting pipeline...")
    if pipeline.get('status') == 'RUNNING':
        print("   ℹ️  Pipeline is already RUNNING")
        print("   Restarting to ensure CDC is active...")
    
    start_response = requests.post(
        f"{API_BASE}/pipelines/{pipeline_id}/start",
        timeout=120  # 2 minutes timeout
    )
    
    if start_response.status_code == 200:
        result = start_response.json()
        print("   ✅ Pipeline start requested!")
        print(f"   Response: {json.dumps(result, indent=6)}")
    else:
        error_detail = start_response.text
        print(f"   ❌ Failed to start pipeline: {start_response.status_code}")
        print(f"   Error: {error_detail}")
        sys.exit(1)
    
    # Step 5: Monitor startup
    print(f"\n5. Monitoring pipeline startup (checking every 5 seconds)...")
    max_checks = 12  # 1 minute total
    for i in range(max_checks):
        time.sleep(5)
        status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
        if status_response.status_code == 200:
            status_data = status_response.json()
            pipeline_stat = status_data.get('status', 'unknown')
            
            dbz = status_data.get('debezium_connector', {})
            dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
            dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
            
            sink = status_data.get('sink_connector', {})
            sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
            sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
            
            print(f"   Check {i+1}/{max_checks}:")
            print(f"      Pipeline: {pipeline_stat}")
            print(f"      Debezium: {dbz_state}")
            print(f"      Sink: {sink_state}")
            
            # Check if all are running
            if pipeline_stat == 'RUNNING' and dbz_state == 'RUNNING' and sink_state == 'RUNNING':
                print(f"\n   ✅ All components are RUNNING!")
                break
            elif pipeline_stat == 'ERROR':
                print(f"\n   ❌ Pipeline is in ERROR state")
                break
    
    # Step 6: Final verification
    print(f"\n6. Final CDC Verification...")
    status_response = requests.get(f"{API_BASE}/pipelines/{pipeline_id}/status", timeout=10)
    if status_response.status_code == 200:
        status_data = status_response.json()
        pipeline_stat = status_data.get('status', 'unknown')
        
        dbz = status_data.get('debezium_connector', {})
        dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
        dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
        dbz_tasks = dbz_conn.get('tasks', []) if isinstance(dbz_conn, dict) else []
        
        sink = status_data.get('sink_connector', {})
        sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
        sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
        sink_tasks = sink_conn.get('tasks', []) if isinstance(sink_conn, dict) else []
        
        print(f"\n   📊 Final Status:")
        print(f"      Pipeline Status: {pipeline_stat}")
        print(f"      Debezium Connector: {dbz_state}")
        if dbz_tasks:
            for idx, task in enumerate(dbz_tasks):
                task_state = task.get('state', 'unknown') if isinstance(task, dict) else 'unknown'
                print(f"         Task {idx}: {task_state}")
        print(f"      Sink Connector: {sink_state}")
        if sink_tasks:
            for idx, task in enumerate(sink_tasks):
                task_state = task.get('state', 'unknown') if isinstance(task, dict) else 'unknown'
                print(f"         Task {idx}: {task_state}")
        
        # Check for CDC events
        print(f"\n7. Checking for CDC events...")
        events_response = requests.get(
            f"{API_BASE}/monitoring/replication-events",
            params={"pipeline_id": pipeline_id, "limit": 10, "today_only": False},
            timeout=10
        )
        if events_response.status_code == 200:
            events = events_response.json()
            if isinstance(events, list):
                print(f"   Found {len(events)} recent events")
                if events:
                    print(f"   Latest event: {events[0].get('event_type', 'unknown')} at {events[0].get('created_at', 'unknown')}")
            else:
                print(f"   Events data: {json.dumps(events, indent=6)[:200]}")
        
        # Summary
        print(f"\n" + "=" * 70)
        print("CDC Verification Summary")
        print("=" * 70)
        
        cdc_working = (
            pipeline_stat == 'RUNNING' and
            dbz_state == 'RUNNING' and
            sink_state == 'RUNNING'
        )
        
        if cdc_working:
            print("✅ CDC IS WORKING!")
            print(f"   - Pipeline: {pipeline_stat}")
            print(f"   - Debezium Connector: {dbz_state}")
            print(f"   - Sink Connector: {sink_state}")
            print(f"\n   The pipeline is capturing changes and replicating to Snowflake.")
        else:
            print("⚠️  CDC Status:")
            print(f"   - Pipeline: {pipeline_stat}")
            print(f"   - Debezium Connector: {dbz_state}")
            print(f"   - Sink Connector: {sink_state}")
            print(f"\n   Some components are not RUNNING. Check the connector status above.")
        
        print(f"\nMonitor with:")
        print(f"   GET {API_BASE}/pipelines/{pipeline_id}/status")
        print(f"   GET {API_BASE}/monitoring/replication-events?pipeline_id={pipeline_id}")
        
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



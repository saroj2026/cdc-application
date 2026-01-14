"""Verify CDC status for ps_sn_p pipeline."""

import requests
import json
import sys
import time

API_BASE = "http://localhost:8000/api/v1"
PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"

print("=" * 70)
print("Verifying CDC Status for ps_sn_p Pipeline")
print("=" * 70)

try:
    # Get pipeline status
    print(f"\n1. Getting pipeline status...")
    status_response = requests.get(f"{API_BASE}/pipelines/{PIPELINE_ID}/status", timeout=15)
    
    if status_response.status_code != 200:
        print(f"   ❌ Error: {status_response.status_code}")
        print(f"   Response: {status_response.text}")
        sys.exit(1)
    
    status_data = status_response.json()
    print(f"   ✅ Status retrieved")
    
    # Display status
    print(f"\n2. Pipeline Status:")
    pipeline_stat = status_data.get('status', 'unknown')
    print(f"   Pipeline Status: {pipeline_stat}")
    
    # Check Debezium connector
    dbz = status_data.get('debezium_connector', {})
    if dbz:
        dbz_conn = dbz.get('connector', {}) if isinstance(dbz, dict) else {}
        dbz_state = dbz_conn.get('state', 'unknown') if isinstance(dbz_conn, dict) else 'unknown'
        dbz_name = dbz_conn.get('name', 'N/A') if isinstance(dbz_conn, dict) else 'N/A'
        dbz_tasks = dbz_conn.get('tasks', []) if isinstance(dbz_conn, dict) else []
        
        print(f"\n3. Debezium Connector:")
        print(f"   Name: {dbz_name}")
        print(f"   State: {dbz_state}")
        if dbz_tasks:
            for idx, task in enumerate(dbz_tasks):
                task_state = task.get('state', 'unknown') if isinstance(task, dict) else 'unknown'
                task_id = task.get('id', idx) if isinstance(task, dict) else idx
                print(f"   Task {task_id}: {task_state}")
        else:
            print(f"   Tasks: None")
    else:
        print(f"\n3. Debezium Connector: Not found or not created")
    
    # Check Sink connector
    sink = status_data.get('sink_connector', {})
    if sink:
        sink_conn = sink.get('connector', {}) if isinstance(sink, dict) else {}
        sink_state = sink_conn.get('state', 'unknown') if isinstance(sink_conn, dict) else 'unknown'
        sink_name = sink_conn.get('name', 'N/A') if isinstance(sink_conn, dict) else 'N/A'
        sink_tasks = sink_conn.get('tasks', []) if isinstance(sink_conn, dict) else []
        
        print(f"\n4. Sink Connector:")
        print(f"   Name: {sink_name}")
        print(f"   State: {sink_state}")
        if sink_tasks:
            for idx, task in enumerate(sink_tasks):
                task_state = task.get('state', 'unknown') if isinstance(task, dict) else 'unknown'
                task_id = task.get('id', idx) if isinstance(task, dict) else idx
                print(f"   Task {task_id}: {task_state}")
        else:
            print(f"   Tasks: None")
    else:
        print(f"\n4. Sink Connector: Not found or not created")
    
    # Get pipeline details
    print(f"\n5. Getting pipeline details...")
    pipeline_response = requests.get(f"{API_BASE}/pipelines/{PIPELINE_ID}", timeout=15)
    if pipeline_response.status_code == 200:
        pipeline_data = pipeline_response.json()
        print(f"   Pipeline Name: {pipeline_data.get('name', 'unknown')}")
        print(f"   Mode: {pipeline_data.get('mode', 'unknown')}")
        print(f"   CDC Status: {pipeline_data.get('cdc_status', 'unknown')}")
        print(f"   Full Load Status: {pipeline_data.get('full_load_status', 'unknown')}")
        print(f"   Debezium Connector Name: {pipeline_data.get('debezium_connector_name', 'None')}")
        print(f"   Sink Connector Name: {pipeline_data.get('sink_connector_name', 'None')}")
        print(f"   Kafka Topics: {pipeline_data.get('kafka_topics', [])}")
    
    # Check for CDC events
    print(f"\n6. Checking for CDC events...")
    try:
        events_response = requests.get(
            f"{API_BASE}/monitoring/replication-events",
            params={"pipeline_id": PIPELINE_ID, "limit": 20, "today_only": False},
            timeout=15
        )
        if events_response.status_code == 200:
            events = events_response.json()
            if isinstance(events, list):
                print(f"   Found {len(events)} recent events")
                if events:
                    print(f"   Latest 5 events:")
                    for event in events[:5]:
                        event_type = event.get('event_type', 'unknown')
                        created_at = event.get('created_at', 'unknown')
                        table_name = event.get('table_name', 'unknown')
                        print(f"      - {event_type} on {table_name} at {created_at}")
            else:
                print(f"   Events response: {json.dumps(events, indent=6)[:300]}")
    except Exception as e:
        print(f"   ⚠️  Could not fetch events: {e}")
    
    # Summary
    print(f"\n" + "=" * 70)
    print("CDC Status Summary")
    print("=" * 70)
    
    dbz_state = dbz_conn.get('state', 'unknown') if (dbz and isinstance(dbz, dict) and isinstance(dbz.get('connector'), dict)) else 'NOT_CREATED'
    sink_state = sink_conn.get('state', 'unknown') if (sink and isinstance(sink, dict) and isinstance(sink.get('connector'), dict)) else 'NOT_CREATED'
    
    cdc_working = (
        pipeline_stat == 'RUNNING' and
        dbz_state == 'RUNNING' and
        sink_state == 'RUNNING'
    )
    
    if cdc_working:
        print("✅ CDC IS WORKING!")
        print(f"   All components are RUNNING and capturing/replicating changes.")
    else:
        print("⚠️  CDC Status:")
        print(f"   Pipeline: {pipeline_stat}")
        print(f"   Debezium: {dbz_state}")
        print(f"   Sink: {sink_state}")
        
        if dbz_state == 'NOT_CREATED' or sink_state == 'NOT_CREATED':
            print(f"\n   ⚠️  Connectors are not created yet.")
            print(f"   This might be because:")
            print(f"      - Pipeline is still starting")
            print(f"      - Kafka Connect is unreachable (check health endpoint)")
            print(f"      - Connector creation failed")
        
        if pipeline_stat == 'STARTING':
            print(f"\n   ℹ️  Pipeline is in STARTING state.")
            print(f"   Wait a bit longer for connectors to be created.")
    
    print(f"\n" + "=" * 70)
    
except requests.exceptions.Timeout:
    print("❌ Request timed out - backend may be slow or stuck")
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



"""Check detailed pipeline status."""

import requests
import json

PIPELINE_ID = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"

print("=" * 70)
print("Pipeline Status Check")
print("=" * 70)

try:
    # Get pipeline status
    response = requests.get(
        f"http://localhost:8000/api/v1/pipelines/{PIPELINE_ID}/status",
        timeout=15
    )
    
    if response.status_code == 200:
        status = response.json()
        
        print(f"\nPipeline: {status.get('name', 'N/A')}")
        print(f"Status: {status.get('status', 'N/A')}")
        print(f"Mode: {status.get('mode', 'N/A')}")
        print(f"CDC Status: {status.get('cdc_status', 'N/A')}")
        print(f"Full Load Status: {status.get('full_load_status', 'N/A')}")
        
        # Debezium connector status
        dbz = status.get('debezium_connector', {})
        if dbz:
            print(f"\nDebezium Connector:")
            if isinstance(dbz, dict):
                conn = dbz.get('connector', {})
                if isinstance(conn, dict):
                    print(f"  State: {conn.get('state', 'N/A')}")
                    print(f"  Worker ID: {conn.get('worker_id', 'N/A')}")
                tasks = dbz.get('tasks', [])
                if tasks:
                    print(f"  Tasks: {len(tasks)}")
                    for i, task in enumerate(tasks):
                        if isinstance(task, dict):
                            print(f"    Task {i}: {task.get('state', 'N/A')} - {task.get('id', 'N/A')}")
            else:
                print(f"  {dbz}")
        
        # Sink connector status
        sink = status.get('sink_connector', {})
        if sink:
            print(f"\nSink Connector:")
            if isinstance(sink, dict):
                conn = sink.get('connector', {})
                if isinstance(conn, dict):
                    print(f"  State: {conn.get('state', 'N/A')}")
                    print(f"  Worker ID: {conn.get('worker_id', 'N/A')}")
                tasks = sink.get('tasks', [])
                if tasks:
                    print(f"  Tasks: {len(tasks)}")
                    for i, task in enumerate(tasks):
                        if isinstance(task, dict):
                            print(f"    Task {i}: {task.get('state', 'N/A')} - {task.get('id', 'N/A')}")
            else:
                print(f"  {sink}")
        else:
            print("\nSink Connector: Not found or not created")
        
        print(f"\n{json.dumps(status, indent=2)}")
    else:
        print(f"Error: Status code {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")



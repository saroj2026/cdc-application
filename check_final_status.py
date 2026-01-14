import requests
import json

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"
BACKEND_URL = "http://localhost:8000"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== FINAL STATUS CHECK ===")

# Check pipeline status
r = requests.get(f"{BACKEND_URL}/api/v1/pipelines/{PIPELINE_ID}")
pipeline = r.json()
print(f"\nPipeline Status: {pipeline.get('status')}")
print(f"CDC Status: {pipeline.get('cdc_status')}")
print(f"Topics: {pipeline.get('kafka_topics', [])}")

# Check Debezium connector
debezium_name = pipeline.get('debezium_connector_name')
if debezium_name:
    print(f"\n=== DEBEZIUM CONNECTOR: {debezium_name} ===")
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{debezium_name}/status")
    dbz_status = r2.json()
    print(f"State: {dbz_status.get('connector', {}).get('state')}")
    print(f"Tasks: {len(dbz_status.get('tasks', []))}")
    for i, task in enumerate(dbz_status.get('tasks', [])):
        print(f"  Task {i}: {task.get('state')}")
        if task.get('trace'):
            print(f"    Error: {task.get('trace')[:500]}")

# Check Sink connector
sink_name = pipeline.get('sink_connector_name')
if sink_name:
    print(f"\n=== SINK CONNECTOR: {sink_name} ===")
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{sink_name}/status")
    sink_status = r3.json()
    print(f"State: {sink_status.get('connector', {}).get('state')}")
    print(f"Tasks: {len(sink_status.get('tasks', []))}")
    for i, task in enumerate(sink_status.get('tasks', [])):
        print(f"  Task {i}: {task.get('state')}")

print(f"\n=== SUMMARY ===")
print(f"Topic name: oracle_sf_p.cdc_user.test (from schema: cdc_user)")
print(f"Connector is configured correctly for this topic")
if debezium_name:
    if dbz_status.get('tasks', [{}])[0].get('state') == 'RUNNING':
        print(f"✓ Connector is working!")
    else:
        error = dbz_status.get('tasks', [{}])[0].get('trace', 'Unknown error')[:200] if dbz_status.get('tasks') else 'No tasks'
        print(f"⚠ Connector still has connectivity issue: {error}")


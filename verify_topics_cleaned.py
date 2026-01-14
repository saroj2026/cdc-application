import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== VERIFYING TOPICS CLEANUP ===")

# Check connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"Expected topic: {expected_topic}")
print(f"Old topics (should be deleted): oracle_sf_p.c_cdc_user.test")

# Check connector status
print(f"\n=== CONNECTOR STATUS ===")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()

print(f"Connector State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")

for i, task in enumerate(status.get('tasks', [])):
    print(f"\nTask {i}:")
    print(f"  State: {task.get('state')}")
    print(f"  Worker: {task.get('worker_id')}")
    if task.get('trace'):
        error = task.get('trace')
        print(f"  Error: {error[:500]}")
    else:
        print(f"  ✓ No error!")

# Check pipeline
print(f"\n=== PIPELINE STATUS ===")
try:
    r3 = requests.get("http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04")
    pipeline = r3.json()
    print(f"Pipeline Status: {pipeline.get('status')}")
    print(f"CDC Status: {pipeline.get('cdc_status')}")
    print(f"Topics: {pipeline.get('kafka_topics', [])}")
    
    # Check for old topics in pipeline config
    old_topics = [t for t in pipeline.get('kafka_topics', []) if 'c_cdc_user' in t]
    if old_topics:
        print(f"⚠ Found old topics in pipeline config: {old_topics}")
    else:
        print(f"✓ No old topics in pipeline config")
        
except Exception as e:
    print(f"Error checking pipeline: {e}")

print(f"\n=== SUMMARY ===")
if status.get('tasks', [{}])[0].get('state') == 'RUNNING':
    print("✓ Connector is RUNNING and working!")
    print(f"✓ Using correct topic: {expected_topic}")
else:
    print("⚠ Connector task is not RUNNING")
    if status.get('tasks', [{}])[0].get('trace'):
        print(f"  Error: {status.get('tasks', [{}])[0].get('trace')[:300]}")


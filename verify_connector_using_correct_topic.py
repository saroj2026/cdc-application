"""Verify the connector is using the correct topic and check if it's working."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== VERIFYING CONNECTOR TOPIC USAGE ===")

# Get connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"Connector: {CONNECTOR_NAME}")
print(f"Schema in config: {schema}")
print(f"Table in config: {table}")
print(f"Expected topic: {expected_topic}")

# Get connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()

print(f"\n=== CONNECTOR STATUS ===")
print(f"State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")

for i, task in enumerate(status.get('tasks', [])):
    print(f"\nTask {i}:")
    print(f"  State: {task.get('state')}")
    print(f"  Worker: {task.get('worker_id')}")
    if task.get('trace'):
        error = task.get('trace')
        print(f"  Error: {error[:500]}")

# Check pipeline topics
print(f"\n=== PIPELINE TOPICS ===")
try:
    r3 = requests.get("http://localhost:8000/api/v1/pipelines/3b06bbae-2bbc-4526-ad6f-4e5d12c14f04")
    pipeline = r3.json()
    pipeline_topics = pipeline.get('kafka_topics', [])
    print(f"Pipeline topics: {pipeline_topics}")
    
    if expected_topic in pipeline_topics:
        print(f"✓ Expected topic '{expected_topic}' is in pipeline topics")
    else:
        print(f"⚠ Expected topic '{expected_topic}' NOT in pipeline topics")
        
    # Check for old topics
    old_topics = [t for t in pipeline_topics if 'c_cdc_user' in t]
    if old_topics:
        print(f"⚠ Found old topics in pipeline: {old_topics}")
        print(f"  These should be removed from pipeline configuration")
except Exception as e:
    print(f"Error checking pipeline: {e}")

print(f"\n=== SUMMARY ===")
print(f"Expected topic: {expected_topic}")
print(f"Old topics to delete: oracle_sf_p.c_cdc_user.test (duplicates)")
print(f"Current topic: oracle_sf_p.cdc_user.test")

if expected_topic == "oracle_sf_p.cdc_user.test":
    print("✓ Connector is configured correctly!")
    if status.get('connector', {}).get('state') == 'RUNNING' and status.get('tasks', [{}])[0].get('state') == 'RUNNING':
        print("✓ Connector is RUNNING and working!")
    else:
        print("⚠ Connector is not fully working - check error above")
else:
    print(f"⚠ Connector expects different topic: {expected_topic}")


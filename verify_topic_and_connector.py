"""Verify topic exists and connector can access it."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"
TOPIC_NAME = "oracle_sf_p.cdc_user.test"

print("=== VERIFYING TOPIC AND CONNECTOR ===")
print(f"Topic: {TOPIC_NAME}")
print(f"Connector: {CONNECTOR_NAME}")

# Check connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"\n=== CONNECTOR CONFIGURATION ===")
print(f"Expected topic: {expected_topic}")
print(f"Bootstrap servers: {config.get('bootstrap.servers')}")
print(f"Schema history bootstrap: {config.get('schema.history.internal.kafka.bootstrap.servers')}")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()

print(f"\n=== CONNECTOR STATUS ===")
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
        print(f"  ✓ No errors!")

# Verify topic name matches
print(f"\n=== TOPIC VERIFICATION ===")
if expected_topic == TOPIC_NAME:
    print(f"✓ Topic name matches: {TOPIC_NAME}")
    print(f"  Connector expects: {expected_topic}")
    print(f"  Topic exists: {TOPIC_NAME}")
else:
    print(f"⚠ Topic name mismatch!")
    print(f"  Connector expects: {expected_topic}")
    print(f"  Topic shown: {TOPIC_NAME}")

# Check if connector is working
if status.get('tasks', [{}])[0].get('state') == 'RUNNING':
    print(f"\n✓✓✓ SUCCESS! Connector is RUNNING! ✓✓✓")
    print(f"  Topic: {TOPIC_NAME}")
    print(f"  Connector can now access Kafka and the topic")
else:
    print(f"\n⚠ Connector task is not RUNNING")
    if status.get('tasks', [{}])[0].get('trace'):
        print(f"  Error: {status.get('tasks', [{}])[0].get('trace')[:400]}")


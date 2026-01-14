import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== DETAILED DEBEZIUM CONNECTOR STATUS ===")

# Get status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()

print(f"Connector State: {status.get('connector', {}).get('state')}")
print(f"Number of Tasks: {len(status.get('tasks', []))}")

for i, task in enumerate(status.get('tasks', [])):
    print(f"\nTask {i}:")
    print(f"  State: {task.get('state')}")
    print(f"  Worker: {task.get('worker_id')}")
    if task.get('trace'):
        print(f"  Error: {task.get('trace')}")

# Get config
print(f"\n=== CONNECTOR CONFIG ===")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r2.json()

print(f"Database server name: {config.get('database.server.name')}")
print(f"Table include list: {config.get('table.include.list')}")
print(f"Schema in config: {config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else 'N/A'}")

# Expected topic name
schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else 'N/A'
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else 'N/A'
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}" if schema != 'N/A' else 'N/A'

print(f"\nExpected topic name: {expected_topic}")
print(f"Pipeline topics: ['oracle_sf_p.cdc_user.test']")

if expected_topic == 'oracle_sf_p.cdc_user.test':
    print("✓ Topic name matches!")
else:
    print(f"⚠ Topic name mismatch!")


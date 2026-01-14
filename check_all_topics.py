import requests
import json

KAFKA_UI_URL = "http://72.61.233.209:8080"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== CHECKING ALL KAFKA TOPICS ===")

# Topics we see in the image
topics_to_check = [
    "oracle_sf_p.c_cdc_user.test",  # Old topic (from old schema c##cdc_user -> c__cdc_user)
    "oracle_sf_p.cdc_user.test",    # New topic (from new schema cdc_user)
]

print("Topics to check:")
for topic in topics_to_check:
    print(f"  - {topic}")

# Check which connector is using which topic
print("\n=== CHECKING CONNECTORS ===")
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema = config.get('table.include.list', '').split('.')[0] if '.' in config.get('table.include.list', '') else ''
table = config.get('table.include.list', '').split('.')[1] if '.' in config.get('table.include.list', '') else ''
server = config.get('database.server.name', '')
expected_topic = f"{server}.{schema}.{table}"

print(f"Connector: {CONNECTOR_NAME}")
print(f"Expected topic: {expected_topic}")
print(f"Schema in config: {schema}")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()
print(f"\nConnector State: {status.get('connector', {}).get('state')}")
print(f"Tasks: {len(status.get('tasks', []))}")

for i, task in enumerate(status.get('tasks', [])):
    print(f"Task {i}: {task.get('state')}")
    if task.get('trace'):
        print(f"  Error: {task.get('trace')[:300]}")

print(f"\n=== ANALYSIS ===")
print(f"Expected topic: {expected_topic}")
print(f"Old topic (should be deleted): oracle_sf_p.c_cdc_user.test")
print(f"New topic (should be used): oracle_sf_p.cdc_user.test")

if expected_topic == "oracle_sf_p.cdc_user.test":
    print("✓ Connector is configured for the correct topic!")
    print("⚠ But there are old duplicate topics that should be cleaned up")
else:
    print(f"⚠ Mismatch! Connector expects {expected_topic}")


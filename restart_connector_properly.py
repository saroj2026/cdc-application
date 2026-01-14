import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== RESTARTING CONNECTOR ===")
print(f"Connector: {CONNECTOR_NAME}")

# Get current status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()
print(f"Current state: {status.get('connector', {}).get('state')}")

# Restart connector
print("Restarting connector...")
try:
    r2 = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
    if r2.status_code == 204:
        print("✓ Connector restart initiated")
    else:
        print(f"Restart response: {r2.status_code} - {r2.text[:200]}")
except Exception as e:
    print(f"Error restarting: {e}")

# Wait and check status
print("Waiting 10 seconds...")
time.sleep(10)

r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status2 = r3.json()
print(f"\nNew state: {status2.get('connector', {}).get('state')}")
print(f"Tasks: {len(status2.get('tasks', []))}")

for i, task in enumerate(status2.get('tasks', [])):
    print(f"Task {i}: {task.get('state')}")
    if task.get('trace'):
        error = task.get('trace')
        print(f"  Error: {error[:300]}")


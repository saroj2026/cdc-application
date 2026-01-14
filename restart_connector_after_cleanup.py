import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== RESTARTING CONNECTOR AFTER TOPIC CLEANUP ===")

# Get current status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()
print(f"Current state: {status.get('connector', {}).get('state')}")
print(f"Current task state: {status.get('tasks', [{}])[0].get('state')}")

# Restart connector
print("\nRestarting connector...")
try:
    r2 = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
    if r2.status_code == 204:
        print("✓ Connector restart initiated")
    else:
        print(f"Response: {r2.status_code} - {r2.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Wait for restart
print("Waiting 15 seconds for connector to restart...")
time.sleep(15)

# Check new status
r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status2 = r3.json()

print(f"\n=== NEW STATUS ===")
print(f"Connector State: {status2.get('connector', {}).get('state')}")
print(f"Tasks: {len(status2.get('tasks', []))}")

for i, task in enumerate(status2.get('tasks', [])):
    print(f"\nTask {i}:")
    print(f"  State: {task.get('state')}")
    if task.get('trace'):
        print(f"  Error: {task.get('trace')[:400]}")
    else:
        print(f"  ✓ No errors - task is working!")

if status2.get('tasks', [{}])[0].get('state') == 'RUNNING':
    print("\n✓✓✓ SUCCESS! Connector is now RUNNING! ✓✓✓")
else:
    print("\n⚠ Connector is still not RUNNING")
    print("The topic cleanup didn't resolve the issue")
    print("This suggests a deeper Kafka connectivity problem")


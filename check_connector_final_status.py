"""Final check of connector status after fix."""
import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== FINAL CONNECTOR STATUS CHECK ===")

# Wait a bit for connector to fully start
print("Waiting 10 seconds for connector to fully start...")
time.sleep(10)

# Check connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()
has_bootstrap = config.get('bootstrap.servers') is not None

print(f"\n1. Configuration:")
print(f"   Has bootstrap.servers: {has_bootstrap}")
if has_bootstrap:
    print(f"   ⚠ ERROR: Still has bootstrap.servers!")
else:
    print(f"   ✓ bootstrap.servers removed (correct)")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()
connector_state = status.get('connector', {}).get('state')
tasks = status.get('tasks', [])

print(f"\n2. Status:")
print(f"   Connector state: {connector_state}")
print(f"   Number of tasks: {len(tasks)}")

if tasks:
    task_state = tasks[0].get('state')
    print(f"   Task 0 state: {task_state}")
    
    if task_state == 'RUNNING':
        print(f"\n   ✓ SUCCESS: Connector task is RUNNING!")
    elif task_state == 'FAILED':
        error = tasks[0].get('trace', 'Unknown error')[:400]
        print(f"\n   ⚠ Task is FAILED")
        print(f"   Error: {error}")
    else:
        print(f"\n   Task state: {task_state}")
else:
    print(f"\n   ⚠ No tasks found")

print(f"\n=== SUMMARY ===")
if not has_bootstrap and tasks and tasks[0].get('state') == 'RUNNING':
    print("✓✓✓ FIX SUCCESSFUL: bootstrap.servers removed AND connector is RUNNING!")
elif not has_bootstrap:
    print("✓ Configuration fixed (bootstrap.servers removed), but connector needs more time or has issues")
else:
    print("⚠ Configuration not updated - bootstrap.servers still present")


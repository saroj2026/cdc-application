"""Detailed connector check with full status."""
import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== DETAILED CONNECTOR STATUS CHECK ===")

# Wait a bit for tasks to start
print("Waiting 5 seconds for tasks to initialize...")
time.sleep(5)

# Check connector status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()

connector_state = status.get('connector', {}).get('state')
tasks = status.get('tasks', [])

print(f"\nConnector state: {connector_state}")
print(f"Number of tasks: {len(tasks)}")

if tasks:
    for i, task in enumerate(tasks):
        task_state = task.get('state')
        task_id = task.get('id')
        print(f"\nTask {i} (ID: {task_id}):")
        print(f"  State: {task_state}")
        
        if task_state == 'RUNNING':
            print(f"  ✓✓✓ SUCCESS: Task is RUNNING!")
        elif task_state == 'FAILED':
            error = task.get('trace', 'Unknown error')
            print(f"  ⚠ Task is FAILED")
            print(f"  Error: {error[:600]}")
        else:
            print(f"  State: {task_state}")
else:
    print("\n⚠ No tasks found yet (may still be starting)")

# Check config
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r2.json()
schema_history_bs = config.get('schema.history.internal.kafka.bootstrap.servers')

print(f"\n=== CONFIGURATION ===")
print(f"Schema history bootstrap servers: {schema_history_bs}")

if schema_history_bs == 'kafka-cdc:29092':
    print("✓ Configuration correct: Using kafka-cdc:29092")
elif schema_history_bs:
    print(f"⚠ Configuration: {schema_history_bs} (should be kafka-cdc:29092)")

print(f"\n=== SUMMARY ===")
if tasks and tasks[0].get('state') == 'RUNNING' and schema_history_bs == 'kafka-cdc:29092':
    print("✓✓✓ SUCCESS: Connector is configured correctly and RUNNING!")
elif schema_history_bs == 'kafka-cdc:29092':
    print("✓ Configuration correct, but connector needs more time or has issues")
else:
    print("⚠ Configuration needs update or connector needs restart")


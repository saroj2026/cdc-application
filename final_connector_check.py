"""Final check of Oracle connector after fixing to use kafka-cdc:29092."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== FINAL CONNECTOR CHECK ===")

# Check connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r.json()

schema_history_bs = config.get('schema.history.internal.kafka.bootstrap.servers')
print(f"\nSchema history bootstrap servers: {schema_history_bs}")

if schema_history_bs == 'kafka-cdc:29092':
    print("✓ Correct: Using kafka-cdc:29092")
elif schema_history_bs == 'kafka:29092':
    print("⚠ Wrong: Still using kafka:29092 (should be kafka-cdc:29092)")
else:
    print(f"ℹ Using: {schema_history_bs}")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r2.json()
connector_state = status.get('connector', {}).get('state')
tasks = status.get('tasks', [])

print(f"\nConnector state: {connector_state}")
print(f"Number of tasks: {len(tasks)}")

if tasks:
    task_state = tasks[0].get('state')
    print(f"Task 0 state: {task_state}")
    
    if task_state == 'RUNNING':
        print("\n✓✓✓ SUCCESS: Connector task is RUNNING!")
    elif task_state == 'FAILED':
        error = tasks[0].get('trace', 'Unknown error')[:500]
        print(f"\n⚠ Task is FAILED")
        print(f"Error: {error}")
    else:
        print(f"\nTask state: {task_state}")


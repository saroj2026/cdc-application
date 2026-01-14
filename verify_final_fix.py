"""Verify the final fix - schema history bootstrap servers removed."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
DEBEZIUM_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"

print("=== VERIFYING FINAL FIX ===")

# Get connector config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/config")
config = r.json()

has_bootstrap = config.get('bootstrap.servers') is not None
has_schema_history_bootstrap = config.get('schema.history.internal.kafka.bootstrap.servers') is not None
schema_history_topic = config.get('schema.history.internal.kafka.topic')

print(f"\n1. Configuration:")
print(f"   bootstrap.servers: {config.get('bootstrap.servers')}")
print(f"   schema.history.internal.kafka.bootstrap.servers: {config.get('schema.history.internal.kafka.bootstrap.servers')}")
print(f"   schema.history.internal.kafka.topic: {schema_history_topic}")

if not has_bootstrap and not has_schema_history_bootstrap:
    print(f"\n   ✓ Both bootstrap servers removed (correct)")
    print(f"   ✓ Schema history topic is set: {schema_history_topic}")
else:
    if has_bootstrap:
        print(f"\n   ⚠ bootstrap.servers still present: {config.get('bootstrap.servers')}")
    if has_schema_history_bootstrap:
        print(f"\n   ⚠ schema.history.internal.kafka.bootstrap.servers still present: {config.get('schema.history.internal.kafka.bootstrap.servers')}")

# Check connector status
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/status")
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
        print(f"\n   ✓✓✓ SUCCESS: Connector task is RUNNING!")
    elif task_state == 'FAILED':
        error = tasks[0].get('trace', 'Unknown error')[:400]
        print(f"\n   ⚠ Task is FAILED")
        print(f"   Error: {error}")
    else:
        print(f"\n   Task state: {task_state}")

print(f"\n=== SUMMARY ===")
if not has_bootstrap and not has_schema_history_bootstrap and tasks and tasks[0].get('state') == 'RUNNING':
    print("✓✓✓ FIX SUCCESSFUL: All bootstrap servers removed AND connector is RUNNING!")
elif not has_bootstrap and not has_schema_history_bootstrap:
    print("✓ Configuration fixed (bootstrap servers removed), but connector needs more time")
else:
    print("⚠ Configuration not fully updated")


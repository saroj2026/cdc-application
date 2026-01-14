"""Verify that the Oracle connector no longer has bootstrap.servers and is working."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
BACKEND_URL = "http://localhost:8000"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== VERIFYING CONNECTOR FIX ===")

# Check connector config
print(f"\n1. Checking connector configuration...")
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
if r.status_code != 200:
    print(f"Error getting connector config: {r.status_code}")
    print(r.text)
    exit(1)

config = r.json()
has_bootstrap_servers = config.get('bootstrap.servers') is not None
schema_history_bootstrap = config.get('schema.history.internal.kafka.bootstrap.servers')

print(f"   Has bootstrap.servers: {has_bootstrap_servers}")
print(f"   Bootstrap servers value: {config.get('bootstrap.servers')}")
print(f"   Schema history bootstrap: {schema_history_bootstrap}")

if has_bootstrap_servers:
    print(f"\n   ⚠ ERROR: Connector still has bootstrap.servers configured!")
    print(f"   This should have been removed.")
else:
    print(f"\n   ✓ Connector does NOT have bootstrap.servers (correct)")
    print(f"   ✓ Schema history bootstrap is set: {schema_history_bootstrap}")

# Check connector status
print(f"\n2. Checking connector status...")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
if r2.status_code != 200:
    print(f"Error getting connector status: {r2.status_code}")
    print(r2.text)
    exit(1)

status = r2.json()
connector_state = status.get('connector', {}).get('state')
tasks = status.get('tasks', [])
print(f"   Connector state: {connector_state}")
print(f"   Number of tasks: {len(tasks)}")

if tasks:
    task_state = tasks[0].get('state')
    print(f"   Task 0 state: {task_state}")
    
    if task_state == 'RUNNING':
        print(f"\n   ✓ Connector task is RUNNING (success!)")
    elif task_state == 'FAILED':
        error = tasks[0].get('trace', 'Unknown error')
        print(f"\n   ⚠ Connector task is FAILED")
        print(f"   Error: {error[:400]}")
    else:
        print(f"\n   ⚠ Connector task state: {task_state}")

# Check pipeline status
print(f"\n3. Checking pipeline status...")
r3 = requests.get(f"{BACKEND_URL}/api/v1/pipelines")
pipelines = r3.json()
oracle_pipelines = [p for p in pipelines if 'oracle' in p.get('name', '').lower() and 'sf' in p.get('name', '').lower()]
if oracle_pipelines:
    pipeline = oracle_pipelines[0]
    print(f"   Pipeline: {pipeline.get('name')}")
    print(f"   Status: {pipeline.get('status')}")
    print(f"   CDC status: {pipeline.get('cdc_status')}")

print(f"\n=== SUMMARY ===")
if not has_bootstrap_servers and tasks and tasks[0].get('state') == 'RUNNING':
    print("✓ Fix successful: bootstrap.servers removed and connector is RUNNING")
elif not has_bootstrap_servers:
    print("✓ bootstrap.servers removed, but connector needs restart")
else:
    print("⚠ bootstrap.servers still present - configuration not updated")

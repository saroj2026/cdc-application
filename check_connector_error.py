"""Check the full connector error to understand why it's failing."""
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=== CHECKING CONNECTOR ERROR ===")

# Get connector status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
status = r.json()

print(f"\nConnector state: {status.get('connector', {}).get('state')}")
tasks = status.get('tasks', [])

if tasks:
    task = tasks[0]
    task_state = task.get('state')
    print(f"\nTask state: {task_state}")
    
    if task_state == 'FAILED':
        error_trace = task.get('trace', '')
        print(f"\n=== FULL ERROR TRACE ===")
        print(error_trace)
        
        # Extract key error messages
        if "change event producer" in error_trace.lower():
            print("\n⚠ Error is related to change event producer")
        if "logminer" in error_trace.lower():
            print("⚠ Error mentions LogMiner")
        if "oracle" in error_trace.lower():
            print("⚠ Error mentions Oracle")
        if "connection" in error_trace.lower():
            print("⚠ Error mentions connection")

# Get connector config to see what it's configured with
print(f"\n=== CONNECTOR CONFIGURATION ===")
r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
config = r2.json()

print(f"Database hostname: {config.get('database.hostname')}")
print(f"Database port: {config.get('database.port')}")
print(f"Database user: {config.get('database.user')}")
print(f"Database dbname: {config.get('database.dbname')}")
print(f"Database server name: {config.get('database.server.name')}")
print(f"Table include list: {config.get('table.include.list')}")
print(f"Snapshot mode: {config.get('snapshot.mode')}")
print(f"Database connection adapter: {config.get('database.connection.adapter')}")

print(f"\n=== ANALYSIS ===")
print(f"The connector is FAILED, which means it cannot start capturing changes.")
print(f"The topic won't be created until the connector successfully starts.")
print(f"We need to fix the connector error first before the topic will be assigned.")

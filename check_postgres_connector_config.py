"""Check PostgreSQL connector config to see if it has bootstrap.servers."""
import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

# Find a PostgreSQL connector
print("=== CHECKING POSTGRESQL CONNECTOR ===")
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r.json()

pg_connectors = [c for c in connectors if 'pg-' in c]
if pg_connectors:
    pg_conn = pg_connectors[0]
    print(f"Checking connector: {pg_conn}")
    
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{pg_conn}/config")
    config = r2.json()
    
    print(f"Has bootstrap.servers: {config.get('bootstrap.servers') is not None}")
    print(f"Bootstrap servers value: {config.get('bootstrap.servers')}")
    print(f"Schema history bootstrap: {config.get('schema.history.internal.kafka.bootstrap.servers')}")
    
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{pg_conn}/status")
    status = r3.json()
    print(f"State: {status.get('connector', {}).get('state')}")
    print(f"Tasks: {len(status.get('tasks', []))}")
    if status.get('tasks'):
        print(f"Task 0 state: {status['tasks'][0].get('state')}")
else:
    print("No PostgreSQL connectors found")


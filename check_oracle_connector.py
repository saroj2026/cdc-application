import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

# Get all connectors
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r.json()
print("All connectors:", connectors)

# Find Oracle connector
oracle_conn = [c for c in connectors if 'oracle' in c.lower()]
print("\nOracle connectors:", oracle_conn)

if oracle_conn:
    conn_name = oracle_conn[0]
    print(f"\n=== Checking connector: {conn_name} ===")
    
    # Get status
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status")
    print("\nStatus:")
    print(json.dumps(r2.json(), indent=2))
    
    # Get config
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config")
    config = r3.json()
    print("\nConfig (key fields):")
    print(f"  Snapshot mode: {config.get('snapshot.mode')}")
    print(f"  Connection adapter: {config.get('database.connection.adapter')}")
    print(f"  Database: {config.get('database.dbname')}")
    print(f"  Table include: {config.get('table.include.list')}")


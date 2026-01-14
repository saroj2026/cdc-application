import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=== CHECKING FOR DUPLICATE CONNECTORS ===")

# Get all connectors
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r.json()

print(f"Total connectors: {len(connectors)}")

# Find Oracle connectors for oracle_sf_p pipeline
oracle_connectors = [c for c in connectors if 'oracle_sf_p' in c and 'cdc' in c]
print(f"\nOracle CDC connectors for oracle_sf_p:")
for conn in oracle_connectors:
    print(f"  - {conn}")
    
    # Get status
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn}/status")
    status = r2.json()
    state = status.get('connector', {}).get('state')
    tasks = len(status.get('tasks', []))
    print(f"    State: {state}, Tasks: {tasks}")
    
    # Get config
    r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn}/config")
    config = r3.json()
    table_list = config.get('table.include.list', 'N/A')
    print(f"    Table include list: {table_list}")

# Identify which one is old and which is new
old_connector = None
new_connector = None

for conn in oracle_connectors:
    if 'c_cdc_user' in conn:  # Old one with double underscore (from c##cdc_user)
        old_connector = conn
    elif 'cdc_user' in conn and 'c_cdc_user' not in conn:  # New one
        new_connector = conn

print(f"\n=== IDENTIFIED ===")
print(f"Old connector (should be deleted): {old_connector}")
print(f"New connector (should be kept): {new_connector}")

if old_connector:
    print(f"\n⚠ Old connector '{old_connector}' should be deleted!")
    print(f"  It's using the old schema name and may cause conflicts")


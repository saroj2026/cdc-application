"""Check and fix Debezium connector configuration."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Checking Debezium Connector Configuration")
print("=" * 80)

connector_name = "cdc-final_test-pg-public"

# Get current config
print(f"\n1. Getting current configuration for {connector_name}...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
    if response.status_code == 200:
        config = response.json()
        
        print(f"\n   Current configuration:")
        print(f"   Database: {config.get('database.dbname')}")
        print(f"   Tables: {config.get('table.include.list')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode')}")
        print(f"   Plugin: {config.get('plugin.name')}")
        print(f"   Slot name: {config.get('slot.name')}")
        print(f"   Publication: {config.get('publication.name')}")
        
        # Check if snapshot mode is correct
        snapshot_mode = config.get('snapshot.mode', '')
        if snapshot_mode == 'initial_only':
            print(f"\n   ⚠️  Snapshot mode is 'initial_only' - this only captures schema, not data changes!")
            print(f"   For CDC, we need 'never' or 'initial' mode")
            print(f"   However, since full load was done, 'never' should be used to start streaming immediately")
        
        # Check publication autocreate
        pub_autocreate = config.get('publication.autocreate.mode', '')
        print(f"   Publication autocreate: {pub_autocreate}")
        
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Get status
print(f"\n2. Getting connector status...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error: {task.get('trace')[:300]}")
                
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)


import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Checking Debezium Connector Configuration")
print("=" * 80)

connector_name = "cdc-final_test-pg-public"

# Get current config
print(f"\n1. Getting current configuration for {connector_name}...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
    if response.status_code == 200:
        config = response.json()
        
        print(f"\n   Current configuration:")
        print(f"   Database: {config.get('database.dbname')}")
        print(f"   Tables: {config.get('table.include.list')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode')}")
        print(f"   Plugin: {config.get('plugin.name')}")
        print(f"   Slot name: {config.get('slot.name')}")
        print(f"   Publication: {config.get('publication.name')}")
        
        # Check if snapshot mode is correct
        snapshot_mode = config.get('snapshot.mode', '')
        if snapshot_mode == 'initial_only':
            print(f"\n   ⚠️  Snapshot mode is 'initial_only' - this only captures schema, not data changes!")
            print(f"   For CDC, we need 'never' or 'initial' mode")
            print(f"   However, since full load was done, 'never' should be used to start streaming immediately")
        
        # Check publication autocreate
        pub_autocreate = config.get('publication.autocreate.mode', '')
        print(f"   Publication autocreate: {pub_autocreate}")
        
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Get status
print(f"\n2. Getting connector status...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error: {task.get('trace')[:300]}")
                
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)


"""Revert Debezium connector to original working configuration."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
connector_name = "cdc-ps_sn_p-pg-public"

print("=" * 70)
print("Reverting Debezium Connector Configuration")
print("=" * 70)

try:
    # Get current config
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        
        # Revert: Use table.include.list with schema prefix, remove schema.include.list
        # For filtered publications, Debezium needs table.include.list with schema.table format
        config['table.include.list'] = 'public.projects_simple'
        if 'schema.include.list' in config:
            del config['schema.include.list']
        
        print(f"\n1. Reverting configuration...")
        print(f"   table.include.list: {config['table.include.list']}")
        print(f"   schema.include.list: (removed)")
        
        # Update config
        update_response = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
            json=config,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if update_response.status_code == 200:
            print("   ✅ Configuration reverted")
        else:
            print(f"   ❌ Update failed: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
        
        # Restart connector
        print(f"\n2. Restarting connector...")
        restart_response = requests.post(
            f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/restart",
            timeout=10
        )
        
        if restart_response.status_code == 204 or restart_response.status_code == 200:
            print("   ✅ Connector restarted")
        else:
            print(f"   ⚠️  Restart response: {restart_response.status_code}")
        
        # Wait and check status
        print(f"\n3. Waiting 5 seconds and checking status...")
        time.sleep(5)
        
        status_response = requests.get(
            f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status",
            timeout=10
        )
        
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"   Connector State: {status.get('connector', {}).get('state', 'N/A')}")
            tasks = status.get('tasks', [])
            for task in tasks:
                print(f"   Task {task.get('id')}: {task.get('state', 'N/A')}")
                if task.get('state') == 'FAILED':
                    trace = task.get('trace', '')
                    print(f"      Error: {trace[:300]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)



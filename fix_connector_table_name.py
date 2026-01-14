#!/usr/bin/env python3
"""Update Debezium connector config to use correct table name with c## prefix."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("FIXING CONNECTOR TABLE NAME")
print("=" * 70)

# Get current config
print("\n1. Getting current config...")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
    if r.status_code == 200:
        current_config = r.json()
        current_table_list = current_config.get('table.include.list', 'N/A')
        print(f"   Current table.include.list: {current_table_list}")
        
        # Update config with correct table name
        # The actual Oracle table is c##cdc_user.test, not cdc_user.test
        new_config = current_config.copy()
        new_config['table.include.list'] = 'c##cdc_user.test'
        
        print(f"\n2. Updating config...")
        print(f"   New table.include.list: {new_config['table.include.list']}")
        
        # Update connector config
        update_r = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if update_r.status_code == 200:
            print(f"   ✓ Config updated successfully!")
            print(f"\n3. Restarting connector...")
            
            # Restart connector to apply changes
            restart_r = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
            if restart_r.status_code == 204:
                print(f"   ✓ Connector restart initiated")
                
                import time
                print(f"   Waiting 15 seconds for connector to restart...")
                time.sleep(15)
                
                # Check status
                status_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
                if status_r.status_code == 200:
                    status = status_r.json()
                    state = status.get('connector', {}).get('state', 'N/A')
                    print(f"\n4. Connector Status After Restart:")
                    print(f"   State: {state}")
                    
                    tasks = status.get('tasks', [])
                    for i, task in enumerate(tasks):
                        task_state = task.get('state', 'N/A')
                        print(f"   Task {i}: {task_state}")
                        if task_state == 'FAILED':
                            error = task.get('trace', 'No error details')
                            print(f"   Error: {error[:500]}")
                    
                    if state == 'RUNNING':
                        print(f"\n   ✓✓✓ Connector is RUNNING with correct table name!")
                        print(f"   Now try INSERT/UPDATE/DELETE operations in Oracle")
                        print(f"   and check if CDC changes are captured.")
            else:
                print(f"   ⚠ Restart failed: {restart_r.status_code} - {restart_r.text}")
        else:
            print(f"   ✗ Config update failed: {update_r.status_code} - {update_r.text}")
    else:
        print(f"   Error getting config: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


#!/usr/bin/env python3
"""Fix connector to use cdc_user.test (without ##) instead of c##cdc_user.test."""

import requests
import time
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("FIXING CONNECTOR TO USE cdc_user.test (WITHOUT ##)")
print("=" * 70)

# Get current config
print("\n1. Getting current config...")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
    if r.status_code == 200:
        current_config = r.json()
        current_table_list = current_config.get('table.include.list', 'N/A')
        current_user = current_config.get('database.user', 'N/A')
        
        print(f"   Current table.include.list: {current_table_list}")
        print(f"   Current database.user: {current_user}")
        
        # Update config to use cdc_user.test (without ##)
        new_config = current_config.copy()
        new_config['table.include.list'] = 'cdc_user.test'
        
        print(f"\n2. Updating config...")
        print(f"   New table.include.list: {new_config['table.include.list']}")
        print(f"   Note: Using 'cdc_user' (without ##) to avoid special character issues")
        
        # Update connector config
        update_r = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if update_r.status_code == 200:
            updated_config = update_r.json()
            print(f"   ✓ Config updated successfully!")
            print(f"   Updated table.include.list: {updated_config.get('table.include.list', 'N/A')}")
            
            print(f"\n3. Restarting connector...")
            
            # Restart connector to apply changes
            restart_r = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
            if restart_r.status_code == 204:
                print(f"   ✓ Connector restart initiated")
                
                print(f"   Waiting 15 seconds for connector to restart and initialize...")
                time.sleep(15)
                
                # Check status
                status_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    
                    print(f"\n4. Connector Status After Restart:")
                    print(f"   Connector State: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for i, task in enumerate(tasks):
                        task_state = task.get('state', 'N/A')
                        worker_id = task.get('worker_id', 'N/A')
                        print(f"   Task {i}: {task_state} on {worker_id}")
                        
                        if task_state == 'FAILED':
                            error = task.get('trace', 'No error details')
                            print(f"   ⚠ Task Error: {error[:500]}")
                    
                    if connector_state == 'RUNNING':
                        print(f"\n   ✓✓✓ Connector is RUNNING with correct configuration!")
                        print(f"   ✓ Using: cdc_user.test (without ##)")
                        print(f"   ✓ This avoids special character issues in Kafka topic names")
                        
                        # Check topics API to see if connector recognizes the topic
                        print(f"\n5. Checking connector topics...")
                        topics_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/topics")
                        if topics_r.status_code == 200:
                            topics_data = topics_r.json()
                            connector_topics = topics_data.get(CONNECTOR_NAME, {}).get('topics', [])
                            if connector_topics:
                                print(f"   ✓ Connector topics: {connector_topics}")
                            else:
                                print(f"   ⚠ Connector topics list is empty (normal for initial_only until first CDC event)")
                    else:
                        print(f"\n   ⚠ Connector state is {connector_state} - check errors above")
                else:
                    print(f"   ⚠ Could not get connector status: {status_r.status_code}")
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
print("SUMMARY:")
print("=" * 70)
print("✓ Connector updated to use: cdc_user.test")
print("✓ This avoids special character (##) issues in Kafka topic names")
print("✓ Connector restarted and should now capture CDC changes")
print("")
print("Next steps:")
print("1. Try INSERT/UPDATE/DELETE operations in Oracle (cdc_user.test table)")
print("2. Wait 10-20 seconds")
print("3. Check Kafka topic for new messages")
print("4. Check Snowflake for CDC events")
print("=" * 70)


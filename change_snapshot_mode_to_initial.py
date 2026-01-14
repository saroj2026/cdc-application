#!/usr/bin/env python3
"""Change snapshot mode from initial_only to initial to enable streaming."""

import requests
import time

print("=" * 70)
print("CHANGING SNAPSHOT MODE TO ENABLE STREAMING")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        
        # Change to 'initial' which does snapshot + streaming
        print("\n2. Changing snapshot.mode from 'initial_only' to 'initial'...")
        print("   'initial_only' = snapshot only, no streaming")
        print("   'initial' = snapshot + streaming (CDC)")
        
        new_config = config.copy()
        new_config['snapshot.mode'] = 'initial'
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            updated_config = update_r.json()
            print(f"   ✓ Config updated successfully!")
            print(f"   New snapshot.mode: {updated_config.get('snapshot.mode', 'N/A')}")
            
            print("\n3. Restarting connector to apply changes...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✓ Connector restart initiated")
                print("   Waiting 30 seconds for connector to initialize and start streaming...")
                time.sleep(30)
                
                print("\n4. Verifying connector status...")
                status_r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    print(f"   Connector state: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        task_state = task.get('state', 'N/A')
                        print(f"   Task {task.get('id', 'N/A')} state: {task_state}")
                
                print("\n✓✓✓ Configuration updated and connector restarted!")
                print("\n5. Next steps:")
                print("   - Wait 1-2 minutes for connector to complete snapshot and start streaming")
                print("   - Then test CDC by inserting/updating/deleting data in Oracle")
                print("   - Check Kafka topic for new messages")
            else:
                print(f"   ⚠ Restart failed: {restart_r.status_code}")
        else:
            print(f"   ✗ Config update failed: {update_r.status_code} - {update_r.text}")
    else:
        print(f"   Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


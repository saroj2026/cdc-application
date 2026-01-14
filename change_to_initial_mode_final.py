#!/usr/bin/env python3
"""Change to 'initial' mode now that continuous mining is disabled."""

import requests
import time

print("=" * 70)
print("CHANGING TO 'initial' MODE (WITH CONTINUOUS MINE DISABLED)")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        print(f"   Current log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
        
        print("\n2. Changing snapshot.mode to 'initial'...")
        print("   'initial' = snapshot + streaming (CDC)")
        print("   Since continuous.mine is disabled, this should work now")
        
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
            
            print("\n3. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✓ Connector restart initiated")
                print("   Waiting 40 seconds for snapshot to complete and streaming to start...")
                time.sleep(40)
                
                print("\n4. Verifying connector status...")
                status_r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    print(f"   Connector state: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        task_state = task.get('state', 'N/A')
                        task_id = task.get('id', 'N/A')
                        print(f"   Task {task_id} state: {task_state}")
                        
                        if task_state == 'FAILED':
                            trace = task.get('trace', '')
                            if trace:
                                print(f"\n   ⚠ Task Error:")
                                print(f"   {trace[:800]}")
                        elif task_state == 'RUNNING':
                            print(f"\n   ✓✓✓ Connector is RUNNING!")
                            print(f"   'initial' mode should enable streaming after snapshot")
                            print(f"   Wait a bit longer for snapshot to complete, then streaming will start")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


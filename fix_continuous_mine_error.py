#!/usr/bin/env python3
"""Fix ORA-44609 error by disabling continuous mine."""

import requests
import time

print("=" * 70)
print("FIXING ORA-44609: CONTINUOUS_MINE DESUPPORTED ERROR")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
        print(f"   Current log.mining.strategy: {config.get('log.mining.strategy', 'N/A')}")
        
        print("\n2. The Error: ORA-44609 - CONTINUOUS_MINE is desupported")
        print("   Solution: Disable continuous mining")
        
        print("\n3. Updating configuration to disable continuous mining...")
        new_config = config.copy()
        new_config['log.mining.continuous.mine'] = 'false'
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            updated_config = update_r.json()
            print(f"   ✓ Config updated successfully!")
            print(f"   New log.mining.continuous.mine: {updated_config.get('log.mining.continuous.mine', 'N/A')}")
            
            print("\n4. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✓ Connector restart initiated")
                print("   Waiting 30 seconds for connector to initialize...")
                time.sleep(30)
                
                print("\n5. Verifying connector status...")
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
                                print(f"\n   ⚠ Task Error (first 500 chars):")
                                print(f"   {trace[:500]}")
                        
                        if task_state == 'RUNNING':
                            print(f"\n   ✓✓✓ Connector is RUNNING!")
                            print(f"   LogMiner should now work without CONTINUOUS_MINE")
                            print(f"\n6. Next: Test CDC operations")
                            print(f"   - Insert/Update/Delete data in Oracle")
                            print(f"   - Check Kafka topic for new messages")
                            print(f"   - Verify CDC events in Snowflake")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


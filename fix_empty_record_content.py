#!/usr/bin/env python3
"""Remove ExtractNewRecordState transform to preserve full Debezium envelope."""

import requests
import time

print("=" * 70)
print("FIXING EMPTY RECORD_CONTENT - REMOVING TRANSFORM")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        
        print(f"   Current transforms: {config.get('transforms', 'N/A')}")
        
        print(f"\n2. Removing ExtractNewRecordState transform...")
        print("-" * 70)
        
        # Remove transform-related configs
        updated_config = config.copy()
        
        # Remove transform configuration
        if 'transforms' in updated_config:
            del updated_config['transforms']
            print(f"   ✅ Removed 'transforms'")
        
        # Remove all transform.* keys
        keys_to_remove = [key for key in updated_config.keys() if key.startswith('transforms.')]
        for key in keys_to_remove:
            del updated_config[key]
            print(f"   ✅ Removed '{key}'")
        
        print(f"\n   Updated configuration:")
        print(f"     Transforms: {updated_config.get('transforms', 'N/A (removed)')}")
        print(f"     ")
        print(f"   This will preserve full Debezium envelope:")
        print(f"     - 'op' field (operation type: c/u/d)")
        print(f"     - 'after' field (new state)")
        print(f"     - 'before' field (old state)")
        
        print(f"\n3. Updating connector configuration...")
        print("-" * 70)
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{sink_connector}/config",
            json=updated_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            print(f"   ✅ Configuration updated successfully!")
            
            print(f"\n4. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector}/restart", timeout=10)
            if restart_r.status_code == 204:
                print(f"   ✅ Connector restart initiated")
                print(f"   Waiting 20 seconds for restart...")
                time.sleep(20)
                
                # Check status
                status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    tasks = status.get('tasks', [])
                    print(f"\n   Connector status: {connector_state}")
                    for task in tasks:
                        task_state = task.get('state', 'N/A')
                        print(f"   Task {task.get('id')}: {task_state}")
                        
                        if task_state == 'FAILED':
                            trace = task.get('trace', '')
                            if trace:
                                print(f"     ⚠ Error: {trace[:500]}")
                        elif task_state == 'RUNNING':
                            print(f"     ✅ Connector is RUNNING!")
            else:
                print(f"   ⚠ Restart response: {restart_r.status_code}")
        else:
            print(f"   ❌ Config update failed: {update_r.status_code}")
            print(f"   Response: {update_r.text}")
    else:
        print(f"   ❌ Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Wait 60 seconds for buffer flush")
print("  2. Insert/update/delete data in Oracle")
print("  3. Check Snowflake - RECORD_CONTENT should now have:")
print("     - 'op' field (c/u/d)")
print("     - 'after' field (new state)")
print("     - 'before' field (old state, for u/d)")
print("  4. DELETE operations will now show 'before' data instead of empty")
print("=" * 70)


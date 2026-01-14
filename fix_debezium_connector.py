"""Fix Debezium connector configuration and restart it."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
connector_name = "cdc-ps_sn_p-pg-public"

print("=" * 70)
print("Fixing Debezium Connector Configuration")
print("=" * 70)

try:
    # Get current config
    print(f"\n1. Getting current configuration...")
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        
        print(f"   Current table.include.list: {config.get('table.include.list')}")
        
        # Fix: table.include.list should be just table name, schema.include.list should be set
        # OR keep table.include.list with schema but ensure schema.include.list is not set
        
        # Option 1: Use schema.include.list + table.include.list (just table names)
        table_include = config.get('table.include.list', '')
        if '.' in table_include:
            # Extract schema and table
            parts = table_include.split('.')
            if len(parts) >= 2:
                schema = parts[0]
                table = '.'.join(parts[1:])
                
                # Update config: set schema.include.list and table.include.list (just table)
                config['schema.include.list'] = schema
                config['table.include.list'] = table
                
                print(f"\n2. Updating configuration...")
                print(f"   schema.include.list: {schema}")
                print(f"   table.include.list: {table}")
                
                # Restart connector first
                print(f"\n3. Restarting connector...")
                restart_response = requests.post(
                    f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/restart",
                    timeout=10
                )
                
                if restart_response.status_code == 204 or restart_response.status_code == 200:
                    print("   ✅ Connector restarted")
                else:
                    print(f"   ⚠️  Restart response: {restart_response.status_code}")
                
                time.sleep(2)
                
                # Update config
                update_response = requests.put(
                    f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
                    json=config,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if update_response.status_code == 200:
                    print("   ✅ Configuration updated")
                    result = update_response.json()
                    print(f"   New table.include.list: {result.get('config', {}).get('table.include.list', 'N/A')}")
                    print(f"   New schema.include.list: {result.get('config', {}).get('schema.include.list', 'N/A')}")
                else:
                    print(f"   ❌ Update failed: {update_response.status_code}")
                    print(f"   Response: {update_response.text}")
                
                # Wait and check status
                print(f"\n4. Waiting 5 seconds and checking status...")
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
            else:
                print("   ⚠️  Could not parse table.include.list format")
        else:
            print("   ✅ table.include.list format looks correct (no schema prefix)")
    else:
        print(f"   ❌ Error getting config: {config_response.status_code}")
        print(f"   Response: {config_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)



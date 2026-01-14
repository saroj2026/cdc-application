#!/usr/bin/env python3
"""Fix connector to preserve Debezium operation field in metadata."""

import requests
import time

print("=" * 70)
print("FIXING CONNECTOR TO PRESERVE OPERATION FIELD")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        
        print(f"   Current transforms: {config.get('transforms', 'N/A')}")
        
        print("\n2. Updating configuration to preserve operation...")
        print("-" * 70)
        
        # The issue: ExtractNewRecordState removes Debezium metadata
        # Solution: Configure it to add operation to headers, or use a different approach
        # Actually, Snowflake connector can handle Debezium envelope directly
        # But we need to configure it properly
        
        # Option 1: Remove the transform and let Snowflake handle Debezium envelope
        # Option 2: Use ExtractNewRecordState but configure it to add operation to headers
        # Option 3: Use a custom transform chain
        
        # Let's try Option 2 first: Configure ExtractNewRecordState to add operation to headers
        new_config = config.copy()
        
        # Keep the transform but configure it to add operation to headers
        # ExtractNewRecordState can add fields to headers
        new_config['transforms'] = 'unwrap,addOperation'
        new_config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
        new_config['transforms.unwrap.drop.tombstones'] = 'false'
        new_config['transforms.unwrap.delete.handling.mode'] = 'none'
        
        # Add operation to headers using HeaderFrom transform
        # This will preserve the operation in headers, which Snowflake connector can use
        new_config['transforms.addOperation.type'] = 'org.apache.kafka.connect.transforms.HeaderFrom$Value'
        new_config['transforms.addOperation.fields'] = '__op'
        new_config['transforms.addOperation.headers'] = '__op'
        
        # Actually, a better approach: Use Flatten transform to preserve all metadata
        # Or remove the transform entirely and let Snowflake handle the Debezium envelope
        
        # Let's try removing the transform and see if Snowflake can handle Debezium envelope
        print("   Trying approach: Remove ExtractNewRecordState transform")
        print("   Let Snowflake connector handle Debezium envelope directly")
        
        # Remove transforms - Snowflake connector should handle Debezium format
        new_config.pop('transforms', None)
        new_config.pop('transforms.unwrap.type', None)
        new_config.pop('transforms.unwrap.drop.tombstones', None)
        new_config.pop('transforms.unwrap.delete.handling.mode', None)
        new_config.pop('transforms.addOperation.type', None)
        new_config.pop('transforms.addOperation.fields', None)
        new_config.pop('transforms.addOperation.headers', None)
        
        # Ensure value converter is set for Debezium format
        new_config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
        new_config['value.converter.schemas.enable'] = 'true'
        
        print(f"   Removed transforms - connector will handle Debezium envelope directly")
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{sink_connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            print(f"   ✅ Configuration updated!")
            
            print("\n3. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✅ Connector restart initiated")
                print("   Waiting 20 seconds...")
                time.sleep(20)
                
                # Check status
                status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    print(f"\n   Connector state: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        task_state = task.get('state', 'N/A')
                        print(f"   Task {task.get('id', 'N/A')} state: {task_state}")
                        
                        if task_state == 'FAILED':
                            trace = task.get('trace', '')
                            if trace:
                                print(f"\n   ⚠ Task Error (first 500 chars):")
                                print(f"   {trace[:500]}")
                        elif task_state == 'RUNNING':
                            print(f"\n   ✅✅✅ Connector is RUNNING!")
                            print(f"   Now processing Debezium envelope directly")
        else:
            print(f"   ❌ Config update failed: {update_r.status_code} - {update_r.text}")
    else:
        print(f"   ❌ Error: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("Note: If this doesn't work, we may need to use a different transform")
print("or configure Snowflake connector to extract operation from Debezium envelope")
print("=" * 70)


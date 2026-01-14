#!/usr/bin/env python3
"""Fix Snowflake sink connector - remove Debezium transform or use alternative."""

import requests
import time

print("=" * 70)
print("FIXING SNOWFLAKE SINK CONNECTOR TRANSFORM")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current transforms: {config.get('transforms', 'N/A')}")
        print(f"   Transform type: {config.get('transforms.unwrap.type', 'N/A')}")
        
        print("\n2. The issue: 'nothing to be flushed' suggests transform is failing")
        print("   The Snowflake connector can handle Debezium messages directly")
        print("   without the ExtractNewRecordState transform if configured correctly")
        
        print("\n3. Trying solution: Remove transform and let Snowflake handle Debezium format")
        print("   Snowflake connector can process Debezium messages in their native format")
        print("   and store them in RECORD_CONTENT/RECORD_METADATA format automatically")
        
        new_config = config.copy()
        
        # Remove transform - Snowflake connector can handle Debezium format directly
        if 'transforms' in new_config:
            del new_config['transforms']
        if 'transforms.unwrap.type' in new_config:
            del new_config['transforms.unwrap.type']
        if 'transforms.unwrap.drop.tombstones' in new_config:
            del new_config['transforms.unwrap.drop.tombstones']
        if 'transforms.unwrap.delete.handling.mode' in new_config:
            del new_config['transforms.unwrap.delete.handling.mode']
        
        # Keep value converter with schemas enabled (Debezium uses schemas)
        # This allows Snowflake to process the full Debezium envelope
        new_config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
        new_config['value.converter.schemas.enable'] = 'true'
        
        print("\n4. Updating configuration (removing transform)...")
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{sink_connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            print("   ✓ Config updated successfully!")
            print("   Transform removed - Snowflake will process Debezium messages directly")
            
            print("\n5. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✓ Connector restart initiated")
                print("   Waiting 30 seconds for connector to process messages...")
                time.sleep(30)
                
                print("\n6. Verifying connector status...")
                status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    print(f"   Connector state: {status.get('connector', {}).get('state', 'N/A')}")
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        print(f"   Task {task.get('id', 'N/A')} state: {task.get('state', 'N/A')}")
        else:
            print(f"   ✗ Config update failed: {update_r.status_code} - {update_r.text}")
    else:
        print(f"   Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NEXT: Check if messages are now being flushed to Snowflake")
print("=" * 70)


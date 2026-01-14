#!/usr/bin/env python3
"""Fix Snowflake connector configuration - ensure transforms are present."""

import requests

print("=" * 70)
print("FIXING SNOWFLAKE CONNECTOR CONFIGURATION")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Transforms: {config.get('transforms', 'N/A')}")
        print(f"   Value converter: {config.get('value.converter', 'N/A')}")
        print(f"   Schema enable: {config.get('value.converter.schemas.enable', 'N/A')}")
        
        # Check if transforms are missing
        if not config.get('transforms'):
            print(f"\n   ⚠ Transforms are missing!")
            print(f"   The Snowflake connector needs ExtractNewRecordState transform")
            print(f"   to unwrap the Debezium envelope format")
            
            print(f"\n2. Adding transforms to configuration...")
            new_config = config.copy()
            
            # Add ExtractNewRecordState transform to unwrap Debezium envelope
            new_config['transforms'] = 'unwrap'
            new_config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
            new_config['transforms.unwrap.drop.tombstones'] = 'false'
            new_config['transforms.unwrap.delete.handling.mode'] = 'none'
            
            # Ensure value converter is set correctly
            new_config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
            new_config['value.converter.schemas.enable'] = 'true'
            
            print(f"   ✅ Added transforms configuration")
            print(f"      transforms: unwrap")
            print(f"      transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState")
            
            update_r = requests.put(
                f"{kafka_connect_url}/connectors/{sink_connector_name}/config",
                json=new_config,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if update_r.status_code == 200:
                print(f"   ✅ Configuration updated successfully!")
                
                print("\n3. Restarting connector...")
                restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
                if restart_r.status_code == 204:
                    print("   ✅ Connector restart initiated")
                    print("   Waiting 20 seconds...")
                    import time
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
                                print(f"\n   ✅✅✅ Connector is RUNNING with transforms!")
            else:
                print(f"   ❌ Config update failed: {update_r.status_code} - {update_r.text}")
        else:
            print(f"\n   ✅ Transforms are present: {config.get('transforms', 'N/A')}")
            print(f"   Checking if they're correct...")
            
            unwrap_type = config.get('transforms.unwrap.type', 'N/A')
            if unwrap_type != 'io.debezium.transforms.ExtractNewRecordState':
                print(f"   ⚠ Transform type is incorrect: {unwrap_type}")
                print(f"   Should be: io.debezium.transforms.ExtractNewRecordState")
            else:
                print(f"   ✅ Transform type is correct")
    else:
        print(f"   ❌ Error: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


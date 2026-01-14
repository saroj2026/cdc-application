#!/usr/bin/env python3
"""Fix Oracle-Snowflake CDC by updating connector configuration to match working pattern."""

import requests
import time

print("=" * 70)
print("FIXING ORACLE-SNOWFLAKE CDC CONFIGURATION")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current connector configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        current_config = r.json()
        
        print(f"   Current config:")
        print(f"     Topics: {current_config.get('topics', 'N/A')}")
        print(f"     Topic2Table map: {current_config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"     Transforms: {current_config.get('transforms', 'N/A')}")
        print(f"     Value converter: {current_config.get('value.converter', 'N/A')}")
        print(f"     Schema enable: {current_config.get('value.converter.schemas.enable', 'N/A')}")
        
        print("\n2. Updating configuration with proper transforms...")
        print("-" * 70)
        
        # Update config to match the expected pattern from sink_config.py
        # The Snowflake connector should use ExtractNewRecordState transform
        # to extract 'after' field from Debezium envelope
        updated_config = current_config.copy()
        
        # Add transforms if not present
        if not updated_config.get('transforms'):
            updated_config['transforms'] = 'unwrap'
            updated_config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
            updated_config['transforms.unwrap.drop.tombstones'] = 'false'
            updated_config['transforms.unwrap.delete.handling.mode'] = 'none'
            print(f"   ✅ Added transforms configuration")
        else:
            print(f"   ℹ Transforms already present: {updated_config.get('transforms')}")
        
        # Ensure value converter is correct
        if updated_config.get('value.converter') != 'org.apache.kafka.connect.json.JsonConverter':
            updated_config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
            print(f"   ✅ Updated value converter")
        
        if updated_config.get('value.converter.schemas.enable') != 'true':
            updated_config['value.converter.schemas.enable'] = 'true'
            print(f"   ✅ Enabled schemas")
        
        # Ensure error handling is set
        if not updated_config.get('errors.tolerance'):
            updated_config['errors.tolerance'] = 'all'
            updated_config['errors.log.enable'] = 'true'
            updated_config['errors.log.include.messages'] = 'true'
            print(f"   ✅ Added error handling")
        
        print(f"\n   Updated configuration:")
        print(f"     Transforms: {updated_config.get('transforms', 'N/A')}")
        if updated_config.get('transforms'):
            print(f"     Transform type: {updated_config.get('transforms.unwrap.type', 'N/A')}")
        
        # Update connector config
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{sink_connector_name}/config",
            json=updated_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            print(f"\n   ✅ Configuration updated successfully!")
            
            print("\n3. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✅ Connector restart initiated")
                print("   Waiting 20 seconds for initialization...")
                time.sleep(20)
                
                # Check status
                status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    connector_state = status.get('connector', {}).get('state', 'N/A')
                    print(f"\n4. Connector Status:")
                    print("-" * 70)
                    print(f"   Connector state: {connector_state}")
                    
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        task_id = task.get('id', 'N/A')
                        task_state = task.get('state', 'N/A')
                        worker_id = task.get('worker_id', 'N/A')
                        print(f"   Task {task_id} state: {task_state} on {worker_id}")
                        
                        if task_state == 'FAILED':
                            trace = task.get('trace', '')
                            if trace:
                                print(f"\n   ⚠ Task Error (first 800 chars):")
                                print(f"   {trace[:800]}")
                        elif task_state == 'RUNNING':
                            print(f"\n   ✅✅✅ Connector is RUNNING!")
                            print(f"   CDC should now flow to Snowflake correctly!")
        else:
            print(f"   ❌ Config update failed: {update_r.status_code}")
            print(f"   Response: {update_r.text}")
    else:
        print(f"   ❌ Error getting config: {r.status_code}")
        print(f"   Response: {r.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Wait 60-90 seconds for buffer flush")
print("  2. Insert/update data in Oracle")
print("  3. Check Snowflake for CDC events")
print("  4. Run: python monitor_cdc_to_snowflake.py")
print("=" * 70)


#!/usr/bin/env python3
"""Delete and recreate Snowflake sink connector with correct configuration."""

import requests
import time

print("=" * 70)
print("RECREATING SNOWFLAKE SINK CONNECTOR")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Getting current configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   ✅ Current configuration retrieved")
        
        # Save the config (we'll recreate with it)
        saved_config = config.copy()
        
        print("\n2. Deleting existing connector...")
        delete_r = requests.delete(f"{kafka_connect_url}/connectors/{sink_connector_name}", timeout=10)
        if delete_r.status_code == 204:
            print(f"   ✅ Connector deleted successfully")
            print(f"   Waiting 5 seconds for cleanup...")
            time.sleep(5)
        else:
            print(f"   ⚠ Delete returned status {delete_r.status_code}")
            if delete_r.status_code == 404:
                print(f"   Connector doesn't exist, will create new one")
        
        print("\n3. Recreating connector with correct configuration...")
        print("-" * 70)
        
        # Ensure all required config is present
        new_config = {
            "connector.class": saved_config.get("connector.class"),
            "tasks.max": "1",
            "topics": saved_config.get("topics"),
            "snowflake.url.name": saved_config.get("snowflake.url.name"),
            "snowflake.user.name": saved_config.get("snowflake.user.name"),
            "snowflake.database.name": saved_config.get("snowflake.database.name"),
            "snowflake.schema.name": saved_config.get("snowflake.schema.name"),
            "snowflake.topic2table.map": saved_config.get("snowflake.topic2table.map"),
            "buffer.count.records": saved_config.get("buffer.count.records", "3000"),
            "buffer.flush.time": saved_config.get("buffer.flush.time", "60"),
            "buffer.size.bytes": saved_config.get("buffer.size.bytes", "5000000"),
            "key.converter": saved_config.get("key.converter", "org.apache.kafka.connect.storage.StringConverter"),
            "value.converter": saved_config.get("value.converter", "org.apache.kafka.connect.json.JsonConverter"),
            "value.converter.schemas.enable": saved_config.get("value.converter.schemas.enable", "true"),
            "transforms": "unwrap",
            "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
            "transforms.unwrap.drop.tombstones": "false",
            "transforms.unwrap.delete.handling.mode": "none",
            "errors.tolerance": saved_config.get("errors.tolerance", "all"),
            "errors.log.enable": saved_config.get("errors.log.enable", "true"),
            "errors.log.include.messages": saved_config.get("errors.log.include.messages", "true"),
        }
        
        # Add authentication
        if saved_config.get("snowflake.private.key"):
            new_config["snowflake.private.key"] = saved_config.get("snowflake.private.key")
        elif saved_config.get("snowflake.password"):
            new_config["snowflake.password"] = saved_config.get("snowflake.password")
        
        # Add optional fields
        if saved_config.get("snowflake.warehouse.name"):
            new_config["snowflake.warehouse.name"] = saved_config.get("snowflake.warehouse.name")
        if saved_config.get("snowflake.role.name"):
            new_config["snowflake.role.name"] = saved_config.get("snowflake.role.name")
        
        print(f"   Topics: {new_config.get('topics')}")
        print(f"   Topic2Table map: {new_config.get('snowflake.topic2table.map')}")
        print(f"   Transforms: {new_config.get('transforms')}")
        print(f"   Database: {new_config.get('snowflake.database.name')}")
        print(f"   Schema: {new_config.get('snowflake.schema.name')}")
        
        create_r = requests.post(
            f"{kafka_connect_url}/connectors",
            json={"name": sink_connector_name, "config": new_config},
            headers={'Content-Type': 'application/json'},
            timeout=15
        )
        
        if create_r.status_code in [200, 201]:
            print(f"\n   ✅ Connector created successfully!")
            print(f"   Waiting 20 seconds for initialization...")
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
                        print(f"   The connector should now process messages correctly!")
        else:
            print(f"   ❌ Connector creation failed: {create_r.status_code}")
            print(f"   Response: {create_r.text}")
    else:
        print(f"   ❌ Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("  1. Wait 60-90 seconds for buffer flush")
print("  2. Check Snowflake for CDC events")
print("  3. Run: python monitor_cdc_to_snowflake.py")
print("=" * 70)


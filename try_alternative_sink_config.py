"""Try alternative Sink connector configuration without ExtractField."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"
DEBEZIUM_CONNECTOR_NAME = "cdc-pg_to_mssql_projects_simple-pg-public"

print("="*80)
print("Trying Alternative Sink Configuration")
print("="*80)
print("\nOption: Configure Debezium to unwrap messages instead of extracting in Sink")
print("This will make Debezium send flat structure, eliminating need for ExtractField")

try:
    # Step 1: Update Debezium to unwrap
    print("\n1. Updating Debezium connector to unwrap messages...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        debezium_config = data.get('config', {})
        
        # Add unwrap transform to Debezium
        debezium_config["transforms"] = "unwrap"
        debezium_config["transforms.unwrap.type"] = "io.debezium.transforms.ExtractNewRecordState"
        debezium_config["transforms.unwrap.drop.tombstones"] = "false"
        debezium_config["transforms.unwrap.delete.handling.mode"] = "none"
        debezium_config["transforms.unwrap.add.fields"] = "op,source.ts_ms"
        
        # Update Debezium
        put_url = f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR_NAME}/config"
        response = requests.put(
            put_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(debezium_config),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("   [OK] Debezium config updated with unwrap transform")
        else:
            print(f"   [ERROR] Failed to update Debezium: {response.status_code}")
            print(f"   Response: {response.text}")
    else:
        print(f"   [ERROR] Failed to get Debezium config: {response.status_code}")
    
    # Step 2: Update Sink to remove ExtractField
    print("\n2. Updating Sink connector to remove ExtractField...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        sink_config = data.get('config', {})
        
        # Remove ExtractField transform - messages will be flat now
        sink_config.pop("transforms", None)
        sink_config.pop("transforms.extractAfter.type", None)
        sink_config.pop("transforms.extractAfter.field", None)
        sink_config.pop("transforms.extractPayload.type", None)
        sink_config.pop("transforms.extractPayload.field", None)
        
        # Update Sink
        put_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/config"
        response = requests.put(
            put_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(sink_config),
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("   [OK] Sink config updated - ExtractField removed")
        else:
            print(f"   [ERROR] Failed to update Sink: {response.status_code}")
            print(f"   Response: {response.text}")
    else:
        print(f"   [ERROR] Failed to get Sink config: {response.status_code}")
    
    # Step 3: Restart both connectors
    print("\n3. Restarting connectors...")
    
    # Restart Debezium
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    print(f"   Debezium restart: {response.status_code}")
    
    # Restart Sink
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    print(f"   Sink restart: {response.status_code}")
    
    print("\n4. Waiting 10 seconds for connectors to restart...")
    time.sleep(10)
    
    print("\n" + "="*80)
    print("Configuration Updated")
    print("="*80)
    print("\nChanges made:")
    print("  1. Debezium: Added unwrap transform (ExtractNewRecordState)")
    print("     - This will send flat structure instead of envelope")
    print("  2. Sink: Removed ExtractField transform")
    print("     - Messages are now flat, no extraction needed")
    print("\nNext steps:")
    print("  1. Make a NEW change in PostgreSQL (INSERT row 111)")
    print("  2. Wait 10-15 seconds")
    print("  3. Check if row appears in SQL Server")
    print("\nNote: This only affects NEW messages. Old messages in Kafka")
    print("      still have the envelope format and won't be processed.")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


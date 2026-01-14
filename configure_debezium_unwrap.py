"""Configure Debezium ExtractNewRecordState transform - the proper solution."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Configuring Debezium ExtractNewRecordState Transform")
print("=" * 70)

try:
    # Get current config
    print("\n1. Getting current connector configuration...")
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"   ❌ Error getting config: {response.status_code}")
        exit(1)
    
    config = response.json()
    
    # Based on documentation:
    # We need to use ExtractNewRecordState to extract 'after' field from Debezium
    # But SnowflakeJsonConverter converts before transforms run
    # So we need to use JsonConverter with the transform, then Snowflake should accept it
    
    print("\n2. Configuring ExtractNewRecordState transform...")
    print("   This will extract the 'after' field from Debezium envelope")
    
    # Remove all existing transform configs
    config.pop('transforms', None)
    for key in list(config.keys()):
        if key.startswith('transforms.'):
            config.pop(key, None)
    
    # Use JsonConverter so transforms can work
    config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
    config['value.converter.schemas.enable'] = 'true'
    
    # Add Debezium ExtractNewRecordState transform
    config['transforms'] = 'unwrap'
    config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
    config['transforms.unwrap.drop.tombstones'] = 'false'
    config['transforms.unwrap.delete.handling.mode'] = 'none'
    
    print("   ✅ Configured JsonConverter with ExtractNewRecordState")
    print("   Note: This extracts 'after' field, making it compatible with Snowflake")
    
    # Update config
    print("\n3. Updating connector configuration...")
    update_response = requests.put(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        json=config,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if update_response.status_code in [200, 201]:
        print("   ✅ Configuration updated")
    else:
        print(f"   ❌ Error: {update_response.status_code}")
        print(f"   Response: {update_response.text[:500]}")
        
        # Check if Debezium transform library is available
        if "ExtractNewRecordState" in update_response.text or "debezium" in update_response.text.lower():
            print("\n   ⚠️  Debezium transform library may not be installed")
            print("   The transform 'io.debezium.transforms.ExtractNewRecordState' is required")
            print("   It should be available if Debezium is installed in Kafka Connect")
            exit(1)
        else:
            exit(1)
    
    # Restart connector
    print("\n4. Restarting connector...")
    restart_response = requests.post(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart",
        timeout=10
    )
    
    if restart_response.status_code == 204:
        print("   ✅ Connector restarted")
    else:
        print(f"   ⚠️  Restart response: {restart_response.status_code}")
    
    print("\n" + "=" * 70)
    print("✅ Configuration Updated!")
    print("=" * 70)
    print("\nThe connector is now configured with:")
    print("  - JsonConverter (so transforms work)")
    print("  - ExtractNewRecordState transform (extracts 'after' field)")
    print("\nNote: Snowflake connector should accept JsonConverter format.")
    print("If it doesn't, we may need to use SnowflakeJsonConverter with a different approach.")
    print("\nWait a bit and check connector status:")
    print("  python check_sink_connector_status.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


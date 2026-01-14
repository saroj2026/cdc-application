"""Use Debezium unwrap transform - the proper solution."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Using Debezium Unwrap Transform")
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
    
    # Remove all existing transform configs
    config.pop('transforms', None)
    for key in list(config.keys()):
        if key.startswith('transforms.'):
            config.pop(key, None)
    
    # Use JsonConverter (required for Debezium unwrap)
    config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
    config['value.converter.schemas.enable'] = 'true'
    
    # Add Debezium unwrap transform
    config['transforms'] = 'unwrap'
    config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
    config['transforms.unwrap.drop.tombstones'] = 'false'
    config['transforms.unwrap.delete.handling.mode'] = 'none'
    
    print("\n2. Configuring Debezium unwrap transform...")
    print("   ✅ This is the proper way to extract data from Debezium envelope")
    print("   - Extracts 'after' field automatically")
    print("   - Handles CREATE, UPDATE, DELETE operations")
    print("   - Works with JsonConverter")
    
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
        
        # If Debezium transform not available, we need to install it
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
    print("\nThe connector is now using Debezium's unwrap transform.")
    print("This should properly extract the 'after' field from Debezium envelope.")
    print("\nWait a bit and verify data flow:")
    print("  python verify_cdc_to_snowflake.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


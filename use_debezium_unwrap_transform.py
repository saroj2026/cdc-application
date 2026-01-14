"""Use Debezium unwrap transform for Snowflake connector."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Using Debezium Unwrap Transform for Snowflake Connector")
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
    print("   ✅ Config retrieved")
    
    # Add Debezium unwrap transform
    print("\n2. Adding Debezium unwrap transform...")
    
    # Remove any existing transforms
    config.pop('transforms', None)
    config.pop('transforms.extractPayload.type', None)
    config.pop('transforms.extractPayload.field', None)
    config.pop('transforms.extractAfter.type', None)
    config.pop('transforms.extractAfter.field', None)
    
    # Add Debezium unwrap transform
    config['transforms'] = 'unwrap'
    config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
    config['transforms.unwrap.drop.tombstones'] = 'false'
    config['transforms.unwrap.delete.handling.mode'] = 'none'
    config['transforms.unwrap.add.fields'] = 'op'
    
    print("   ✅ Debezium unwrap transform added")
    print("   - Extracts 'after' field from Debezium envelope")
    print("   - Handles CREATE, UPDATE, DELETE operations")
    print("   - Preserves operation type in 'op' field")
    
    # Update connector config
    print("\n3. Updating connector configuration...")
    update_response = requests.put(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        json=config,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if update_response.status_code in [200, 201]:
        print("   ✅ Configuration updated successfully")
    else:
        print(f"   ❌ Error updating config: {update_response.status_code}")
        print(f"   Response: {update_response.text[:500]}")
        
        # If Debezium transform not available, try ExtractField approach
        if "ExtractNewRecordState" in update_response.text or "debezium" in update_response.text.lower():
            print("\n   ⚠️  Debezium transform library may not be available")
            print("   Trying ExtractField approach with nested field extraction...")
            
            # Try ExtractField with nested path
            config['transforms'] = 'unwrap'
            config['transforms.unwrap.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
            config['transforms.unwrap.field'] = 'payload.after'
            config.pop('transforms.unwrap.drop.tombstones', None)
            config.pop('transforms.unwrap.delete.handling.mode', None)
            config.pop('transforms.unwrap.add.fields', None)
            
            update_response2 = requests.put(
                f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
                json=config,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if update_response2.status_code in [200, 201]:
                print("   ✅ Configuration updated with ExtractField approach")
            else:
                print(f"   ❌ Still failed: {update_response2.status_code}")
                print(f"   Response: {update_response2.text[:500]}")
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
    print("✅ Transform configured!")
    print("=" * 70)
    print("\nThe connector should now extract data from Debezium envelope.")
    print("Wait a few seconds and check the connector status:")
    print("  python check_sink_connector_status.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


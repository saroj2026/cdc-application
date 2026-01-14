"""Fix Snowflake connector with ExtractField for payload.after."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Fixing Snowflake Connector with ExtractField")
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
    
    # Use simple ExtractField for payload.after
    print("\n2. Configuring ExtractField transform...")
    
    # Clear existing transforms
    config.pop('transforms', None)
    for key in list(config.keys()):
        if key.startswith('transforms.'):
            config.pop(key, None)
    
    # Add single ExtractField transform
    config['transforms'] = 'extractAfter'
    config['transforms.extractAfter.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractAfter.field'] = 'payload.after'
    
    print("   ✅ ExtractField transform configured")
    print("   - Field: payload.after")
    print("   - This extracts the 'after' field from Debezium envelope")
    
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
        
        # If payload.after doesn't work, try nested extraction
        print("\n   ⚠️  Trying nested field extraction...")
        config['transforms'] = 'extractPayload,extractAfter'
        config['transforms.extractPayload.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
        config['transforms.extractPayload.field'] = 'payload'
        config['transforms.extractAfter.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
        config['transforms.extractAfter.field'] = 'after'
        
        update_response2 = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            json=config,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if update_response2.status_code in [200, 201]:
            print("   ✅ Configuration updated with nested extraction")
        else:
            print(f"   ❌ Still failed: {update_response2.status_code}")
            print(f"   Response: {update_response2.text[:500]}")
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
    print("✅ Connector configured!")
    print("=" * 70)
    print("\nWait a few seconds and check the connector status:")
    print("  python check_sink_connector_status.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


"""Use JsonConverter with transforms, configure Snowflake to accept JSON."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Using JsonConverter with Transforms")
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
    
    # Use JsonConverter so transforms work, then configure Snowflake
    print("\n2. Configuring JsonConverter with transforms...")
    
    config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
    config['value.converter.schemas.enable'] = 'true'
    
    # Add transforms to extract 'after' field
    config['transforms'] = 'extractPayload,extractAfter'
    config['transforms.extractPayload.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractPayload.field'] = 'payload'
    config['transforms.extractAfter.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractAfter.field'] = 'after'
    
    # Note: Snowflake connector might not work with JsonConverter
    # But let's try it - the connector might accept JSON format
    
    print("   ✅ Configured JsonConverter with transforms")
    print("   This will extract payload.after from Debezium envelope")
    
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
        
        # If Snowflake connector doesn't accept JsonConverter, we need a different approach
        # The connector might require SnowflakeJsonConverter
        
        print("\n   ⚠️  Snowflake connector might require SnowflakeJsonConverter")
        print("   Alternative: Use a different sink approach or custom solution")
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
    print("✅ Configuration Updated")
    print("=" * 70)
    print("\nNote: If Snowflake connector doesn't accept JsonConverter,")
    print("we may need to use a different approach or check Snowflake connector documentation.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


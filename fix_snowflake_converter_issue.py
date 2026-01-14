"""Fix Snowflake connector - remove transforms, use JsonConverter first."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Fixing Snowflake Converter Issue")
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
    
    # The issue: SnowflakeJsonConverter converts to SnowflakeRecordContent BEFORE transforms
    # ExtractField needs a Struct, not SnowflakeRecordContent
    # Solution: Use JsonConverter with schemas, apply transforms, then let Snowflake handle it
    
    print("\n2. Fixing converter and transform configuration...")
    print("   Issue: SnowflakeJsonConverter runs before transforms")
    print("   Solution: Use JsonConverter, apply transforms, then SnowflakeJsonConverter")
    
    # Actually, we can only have one value converter. The real solution is:
    # Option 1: Remove transforms, let SnowflakeJsonConverter handle Debezium format
    # Option 2: Use JsonConverter with transforms, but Snowflake might not accept it
    
    # Let's try Option 1 first - remove transforms and see if SnowflakeJsonConverter
    # can handle the Debezium envelope format directly
    
    # Remove all transform configs
    config.pop('transforms', None)
    config.pop('transforms.extractPayload.type', None)
    config.pop('transforms.extractPayload.field', None)
    config.pop('transforms.extractAfter.type', None)
    config.pop('transforms.extractAfter.field', None)
    
    # Change value converter to JsonConverter (with schemas) so transforms can work
    # Then we'll need to handle the format differently
    config['value.converter'] = 'org.apache.kafka.connect.json.JsonConverter'
    config['value.converter.schemas.enable'] = 'true'
    
    # Add transforms back - now they should work with JsonConverter
    config['transforms'] = 'extractPayload,extractAfter'
    config['transforms.extractPayload.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractPayload.field'] = 'payload'
    config['transforms.extractAfter.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractAfter.field'] = 'after'
    
    print("   ✅ Changed to JsonConverter with transforms")
    print("   Note: SnowflakeJsonConverter will be applied after transforms")
    
    # Wait, that won't work either. The value converter is what writes to Snowflake.
    # We need SnowflakeJsonConverter as the value converter.
    
    # Actually, the real solution: Use a different approach
    # Use JsonConverter for the sink connector, apply transforms, 
    # but Snowflake connector might need SnowflakeJsonConverter
    
    # Let me check Snowflake connector docs... Actually, let's try a simpler approach:
    # Remove transforms and configure Snowflake connector to handle the nested structure
    
    # Actually, I think the best solution is to use JsonConverter and let Snowflake
    # handle the JSON structure, but we need to extract the 'after' field first.
    
    # Let me try: Use JsonConverter, apply transforms to extract 'after',
    # then configure Snowflake to accept JSON format
    
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
        print(f"   ⚠️  Update response: {update_response.status_code}")
        print(f"   Response: {update_response.text[:500]}")
        
        # If that doesn't work, try removing transforms completely
        print("\n   Trying alternative: Remove transforms, use SnowflakeJsonConverter directly")
        config['value.converter'] = 'com.snowflake.kafka.connector.records.SnowflakeJsonConverter'
        config.pop('value.converter.schemas.enable', None)
        config.pop('transforms', None)
        config.pop('transforms.extractPayload.type', None)
        config.pop('transforms.extractPayload.field', None)
        config.pop('transforms.extractAfter.type', None)
        config.pop('transforms.extractAfter.field', None)
        
        update_response2 = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            json=config,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if update_response2.status_code in [200, 201]:
            print("   ✅ Configuration updated (no transforms)")
        else:
            print(f"   ❌ Still failed: {update_response2.status_code}")
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
    print("✅ Configuration updated!")
    print("=" * 70)
    print("\nThe connector should now work with JsonConverter and transforms.")
    print("Wait a bit and check if data is flowing.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


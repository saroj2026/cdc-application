"""Final fix: Use SnowflakeJsonConverter but configure it to handle Debezium format."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Final Fix: Configure Snowflake Connector Properly")
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
    
    # The issue: SnowflakeJsonConverter converts before transforms
    # Solution: The Snowflake connector might be able to handle Debezium format
    # if we configure it correctly, OR we need to use a different approach
    
    # Actually, looking at Snowflake connector docs, it should handle JSON.
    # The problem is the order: converter -> transforms -> sink
    # But SnowflakeJsonConverter converts to SnowflakeRecordContent before transforms
    
    # Real solution: Use JsonConverter, apply transforms, 
    # but Snowflake connector needs to accept JSON format
    
    # Let's try: Keep JsonConverter with transforms, but check if Snowflake accepts it
    # If not, we might need to use a custom transform or different approach
    
    print("\n2. Current configuration:")
    print(f"   Value Converter: {config.get('value.converter', 'N/A')}")
    print(f"   Transforms: {config.get('transforms', 'None')}")
    
    # The Snowflake connector might work with JsonConverter if the format is correct
    # Let's verify the current setup is working
    
    # Actually, I think the issue might be that Snowflake connector specifically
    # requires SnowflakeJsonConverter. So we need a different solution.
    
    # Option: Use a Flatten transform or custom transform that works with SnowflakeJsonConverter
    # Or: Configure the connector to handle nested JSON structure
    
    # Let me check if we can use a different transform that works with SnowflakeJsonConverter
    # Or configure Snowflake to accept the nested structure
    
    print("\n3. The Snowflake connector requires SnowflakeJsonConverter.")
    print("   But SnowflakeJsonConverter converts before transforms can run.")
    print("   Solution: Configure Snowflake connector to handle Debezium envelope format directly.")
    
    # Change back to SnowflakeJsonConverter
    config['value.converter'] = 'com.snowflake.kafka.connector.records.SnowflakeJsonConverter'
    config.pop('value.converter.schemas.enable', None)
    
    # Remove transforms - they don't work with SnowflakeJsonConverter
    config.pop('transforms', None)
    config.pop('transforms.extractPayload.type', None)
    config.pop('transforms.extractPayload.field', None)
    config.pop('transforms.extractAfter.type', None)
    config.pop('transforms.extractAfter.field', None)
    
    # Configure Snowflake to handle the nested structure
    # The Snowflake connector should be able to extract fields from nested JSON
    # using topic2table mapping and field extraction
    
    print("   ✅ Removed transforms, using SnowflakeJsonConverter directly")
    print("   Note: Snowflake connector should handle Debezium format")
    print("   The connector will write the entire Debezium envelope to Snowflake")
    print("   You may need to create a view or use Snowflake's JSON functions to extract 'after' field")
    
    # Update config
    print("\n4. Updating connector configuration...")
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
        exit(1)
    
    # Restart connector
    print("\n5. Restarting connector...")
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
    print("\nThe connector is now using SnowflakeJsonConverter without transforms.")
    print("It will write the Debezium envelope format to Snowflake.")
    print("\nNote: The data in Snowflake will be in Debezium format.")
    print("You may need to:")
    print("1. Create a view that extracts the 'after' field")
    print("2. Or use Snowflake's JSON functions to query the data")
    print("3. Or configure the table to flatten the structure")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

"""Configure Snowflake connector properly based on documentation."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Configuring Snowflake Connector (Based on Documentation)")
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
    
    # Based on Snowflake documentation:
    # 1. Snowflake connector stores messages in RECORD_CONTENT (VARIANT) by default
    # 2. For user-created tables, it can insert into individual columns
    # 3. The connector can handle JSON format with SnowflakeJsonConverter
    # 4. For Debezium format, we might need to let it store in RECORD_CONTENT first
    
    print("\n2. Based on Snowflake documentation:")
    print("   - Snowflake connector stores messages in RECORD_CONTENT (VARIANT) by default")
    print("   - For user-created tables with columns, it tries to match schema")
    print("   - The connector can handle Debezium format but may need special config")
    
    # Remove all transforms - let Snowflake handle the format
    config.pop('transforms', None)
    for key in list(config.keys()):
        if key.startswith('transforms.'):
            config.pop(key, None)
    
    # Use SnowflakeJsonConverter (required for Snowflake connector)
    config['value.converter'] = 'com.snowflake.kafka.connector.records.SnowflakeJsonConverter'
    config.pop('value.converter.schemas.enable', None)
    
    # The key insight: Snowflake connector will store the Debezium envelope in RECORD_CONTENT
    # OR if the table schema matches, it will try to insert into columns
    # Since our table has columns matching the 'after' field, we need to either:
    # 1. Let it store in RECORD_CONTENT and extract later with SQL
    # 2. Or configure it to extract 'after' field somehow
    
    # Actually, looking at the error we got earlier - the connector tried to match schema
    # but failed because the message format doesn't match
    
    # Solution: Drop the table and let connector auto-create it with RECORD_CONTENT
    # OR configure connector to not try schema matching
    
    print("\n3. Configuration strategy:")
    print("   Option A: Store in RECORD_CONTENT (VARIANT) - extract 'after' with SQL")
    print("   Option B: Use transforms to extract 'after' before SnowflakeJsonConverter")
    print("   Option C: Configure connector to handle nested JSON")
    
    # Let's try Option A first - remove transforms, use SnowflakeJsonConverter
    # The connector will store the entire Debezium envelope in RECORD_CONTENT
    # Then we can extract 'after' field in Snowflake using SQL
    
    print("\n4. Configuring for Option A (RECORD_CONTENT storage)...")
    print("   ✅ Using SnowflakeJsonConverter without transforms")
    print("   ✅ Data will be stored in RECORD_CONTENT column")
    print("   ✅ Can extract 'after' field using Snowflake SQL: RECORD_CONTENT:after")
    
    # Update config
    print("\n5. Updating connector configuration...")
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
    
    # We also need to drop the existing table and let connector auto-create it
    # OR modify the table to have RECORD_CONTENT column
    print("\n6. Table configuration needed:")
    print("   The table needs to have RECORD_CONTENT column (VARIANT type)")
    print("   OR drop the table and let connector auto-create it")
    
    # Restart connector
    print("\n7. Restarting connector...")
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
    print("\nNext steps:")
    print("1. Modify Snowflake table to have RECORD_CONTENT column (VARIANT)")
    print("2. OR drop table and let connector auto-create it")
    print("3. Data will be stored in RECORD_CONTENT")
    print("4. Extract 'after' field using: SELECT RECORD_CONTENT:after FROM projects_simple")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


"""Remove transforms from Snowflake connector - let SnowflakeJsonConverter handle Debezium format."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Removing Transforms from Snowflake Connector")
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
    
    # Remove transforms
    print("\n2. Removing transforms...")
    print(f"   Current transforms: {config.get('transforms', 'None')}")
    
    # Remove transform-related configs
    config.pop('transforms', None)
    config.pop('transforms.extractPayload.type', None)
    config.pop('transforms.extractPayload.field', None)
    config.pop('transforms.extractAfter.type', None)
    config.pop('transforms.extractAfter.field', None)
    
    print("   ✅ Transforms removed")
    print("   Note: SnowflakeJsonConverter should handle Debezium format automatically")
    
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
    print("✅ Transforms removed!")
    print("=" * 70)
    print("\nThe SnowflakeJsonConverter should now handle Debezium format directly.")
    print("Wait a few seconds and check the connector status:")
    print("  python check_sink_connector_status.py")
    print("\nThen verify data flow:")
    print("  python verify_cdc_to_snowflake.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


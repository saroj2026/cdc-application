"""Update Snowflake connector to add transforms for Debezium format."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Updating Snowflake Connector with Transforms")
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
    
    # Add transforms to extract 'after' field from Debezium envelope
    print("\n2. Adding transforms for Debezium format...")
    
    # The Snowflake connector needs to extract the actual data from Debezium's envelope
    # Debezium format: {schema: {...}, payload: {before: {...}, after: {...}, op: "c/u/d"}}
    # We need to extract payload.after
    
    config['transforms'] = 'extractPayload,extractAfter'
    config['transforms.extractPayload.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractPayload.field'] = 'payload'
    config['transforms.extractAfter.type'] = 'org.apache.kafka.connect.transforms.ExtractField$Value'
    config['transforms.extractAfter.field'] = 'after'
    
    print("   ✅ Transforms added:")
    print("      - extractPayload: Extract 'payload' field")
    print("      - extractAfter: Extract 'after' field from payload")
    
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
    print("✅ Connector updated with transforms!")
    print("=" * 70)
    print("\nThe connector will now extract the 'after' field from Debezium messages.")
    print("Wait a few seconds and check the status:")
    print("  python check_sink_connector_status.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


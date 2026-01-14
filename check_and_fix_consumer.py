"""Check and fix consumer group - ensure connector is actually consuming."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Checking and Fixing Consumer Group")
print("=" * 70)

try:
    # Get connector config
    print("\n1. Getting connector configuration...")
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        timeout=10
    )
    
    if config_response.status_code != 200:
        print(f"   ❌ Error: {config_response.status_code}")
        exit(1)
    
    config = config_response.json()
    
    # Check if consumer group is explicitly configured
    consumer_group = config.get('consumer.group.id', 'N/A')
    print(f"   Consumer Group ID: {consumer_group}")
    
    # The issue might be that the connector needs explicit consumer group config
    # Or it might be consuming from the end of the topic (no messages)
    
    # Add explicit consumer group configuration
    print("\n2. Adding explicit consumer group configuration...")
    
    # Set consumer group explicitly
    config['consumer.group.id'] = f"connect-{CONNECTOR_NAME}"
    
    # Also ensure auto.offset.reset is set to earliest (to consume from beginning)
    # But this might not be available in sink connectors - they usually consume from committed offsets
    
    # Actually, for sink connectors, the issue might be that:
    # 1. The connector is consuming from the end of the topic (no new messages)
    # 2. The connector needs to be reset to consume from beginning
    # 3. Or there's an issue with the topic subscription
    
    # Let's try adding consumer group config and see if that helps
    print(f"   Setting consumer.group.id: connect-{CONNECTOR_NAME}")
    
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
        print(f"   ⚠️  Update response: {update_response.status_code}")
        print(f"   Response: {update_response.text[:300]}")
    
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
    print("Configuration Updated")
    print("=" * 70)
    print("\nNote: The consumer group should now be explicitly set.")
    print("However, sink connectors typically consume from committed offsets.")
    print("\nIf the consumer group is still DEAD, the issue might be:")
    print("1. The connector task isn't actually running (despite showing RUNNING)")
    print("2. There's a Kafka Connect worker issue")
    print("3. The topic subscription isn't working")
    print("\nCheck the consumer group status again after a few seconds.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


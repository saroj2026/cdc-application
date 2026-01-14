#!/usr/bin/env python3
"""Fix sink connector topic name to use uppercase (Oracle format)."""

import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"

print("=" * 70)
print("FIXING SINK CONNECTOR TOPIC NAME")
print("=" * 70)

# Get current config
print("\n1. Getting current sink connector config...")
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
current_config = r.json()
print(f"   Current topics: {current_config.get('topics')}")

# Update config with correct topic name (uppercase)
print("\n2. Updating config with correct topic name...")
current_config['topics'] = 'oracle_sf_p.CDC_USER.TEST'  # Uppercase to match Oracle
print(f"   New topics: {current_config.get('topics')}")

# Update the connector config
print("\n3. Updating connector config...")
r = requests.put(
    f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config",
    json=current_config,
    headers={"Content-Type": "application/json"}
)

if r.status_code == 200:
    print("   ✓ Connector config updated successfully!")
    
    # Restart the connector
    print("\n4. Restarting connector...")
    r = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/restart")
    if r.status_code in [200, 204]:
        print("   ✓ Connector restarted successfully!")
    else:
        print(f"   ⚠ Restart response: {r.status_code}")
    
    # Wait a bit
    import time
    print("\n5. Waiting 5 seconds...")
    time.sleep(5)
    
    # Check status
    print("\n6. Checking connector status...")
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/status")
    status = r.json()
    print(f"   State: {status.get('connector', {}).get('state')}")
    tasks = status.get('tasks', [])
    for task in tasks:
        print(f"   Task {task.get('id')}: {task.get('state')}")
    
    # Verify config
    print("\n7. Verifying updated config...")
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
    updated_config = r.json()
    print(f"   Topics: {updated_config.get('topics')}")
    
    if updated_config.get('topics') == 'oracle_sf_p.CDC_USER.TEST':
        print("\n✓✓✓ SUCCESS: Sink connector topic name fixed!")
    else:
        print("\n⚠ Config might not have been updated correctly")
else:
    print(f"\n❌ Failed to update config: {r.status_code}")
    print(f"   Response: {r.text}")

print("\n" + "=" * 70)


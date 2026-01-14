"""Update Sink connector configuration with improved transform chain."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"

print("="*80)
print("Updating Sink Connector Configuration")
print("="*80)

try:
    # Step 1: Get current config
    print("\n1. Getting current configuration...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        print("   [OK] Got current config")
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        exit(1)
    
    # Step 2: Update transforms - try simpler approach first
    print("\n2. Updating transform configuration...")
    print("   Current transforms: ", config.get('transforms', 'NOT SET'))
    
    # Try alternative: Use ExtractField without Flatten first
    # If that doesn't work, the issue might be with the message structure
    # Alternative approach: Remove transforms and see if JDBC can handle envelope directly
    # But JDBC Sink needs flat structure, so we need ExtractField
    
    # Update config - try with just ExtractField but ensure it's configured correctly
    updated_config = config.copy()
    
    # Keep the ExtractField transform but ensure it's correct
    # The issue might be that 'after' is nested in 'payload.after' not just 'after'
    # Let's try both approaches
    
    print("\n   Option 1: Try extracting from payload.after")
    updated_config["transforms"] = "extractAfter"
    updated_config["transforms.extractAfter.type"] = "org.apache.kafka.connect.transforms.ExtractField$Value"
    updated_config["transforms.extractAfter.field"] = "payload.after"  # Try payload.after instead of just after
    
    # Step 3: Update connector
    print("\n3. Updating connector configuration...")
    put_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/config"
    response = requests.put(
        put_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(updated_config),
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print("   [OK] Configuration updated")
        result = response.json()
        print(f"   Updated config keys: {len(result.get('config', {}))}")
    else:
        print(f"   [ERROR] Failed to update: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
    
    # Step 4: Restart connector
    print("\n4. Restarting connector...")
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    
    if response.status_code == 204:
        print("   [OK] Restart command sent")
    else:
        print(f"   [WARN] Restart response: {response.status_code}")
    
    print("\n" + "="*80)
    print("Configuration Updated")
    print("="*80)
    print("\nChanged transform field from 'after' to 'payload.after'")
    print("This assumes Debezium messages have structure: {payload: {after: {...}}}")
    print("\nWait 10-15 seconds, then check if row 110 appears in SQL Server")
    print("If it still doesn't work, the message format might be different.")
    print("Check the actual Kafka message format to see the exact structure.")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


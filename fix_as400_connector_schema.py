#!/usr/bin/env python3
"""Fix AS400 connector schema configuration."""

import requests
import json

KAFKA_CONNECT = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-as400-s3_p-as400-segmetriq1"

def get_connector_config():
    """Get current connector configuration."""
    response = requests.get(f"{KAFKA_CONNECT}/connectors/{CONNECTOR_NAME}/config")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get config: {response.status_code}")
        return None

def update_connector_config(config):
    """Update connector configuration with schema."""
    # Ensure database.schema is set
    if 'database.schema' not in config or not config.get('database.schema'):
        config['database.schema'] = config.get('database.dbname', 'SEGMETRIQ1')
        print(f"✅ Added database.schema: {config['database.schema']}")
    
    # Also ensure snapshot.mode is set correctly
    if config.get('snapshot.mode') == 'never':
        config['snapshot.mode'] = 'initial'
        print(f"✅ Changed snapshot.mode to 'initial'")
    
    # Update the connector
    response = requests.put(
        f"{KAFKA_CONNECT}/connectors/{CONNECTOR_NAME}/config",
        json=config,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✅ Connector configuration updated successfully")
        return True
    else:
        print(f"❌ Failed to update config: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def restart_connector():
    """Restart the connector."""
    response = requests.post(f"{KAFKA_CONNECT}/connectors/{CONNECTOR_NAME}/restart")
    if response.status_code == 204:
        print(f"✅ Connector restart requested")
        return True
    else:
        print(f"⚠️  Restart response: {response.status_code}")
        return False

def main():
    print("=" * 80)
    print("  FIXING AS400 CONNECTOR SCHEMA CONFIGURATION")
    print("=" * 80)
    
    # Get current config
    print("\n1. Getting current connector configuration...")
    config = get_connector_config()
    if not config:
        return
    
    print(f"   Current database.schema: {config.get('database.schema', 'NOT SET')}")
    print(f"   Current snapshot.mode: {config.get('snapshot.mode', 'NOT SET')}")
    
    # Update config
    print("\n2. Updating connector configuration...")
    if update_connector_config(config):
        # Restart connector
        print("\n3. Restarting connector...")
        restart_connector()
        
        print("\n" + "=" * 80)
        print("  ✅ CONFIGURATION UPDATED")
        print("=" * 80)
        print("\nThe connector will restart automatically. Check status in a few seconds.")
    else:
        print("\n" + "=" * 80)
        print("  ❌ FAILED TO UPDATE CONFIGURATION")
        print("=" * 80)

if __name__ == "__main__":
    main()


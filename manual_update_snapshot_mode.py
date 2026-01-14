"""Manually update Debezium connector to use 'never' snapshot mode."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Manually Updating Debezium Connector Snapshot Mode")
print("=" * 80)

connector_name = "cdc-final_test-pg-public"

# Get current config
print(f"\n1. Getting current configuration...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
    if response.status_code == 200:
        config = response.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode')}")
        
        # Update snapshot mode to 'never'
        config['snapshot.mode'] = 'never'
        
        print(f"\n2. Updating configuration with snapshot.mode='never'...")
        update_response = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
            json=config,
            timeout=30
        )
        
        if update_response.status_code in [200, 201]:
            print(f"   [OK] Configuration updated")
            
            # Verify
            print(f"\n3. Verifying update...")
            verify_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
            if verify_response.status_code == 200:
                new_config = verify_response.json()
                print(f"   New snapshot.mode: {new_config.get('snapshot.mode')}")
                
                if new_config.get('snapshot.mode') == 'never':
                    print(f"   ✅ Snapshot mode updated successfully!")
                else:
                    print(f"   ⚠️  Snapshot mode is {new_config.get('snapshot.mode')}, expected 'never'")
        else:
            print(f"   [ERROR] Failed to update: {update_response.status_code}")
            print(f"   Response: {update_response.text[:300]}")
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Update Complete!")
print("=" * 80)
print("\nNote: The connector will restart automatically with the new configuration.")
print("Wait a few seconds, then test CDC again.")


import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Manually Updating Debezium Connector Snapshot Mode")
print("=" * 80)

connector_name = "cdc-final_test-pg-public"

# Get current config
print(f"\n1. Getting current configuration...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
    if response.status_code == 200:
        config = response.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode')}")
        
        # Update snapshot mode to 'never'
        config['snapshot.mode'] = 'never'
        
        print(f"\n2. Updating configuration with snapshot.mode='never'...")
        update_response = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
            json=config,
            timeout=30
        )
        
        if update_response.status_code in [200, 201]:
            print(f"   [OK] Configuration updated")
            
            # Verify
            print(f"\n3. Verifying update...")
            verify_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config", timeout=10)
            if verify_response.status_code == 200:
                new_config = verify_response.json()
                print(f"   New snapshot.mode: {new_config.get('snapshot.mode')}")
                
                if new_config.get('snapshot.mode') == 'never':
                    print(f"   ✅ Snapshot mode updated successfully!")
                else:
                    print(f"   ⚠️  Snapshot mode is {new_config.get('snapshot.mode')}, expected 'never'")
        else:
            print(f"   [ERROR] Failed to update: {update_response.status_code}")
            print(f"   Response: {update_response.text[:300]}")
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Update Complete!")
print("=" * 80)
print("\nNote: The connector will restart automatically with the new configuration.")
print("Wait a few seconds, then test CDC again.")


import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
OLD_CONNECTOR = "cdc-oracle_sf_p-ora-c_cdc_user"  # Old connector with old schema

print(f"=== DELETING OLD CONNECTOR ===")
print(f"Connector: {OLD_CONNECTOR}")

try:
    # First, stop the connector
    print("Stopping connector...")
    r = requests.put(f"{KAFKA_CONNECT_URL}/connectors/{OLD_CONNECTOR}/stop")
    if r.status_code == 200:
        print("✓ Connector stopped")
    else:
        print(f"Note: {r.status_code} - {r.text[:200]}")
    
    import time
    time.sleep(2)
    
    # Delete the connector
    print("Deleting connector...")
    r2 = requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{OLD_CONNECTOR}")
    if r2.status_code == 204:
        print(f"✓ Successfully deleted connector: {OLD_CONNECTOR}")
    else:
        print(f"✗ Failed to delete: {r2.status_code} - {r2.text[:200]}")
        
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:
        print(f"✓ Connector {OLD_CONNECTOR} doesn't exist (already deleted)")
    else:
        print(f"✗ Error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")


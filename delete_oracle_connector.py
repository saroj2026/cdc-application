import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-c##cdc_user"

print(f"=== DELETING CONNECTOR: {CONNECTOR_NAME} ===")

# Try URL encoding the connector name
from urllib.parse import quote
encoded_name = quote(CONNECTOR_NAME, safe='')
print(f"Encoded name: {encoded_name}")

try:
    # Try with encoded name
    r = requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{encoded_name}")
    print(f"Delete status (encoded): {r.status_code}")
    if r.status_code == 200:
        print("✓ Connector deleted successfully!")
    elif r.status_code == 404:
        print("Connector not found (may already be deleted)")
    else:
        print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"Error with encoded name: {e}")

# Also try without encoding (in case Kafka Connect handles it)
try:
    r2 = requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}")
    print(f"\nDelete status (raw): {r2.status_code}")
    if r2.status_code == 200:
        print("✓ Connector deleted successfully!")
    elif r2.status_code == 404:
        print("Connector not found (may already be deleted)")
    else:
        print(f"Response: {r2.text[:200]}")
except Exception as e:
    print(f"Error with raw name: {e}")

# Verify deletion
print(f"\n=== VERIFYING DELETION ===")
r3 = requests.get(f"{KAFKA_CONNECT_URL}/connectors")
connectors = r3.json()
oracle_conns = [c for c in connectors if 'oracle' in c.lower() and 'oracle_sf_p' in c.lower()]
if CONNECTOR_NAME in oracle_conns:
    print(f"✗ Connector still exists: {oracle_conns}")
else:
    print(f"✓ Connector deleted - not found in list")
    print(f"Remaining Oracle connectors: {oracle_conns}")


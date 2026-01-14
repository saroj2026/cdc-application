"""Restart connectors to pick up configuration changes."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Restarting Connectors")
print("=" * 80)

connectors = [
    "cdc-final_test-pg-public",
    "sink-final_test-mssql-dbo"
]

for conn_name in connectors:
    print(f"\nRestarting {conn_name}...")
    try:
        # Restart connector
        response = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/restart", timeout=10)
        if response.status_code in [200, 204, 409]:  # 409 = already restarting
            print(f"   [OK] Restart initiated")
        else:
            print(f"   [WARNING] Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] Exception: {e}")

print("\nWaiting 15 seconds for connectors to restart...")
time.sleep(15)

# Verify status
print("\nChecking connector status...")
for conn_name in connectors:
    try:
        status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if status_response.status_code == 200:
            status = status_response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   {conn_name}: {connector_state}")
    except Exception as e:
        print(f"   {conn_name}: Error checking status - {e}")

print("\n" + "=" * 80)
print("Connectors restarted!")
print("=" * 80)


import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Restarting Connectors")
print("=" * 80)

connectors = [
    "cdc-final_test-pg-public",
    "sink-final_test-mssql-dbo"
]

for conn_name in connectors:
    print(f"\nRestarting {conn_name}...")
    try:
        # Restart connector
        response = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/restart", timeout=10)
        if response.status_code in [200, 204, 409]:  # 409 = already restarting
            print(f"   [OK] Restart initiated")
        else:
            print(f"   [WARNING] Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   [ERROR] Exception: {e}")

print("\nWaiting 15 seconds for connectors to restart...")
time.sleep(15)

# Verify status
print("\nChecking connector status...")
for conn_name in connectors:
    try:
        status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if status_response.status_code == 200:
            status = status_response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   {conn_name}: {connector_state}")
    except Exception as e:
        print(f"   {conn_name}: Error checking status - {e}")

print("\n" + "=" * 80)
print("Connectors restarted!")
print("=" * 80)


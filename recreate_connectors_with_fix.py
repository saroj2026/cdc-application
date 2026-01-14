"""Recreate connectors with correct snapshot mode for CDC."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Recreating Connectors with Correct Configuration")
print("=" * 80)

# Step 1: Stop the pipeline
print("\n1. Stopping pipeline...")
pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
    if response.status_code in [200, 404]:
        print("   [OK] Pipeline stopped")
    else:
        print(f"   [WARNING] Status: {response.status_code}")
except Exception as e:
    print(f"   [WARNING] Exception: {e}")

# Step 2: Delete existing connectors
print("\n2. Deleting existing connectors...")
connectors = [
    "cdc-final_test-pg-public",
    "sink-final_test-mssql-dbo"
]

for conn_name in connectors:
    try:
        response = requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}", timeout=10)
        if response.status_code in [200, 204, 404]:
            print(f"   [OK] Deleted {conn_name}")
        else:
            print(f"   [WARNING] {conn_name}: {response.status_code}")
    except Exception as e:
        print(f"   [WARNING] {conn_name}: {e}")

print("\n3. Waiting 5 seconds...")
time.sleep(5)

# Step 3: Restart the pipeline (this will recreate connectors with correct config)
print("\n4. Restarting pipeline (will recreate connectors with correct snapshot mode)...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=60)
    if response.status_code == 200:
        result = response.json()
        print("   [OK] Pipeline restarted")
        print(f"   Status: {result.get('status', 'N/A')}")
    else:
        print(f"   [ERROR] Failed to restart: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n5. Waiting 15 seconds for connectors to start...")
time.sleep(15)

# Step 4: Verify connectors
print("\n6. Verifying connectors...")
for conn_name in connectors:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   {conn_name}: {connector_state}")
            
            # Check snapshot mode for Debezium
            if conn_name.startswith("cdc-"):
                config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config", timeout=10)
                if config_response.status_code == 200:
                    config = config_response.json()
                    snapshot_mode = config.get('snapshot.mode', 'N/A')
                    print(f"      Snapshot mode: {snapshot_mode}")
                    if snapshot_mode == "never":
                        print(f"      ✅ Correct snapshot mode for CDC!")
                    else:
                        print(f"      ⚠️  Snapshot mode should be 'never' for CDC after full load")
    except Exception as e:
        print(f"   [ERROR] {conn_name}: {e}")

print("\n" + "=" * 80)
print("Connectors recreated!")
print("=" * 80)
print("\nNow test CDC again with: python test_cdc_final_test.py")


import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
API_URL = "http://localhost:8000/api"

print("=" * 80)
print("Recreating Connectors with Correct Configuration")
print("=" * 80)

# Step 1: Stop the pipeline
print("\n1. Stopping pipeline...")
pipeline_id = "07cd7358-0c80-4c6f-9e2a-8cf5d8845017"

try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/stop", timeout=30)
    if response.status_code in [200, 404]:
        print("   [OK] Pipeline stopped")
    else:
        print(f"   [WARNING] Status: {response.status_code}")
except Exception as e:
    print(f"   [WARNING] Exception: {e}")

# Step 2: Delete existing connectors
print("\n2. Deleting existing connectors...")
connectors = [
    "cdc-final_test-pg-public",
    "sink-final_test-mssql-dbo"
]

for conn_name in connectors:
    try:
        response = requests.delete(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}", timeout=10)
        if response.status_code in [200, 204, 404]:
            print(f"   [OK] Deleted {conn_name}")
        else:
            print(f"   [WARNING] {conn_name}: {response.status_code}")
    except Exception as e:
        print(f"   [WARNING] {conn_name}: {e}")

print("\n3. Waiting 5 seconds...")
time.sleep(5)

# Step 3: Restart the pipeline (this will recreate connectors with correct config)
print("\n4. Restarting pipeline (will recreate connectors with correct snapshot mode)...")
try:
    response = requests.post(f"{API_URL}/pipelines/{pipeline_id}/start", timeout=60)
    if response.status_code == 200:
        result = response.json()
        print("   [OK] Pipeline restarted")
        print(f"   Status: {result.get('status', 'N/A')}")
    else:
        print(f"   [ERROR] Failed to restart: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n5. Waiting 15 seconds for connectors to start...")
time.sleep(15)

# Step 4: Verify connectors
print("\n6. Verifying connectors...")
for conn_name in connectors:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   {conn_name}: {connector_state}")
            
            # Check snapshot mode for Debezium
            if conn_name.startswith("cdc-"):
                config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/config", timeout=10)
                if config_response.status_code == 200:
                    config = config_response.json()
                    snapshot_mode = config.get('snapshot.mode', 'N/A')
                    print(f"      Snapshot mode: {snapshot_mode}")
                    if snapshot_mode == "never":
                        print(f"      ✅ Correct snapshot mode for CDC!")
                    else:
                        print(f"      ⚠️  Snapshot mode should be 'never' for CDC after full load")
    except Exception as e:
        print(f"   [ERROR] {conn_name}: {e}")

print("\n" + "=" * 80)
print("Connectors recreated!")
print("=" * 80)
print("\nNow test CDC again with: python test_cdc_final_test.py")


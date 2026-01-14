"""Delete and recreate Debezium connector."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
CONNECTOR_NAME = f"cdc-{PIPELINE_NAME}-pg-public"

print("="*80)
print("Recreating Debezium Connector")
print("="*80)

try:
    # Step 1: Get current config
    print("\n1. Getting current connector configuration...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        connector_data = response.json()
        config = connector_data.get('config', {})
        print("   ✓ Got configuration")
    else:
        print(f"   ✗ Failed to get config: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
    
    # Step 2: Delete connector
    print("\n2. Deleting existing connector...")
    delete_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}"
    response = requests.delete(delete_url, timeout=30)
    
    if response.status_code == 204:
        print("   ✓ Connector deleted successfully")
    else:
        print(f"   ⚠ Delete response: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 3: Wait a bit
    print("\n3. Waiting 3 seconds...")
    time.sleep(3)
    
    # Step 4: Recreate connector
    print("\n4. Recreating connector...")
    create_url = f"{KAFKA_CONNECT_URL}/connectors"
    create_payload = {
        "name": CONNECTOR_NAME,
        "config": config
    }
    
    response = requests.post(
        create_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(create_payload),
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print("   ✓ Connector created successfully")
        result = response.json()
        print(f"   Connector name: {result.get('name')}")
    else:
        print(f"   ✗ Failed to create connector: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
    
    # Step 5: Wait and check status
    print("\n5. Waiting for connector to start...")
    time.sleep(5)
    
    status_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status"
    for attempt in range(1, 6):
        print(f"   Checking status (attempt {attempt}/5)...")
        response = requests.get(status_url, timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            tasks = status.get('tasks', [])
            
            print(f"   Connector state: {connector_state}")
            if tasks:
                task_state = tasks[0].get('state', 'UNKNOWN')
                print(f"   Task 0 state: {task_state}")
                
                if connector_state == 'RUNNING' and task_state == 'RUNNING':
                    print("\n✓ SUCCESS: Connector is RUNNING!")
                    break
                elif task_state == 'FAILED':
                    error = tasks[0].get('trace', 'No error details')
                    print(f"\n✗ Task failed: {error[:300]}...")
                    if attempt < 5:
                        print("   Retrying...")
                        time.sleep(3)
            else:
                print("   No tasks found yet")
        
        if attempt < 5:
            time.sleep(3)
    
    print("\n" + "="*80)
    print("Done!")
    print("="*80)
    print("\nYou can now verify CDC flow by running: python verify_cdc_flow.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()


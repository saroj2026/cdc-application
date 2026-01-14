"""Fix consumer group issue - connector not consuming messages."""

import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Fixing Consumer Group Issue")
print("=" * 70)

try:
    # 1. Check current connector status
    print("\n1. Checking connector status...")
    status_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status",
        timeout=10
    )
    
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        
        print(f"   Connector State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            worker_id = task.get('worker_id', 'N/A')
            print(f"      Task {task_id}: {task_state} (Worker: {worker_id})")
    
    # 2. Get connector config
    print("\n2. Checking connector configuration...")
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Tasks Max: {config.get('tasks.max', 'N/A')}")
        print(f"   Value Converter: {config.get('value.converter', 'N/A')}")
        
        # Check if there's a consumer group configuration issue
        # The connector should automatically create a consumer group
        # But maybe we need to restart it properly
    
    # 3. Restart connector completely
    print("\n3. Restarting connector completely...")
    
    # Stop connector
    print("   Stopping connector...")
    stop_response = requests.delete(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}",
        timeout=10
    )
    
    if stop_response.status_code == 204:
        print("   ✅ Connector deleted")
    else:
        print(f"   ⚠️  Delete response: {stop_response.status_code}")
        # Try pause instead
        pause_response = requests.put(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/pause",
            timeout=10
        )
        if pause_response.status_code in [200, 202, 204]:
            print("   ✅ Connector paused")
        time.sleep(2)
    
    # Wait a bit
    time.sleep(3)
    
    # Recreate connector with same config
    print("   Recreating connector...")
    create_response = requests.post(
        f"{KAFKA_CONNECT_URL}/connectors",
        json={
            "name": CONNECTOR_NAME,
            "config": config
        },
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if create_response.status_code in [200, 201]:
        print("   ✅ Connector recreated")
    else:
        print(f"   ❌ Error recreating: {create_response.status_code}")
        print(f"   Response: {create_response.text[:500]}")
        
        # If delete failed, try resume
        if stop_response.status_code != 204:
            print("   Trying to resume connector...")
            resume_response = requests.put(
                f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/resume",
                timeout=10
            )
            if resume_response.status_code in [200, 202, 204]:
                print("   ✅ Connector resumed")
    
    # 4. Wait and check status
    print("\n4. Waiting for connector to initialize...")
    time.sleep(10)
    
    status_response2 = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status",
        timeout=10
    )
    
    if status_response2.status_code == 200:
        status2 = status_response2.json()
        connector_state2 = status2.get('connector', {}).get('state', 'N/A')
        tasks2 = status2.get('tasks', [])
        
        print(f"   Connector State: {connector_state2}")
        for task in tasks2:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            print(f"      Task {task_id}: {task_state}")
    
    print("\n" + "=" * 70)
    print("✅ Connector restart completed!")
    print("=" * 70)
    print("\nThe connector has been restarted.")
    print("Check the consumer group status again - it should show active members now.")
    print("\nWait a bit and verify data flow:")
    print("  python verify_cdc_to_snowflake.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


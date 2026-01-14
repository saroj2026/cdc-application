"""Check Snowflake sink connector status."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Checking Sink Connector Status")
print("=" * 70)

try:
    # Wait a bit for connector to initialize
    time.sleep(3)
    
    print(f"\n1. Checking connector status: {CONNECTOR_NAME}")
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status",
        timeout=10
    )
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {connector_state}")
        
        tasks = status.get('tasks', [])
        print(f"\n2. Tasks ({len(tasks)}):")
        
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            worker_id = task.get('worker_id', 'N/A')
            
            print(f"\n   Task {task_id}:")
            print(f"      State: {task_state}")
            print(f"      Worker: {worker_id}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"      Error: {trace[:800]}")
        
        # Check connector config
        print(f"\n3. Connector Configuration:")
        config_response = requests.get(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
            timeout=10
        )
        
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"   Topics: {config.get('topics', 'N/A')}")
            print(f"   Database: {config.get('snowflake.database.name', 'N/A')}")
            print(f"   Schema: {config.get('snowflake.schema.name', 'N/A')}")
            print(f"   Username: {config.get('snowflake.user.name', 'N/A')}")
            print(f"   Account: {config.get('snowflake.url.name', 'N/A')[:50]}...")
            has_private_key = 'snowflake.private.key' in config
            has_password = 'snowflake.password' in config
            print(f"   Auth Method: {'Private Key' if has_private_key else 'Password' if has_password else 'Unknown'}")
        
    else:
        print(f"   ❌ Error getting status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


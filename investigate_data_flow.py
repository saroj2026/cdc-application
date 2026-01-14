"""Investigate why data isn't flowing to Snowflake."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_UI_URL = "http://72.61.233.209:8080"
TOPIC = "ps_sn_p.public.projects_simple"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print("Investigating Data Flow Issues")
print("=" * 70)

try:
    # 1. Check connector status
    print("\n1. Checking connector status...")
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status",
        timeout=10
    )
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        
        print(f"   Connector State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            print(f"      Task {task_id}: {task_state}")
            
            # Check for errors
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"      Error: {trace[:500]}")
    
    # 2. Check connector config - especially transforms
    print("\n2. Checking connector configuration...")
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Value Converter: {config.get('value.converter', 'N/A')}")
        
        transforms = config.get('transforms', '')
        if transforms:
            print(f"   Transforms: {transforms}")
            transform_list = transforms.split(',')
            for transform in transform_list:
                transform_type = config.get(f'transforms.{transform}.type', 'N/A')
                transform_field = config.get(f'transforms.{transform}.field', 'N/A')
                print(f"      {transform}: type={transform_type}, field={transform_field}")
        else:
            print(f"   Transforms: None")
    
    # 3. Check if there are messages in Kafka topic
    print("\n3. Checking Kafka topic...")
    try:
        # Try to get topic info from Kafka Connect (if available)
        # Or check via Kafka UI if accessible
        print(f"   Topic: {TOPIC}")
        print(f"   Note: Checking if messages exist in topic...")
        print(f"   (Kafka UI: {KAFKA_UI_URL})")
        print(f"   You can check manually at: {KAFKA_UI_URL}/ui/cluster/topic/{TOPIC}")
    except:
        pass
    
    # 4. Check Debezium connector status
    print("\n4. Checking Debezium source connector...")
    dbz_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/cdc-ps_sn_p-pg-public/status",
        timeout=10
    )
    
    if dbz_response.status_code == 200:
        dbz_status = dbz_response.json()
        dbz_state = dbz_status.get('connector', {}).get('state', 'N/A')
        print(f"   Debezium State: {dbz_state}")
        
        dbz_tasks = dbz_status.get('tasks', [])
        for task in dbz_tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            print(f"      Task {task_id}: {task_state}")
    
    # 5. Test removing transforms (SnowflakeJsonConverter might handle Debezium format automatically)
    print("\n5. Testing configuration...")
    print(f"   Issue: SnowflakeJsonConverter might handle Debezium format automatically")
    print(f"   Current: Using ExtractField transforms to extract 'after' field")
    print(f"   Recommendation: Try removing transforms to let SnowflakeJsonConverter handle it")
    
    print("\n" + "=" * 70)
    print("Recommendations:")
    print("=" * 70)
    print("1. Check Kafka UI to verify messages are in the topic")
    print("2. Try removing transforms - SnowflakeJsonConverter may handle Debezium format")
    print("3. Check connector logs for any silent errors")
    print("4. Verify connector is consuming from correct offset")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


"""Check Kafka topics for messages."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
CONNECTOR_NAME = f"cdc-{PIPELINE_NAME}-pg-public"

print("="*80)
print("Checking Kafka Topics and Messages")
print("="*80)

try:
    # Step 1: Get Debezium connector config to find topic name
    print("\n1. Getting Debezium connector configuration...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        connector_data = response.json()
        config = connector_data.get('config', {})
        topic_prefix = config.get('topic.prefix', 'unknown')
        slot_name = config.get('slot.name', 'unknown')
        snapshot_mode = config.get('snapshot.mode', 'unknown')
        
        print(f"   Topic prefix: {topic_prefix}")
        print(f"   Slot name: {slot_name}")
        print(f"   Snapshot mode: {snapshot_mode}")
        
        expected_topic = f"{topic_prefix}.public.projects_simple"
        print(f"\n   Expected topic: {expected_topic}")
    else:
        print(f"   [ERROR] Failed to get connector config: {response.status_code}")
        exit(1)
    
    # Step 2: Check connector status
    print("\n2. Checking Debezium connector status...")
    status_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status"
    response = requests.get(status_url, timeout=10)
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   Connector state: {connector_state}")
        if tasks:
            task_state = tasks[0].get('state', 'UNKNOWN')
            print(f"   Task 0 state: {task_state}")
            
            if task_state == 'FAILED':
                error = tasks[0].get('trace', 'No error details')
                print(f"   [ERROR] Task error: {error[:500]}")
        else:
            print("   No tasks found")
    
    # Step 3: Check if we can query Kafka topics (if Kafka REST API is available)
    print("\n3. Checking Kafka topics...")
    print("   Note: To check messages, you need to use Kafka console consumer")
    print(f"   Command: kafka-console-consumer --bootstrap-server 72.61.233.209:9092 --topic {expected_topic} --from-beginning")
    
    # Step 4: Check PostgreSQL replication slot
    print("\n4. Checking PostgreSQL replication slot...")
    import psycopg2
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass"
    )
    cur = conn.cursor()
    
    cur.execute("""
        SELECT slot_name, slot_type, active, database,
               confirmed_flush_lsn, restart_lsn
        FROM pg_replication_slots
        WHERE slot_name = %s
    """, (slot_name,))
    
    slot = cur.fetchone()
    if slot:
        print(f"   [OK] Slot found: {slot[0]}")
        print(f"   Active: {slot[2]}")
        print(f"   Confirmed flush LSN: {slot[4]}")
        print(f"   Restart LSN: {slot[5]}")
    else:
        print(f"   [ERROR] Slot '{slot_name}' not found!")
    
    cur.close()
    conn.close()
    
    # Step 5: Recommendations
    print("\n" + "="*80)
    print("Diagnosis and Recommendations")
    print("="*80)
    
    if snapshot_mode == 'never':
        print("\n[WARN] Snapshot mode is 'never' - Debezium will only capture NEW changes")
        print("  This means changes made BEFORE the connector started won't be captured.")
        print("  Solution: Change snapshot.mode to 'initial' or 'always' to capture existing data")
    
    if connector_state == 'RUNNING' and tasks and tasks[0].get('state') == 'RUNNING':
        print("\n[OK] Debezium connector is RUNNING")
        print("  If no messages in Kafka:")
        print("  1. Make a NEW change to the table (INSERT/UPDATE/DELETE)")
        print("  2. Wait a few seconds for CDC to process")
        print("  3. Check Kafka topic again")
    else:
        print("\n[ERROR] Debezium connector is not fully operational")
        print("  Fix the connector issues first")
    
    print("\nTo verify messages are being produced:")
    print(f"  1. Make a change: INSERT INTO public.projects_simple VALUES (110, 'Test', 200, 101, '2024-01-11', NULL, 'ACTIVE');")
    print(f"  2. Check Kafka: kafka-console-consumer --bootstrap-server 72.61.233.209:9092 --topic {expected_topic} --from-beginning")
    print(f"  3. Or use Kafka UI/Conduktor to browse topics")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


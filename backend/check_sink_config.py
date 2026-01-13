"""Check Sink connector configuration and verify topic mapping."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"

print("="*80)
print("Sink Connector Configuration Check")
print("="*80)

try:
    # Get sink connector config
    print("\n1. Sink Connector Configuration:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        
        print(f"   Connector class: {config.get('connector.class')}")
        print(f"   Topics: {config.get('topics', 'NOT SET')}")
        print(f"   Topics regex: {config.get('topics.regex', 'NOT SET')}")
        print(f"   Connection URL: {config.get('connection.url', 'NOT SET')}")
        print(f"   Connection user: {config.get('connection.user', 'NOT SET')}")
        print(f"   Table name format: {config.get('table.name.format', 'NOT SET')}")
        print(f"   Insert mode: {config.get('insert.mode', 'NOT SET')}")
        print(f"   PK mode: {config.get('pk.mode', 'NOT SET')}")
        print(f"   PK fields: {config.get('pk.fields', 'NOT SET')}")
    
    # Get sink connector status
    print("\n2. Sink Connector Status:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        if tasks:
            for i, task in enumerate(tasks):
                task_state = task.get('state', 'UNKNOWN')
                print(f"   Task {i}: {task_state}")
                if task_state == 'FAILED':
                    error = task.get('trace', 'No error')
                    print(f"      Error: {error[:500]}")
                elif task_state == 'RUNNING':
                    # Get task metrics if available
                    worker_id = task.get('worker_id', 'unknown')
                    print(f"      Worker: {worker_id}")
    
    # Expected topic name
    print("\n3. Topic Mapping:")
    expected_topic = "pg_to_mssql_projects_simple.public.projects_simple"
    print(f"   Expected Debezium topic: {expected_topic}")
    print(f"   Sink connector topics: {config.get('topics', 'NOT SET')}")
    
    if config.get('topics') == expected_topic:
        print("   [OK] Topic names match!")
    else:
        print("   [ERROR] Topic names don't match!")
        print("   This could be why messages aren't being consumed")
    
    # Check for errors in connector logs
    print("\n4. Recommendations:")
    print("   If messages aren't appearing in SQL Server:")
    print("   1. Verify Kafka topic has messages:")
    print(f"      kafka-console-consumer --bootstrap-server 72.61.233.209:9092 --topic {expected_topic} --from-beginning")
    print("   2. Check sink connector logs for errors")
    print("   3. Verify SQL Server connection is working")
    print("   4. Check if sink connector is actually consuming from the topic")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


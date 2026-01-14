"""Diagnose CDC replication issues."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Diagnosing CDC Issues")
print("=" * 80)

# Check Debezium connector
print("\n1. Checking Debezium Source Connector...")
try:
    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-final_test-pg-public/status", timeout=10)
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error in task {task_id}:")
                print(f"      {task.get('trace')[:500]}")
    else:
        print(f"   [ERROR] Failed to get status: {status_response.status_code}")
        
    # Get connector config
    config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-final_test-pg-public/config", timeout=10)
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"\n   Key configuration:")
        print(f"   Database: {config.get('database.dbname')}")
        print(f"   Tables: {config.get('table.include.list', 'N/A')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode', 'N/A')}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Check Sink connector
print("\n2. Checking JDBC Sink Connector...")
try:
    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-final_test-mssql-dbo/status", timeout=10)
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error in task {task_id}:")
                print(f"      {task.get('trace')[:500]}")
    else:
        print(f"   [ERROR] Failed to get status: {status_response.status_code}")
        
    # Get connector config
    config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-final_test-mssql-dbo/config", timeout=10)
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"\n   Key configuration:")
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Connection URL: {config.get('connection.url', 'N/A')[:50]}...")
        print(f"   Table format: {config.get('table.name.format', 'N/A')}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Check Kafka topics
print("\n3. Checking Kafka topics...")
try:
    # Note: We can't directly list topics via Kafka Connect API
    # But we can check if the connector is consuming/producing
    print("   (Kafka topic inspection requires Kafka CLI tools)")
    print("   Topic should be: final_test.public.projects_simple")
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Diagnosis Complete")
print("=" * 80)
print("\nRecommendations:")
print("1. Check if Debezium connector is capturing changes (check Kafka topics)")
print("2. Check if Sink connector is writing to SQL Server (check connector logs)")
print("3. Verify table structure matches between source and target")
print("4. Check for any errors in connector status above")


import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Diagnosing CDC Issues")
print("=" * 80)

# Check Debezium connector
print("\n1. Checking Debezium Source Connector...")
try:
    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-final_test-pg-public/status", timeout=10)
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error in task {task_id}:")
                print(f"      {task.get('trace')[:500]}")
    else:
        print(f"   [ERROR] Failed to get status: {status_response.status_code}")
        
    # Get connector config
    config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-final_test-pg-public/config", timeout=10)
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"\n   Key configuration:")
        print(f"   Database: {config.get('database.dbname')}")
        print(f"   Tables: {config.get('table.include.list', 'N/A')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode', 'N/A')}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Check Sink connector
print("\n2. Checking JDBC Sink Connector...")
try:
    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-final_test-mssql-dbo/status", timeout=10)
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"   State: {connector_state}")
        print(f"   Tasks: {len(tasks)}")
        
        for task in tasks:
            task_state = task.get('state', 'UNKNOWN')
            task_id = task.get('id', 0)
            print(f"   Task {task_id}: {task_state}")
            
            if task.get('trace'):
                print(f"   ⚠️  Error in task {task_id}:")
                print(f"      {task.get('trace')[:500]}")
    else:
        print(f"   [ERROR] Failed to get status: {status_response.status_code}")
        
    # Get connector config
    config_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-final_test-mssql-dbo/config", timeout=10)
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"\n   Key configuration:")
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Connection URL: {config.get('connection.url', 'N/A')[:50]}...")
        print(f"   Table format: {config.get('table.name.format', 'N/A')}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

# Check Kafka topics
print("\n3. Checking Kafka topics...")
try:
    # Note: We can't directly list topics via Kafka Connect API
    # But we can check if the connector is consuming/producing
    print("   (Kafka topic inspection requires Kafka CLI tools)")
    print("   Topic should be: final_test.public.projects_simple")
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")

print("\n" + "=" * 80)
print("Diagnosis Complete")
print("=" * 80)
print("\nRecommendations:")
print("1. Check if Debezium connector is capturing changes (check Kafka topics)")
print("2. Check if Sink connector is writing to SQL Server (check connector logs)")
print("3. Verify table structure matches between source and target")
print("4. Check for any errors in connector status above")


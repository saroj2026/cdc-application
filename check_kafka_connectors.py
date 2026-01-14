"""Check Kafka Connect connectors status."""

import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Checking Kafka Connect Connectors")
print("=" * 80)

# List all connectors
print("\n1. Listing all connectors...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
    if response.status_code == 200:
        connectors = response.json()
        print(f"   Found {len(connectors)} connector(s)")
        
        if len(connectors) == 0:
            print("   ⚠️  No connectors found in Kafka Connect!")
            print("   This explains why full load shows 0 rows - connectors are not running")
        else:
            print(f"   Connectors: {', '.join(connectors)}")
            
            # Check status of each connector
            for conn_name in connectors:
                print(f"\n2. Checking connector: {conn_name}...")
                try:
                    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
                    if status_response.status_code == 200:
                        status = status_response.json()
                        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                        tasks = status.get('tasks', [])
                        
                        print(f"   State: {connector_state}")
                        print(f"   Tasks: {len(tasks)}")
                        
                        for task in tasks:
                            task_state = task.get('state', 'UNKNOWN')
                            task_id = task.get('id', 0)
                            print(f"      Task {task_id}: {task_state}")
                            
                            if task.get('trace'):
                                print(f"      ⚠️  Error: {task.get('trace')[:300]}")
                except Exception as e:
                    print(f"   [ERROR] Failed to get status: {e}")
    else:
        print(f"   [ERROR] Failed to list connectors: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

# Check expected connector names
print("\n3. Expected connectors for final_test pipeline:")
print("   - cdc-final_test-pg-public (Debezium source)")
print("   - sink-final_test-mssql-dbo (JDBC sink)")

print("\n" + "=" * 80)
print("Kafka Connect Status Check Complete!")
print("=" * 80)


import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Checking Kafka Connect Connectors")
print("=" * 80)

# List all connectors
print("\n1. Listing all connectors...")
try:
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors", timeout=10)
    if response.status_code == 200:
        connectors = response.json()
        print(f"   Found {len(connectors)} connector(s)")
        
        if len(connectors) == 0:
            print("   ⚠️  No connectors found in Kafka Connect!")
            print("   This explains why full load shows 0 rows - connectors are not running")
        else:
            print(f"   Connectors: {', '.join(connectors)}")
            
            # Check status of each connector
            for conn_name in connectors:
                print(f"\n2. Checking connector: {conn_name}...")
                try:
                    status_response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
                    if status_response.status_code == 200:
                        status = status_response.json()
                        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                        tasks = status.get('tasks', [])
                        
                        print(f"   State: {connector_state}")
                        print(f"   Tasks: {len(tasks)}")
                        
                        for task in tasks:
                            task_state = task.get('state', 'UNKNOWN')
                            task_id = task.get('id', 0)
                            print(f"      Task {task_id}: {task_state}")
                            
                            if task.get('trace'):
                                print(f"      ⚠️  Error: {task.get('trace')[:300]}")
                except Exception as e:
                    print(f"   [ERROR] Failed to get status: {e}")
    else:
        print(f"   [ERROR] Failed to list connectors: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

# Check expected connector names
print("\n3. Expected connectors for final_test pipeline:")
print("   - cdc-final_test-pg-public (Debezium source)")
print("   - sink-final_test-mssql-dbo (JDBC sink)")

print("\n" + "=" * 80)
print("Kafka Connect Status Check Complete!")
print("=" * 80)


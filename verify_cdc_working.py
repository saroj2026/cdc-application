"""Verify CDC is working by checking for replicated data."""

import requests
import time
import pyodbc

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Verifying CDC is Working")
print("=" * 80)

# Check connectors
print("\n1. Checking connector status...")
connectors = ["cdc-final_test-pg-public", "sink-final_test-mssql-dbo"]

for conn_name in connectors:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            tasks = status.get('tasks', [])
            
            print(f"\n   {conn_name}:")
            print(f"      State: {connector_state}")
            
            for task in tasks:
                task_state = task.get('state', 'UNKNOWN')
                task_id = task.get('id', 0)
                print(f"      Task {task_id}: {task_state}")
                
                if task.get('trace'):
                    print(f"      ⚠️  Error: {task.get('trace')[:200]}")
    except Exception as e:
        print(f"   [ERROR] {conn_name}: {e}")

# Check for test row
print("\n2. Checking for CDC test row in SQL Server...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    
    # Check test row
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple WHERE project_id = 999;")
    test_count = mssql_cur.fetchone()[0]
    
    if test_count > 0:
        print(f"   ✅ Test row found! CDC is working!")
        mssql_cur.execute("SELECT * FROM dbo.projects_simple WHERE project_id = 999;")
        row = mssql_cur.fetchone()
        print(f"   Row: {row}")
    else:
        print(f"   ⚠️  Test row not found yet")
        print(f"   Waiting additional 20 seconds...")
        time.sleep(20)
        
        mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple WHERE project_id = 999;")
        test_count = mssql_cur.fetchone()[0]
        
        if test_count > 0:
            print(f"   ✅ Test row found after additional wait! CDC is working!")
        else:
            print(f"   ⚠️  Test row still not found")
            print(f"   This might indicate CDC is not capturing changes")
            print(f"   Check Debezium connector logs on VPS")
    
    # Check total row count
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    total_count = mssql_cur.fetchone()[0]
    print(f"\n   Total rows in SQL Server: {total_count}")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to check: {e}")

print("\n" + "=" * 80)
print("CDC Verification Complete!")
print("=" * 80)
print("\nIf CDC is not working:")
print("1. Check Debezium connector logs: docker logs kafka-connect-cdc")
print("2. Verify snapshot mode is 'never' (for CDC after full load)")
print("3. Check Kafka topics for messages")
print("4. Verify sink connector is writing to SQL Server")


import requests
import time
import pyodbc

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"

print("=" * 80)
print("Verifying CDC is Working")
print("=" * 80)

# Check connectors
print("\n1. Checking connector status...")
connectors = ["cdc-final_test-pg-public", "sink-final_test-mssql-dbo"]

for conn_name in connectors:
    try:
        response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{conn_name}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            tasks = status.get('tasks', [])
            
            print(f"\n   {conn_name}:")
            print(f"      State: {connector_state}")
            
            for task in tasks:
                task_state = task.get('state', 'UNKNOWN')
                task_id = task.get('id', 0)
                print(f"      Task {task_id}: {task_state}")
                
                if task.get('trace'):
                    print(f"      ⚠️  Error: {task.get('trace')[:200]}")
    except Exception as e:
        print(f"   [ERROR] {conn_name}: {e}")

# Check for test row
print("\n2. Checking for CDC test row in SQL Server...")
try:
    mssql_conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=72.61.233.209,1433;"
        f"DATABASE=cdctest;"
        f"UID=sa;"
        f"PWD=Sql@12345;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    mssql_cur = mssql_conn.cursor()
    
    # Check test row
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple WHERE project_id = 999;")
    test_count = mssql_cur.fetchone()[0]
    
    if test_count > 0:
        print(f"   ✅ Test row found! CDC is working!")
        mssql_cur.execute("SELECT * FROM dbo.projects_simple WHERE project_id = 999;")
        row = mssql_cur.fetchone()
        print(f"   Row: {row}")
    else:
        print(f"   ⚠️  Test row not found yet")
        print(f"   Waiting additional 20 seconds...")
        time.sleep(20)
        
        mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple WHERE project_id = 999;")
        test_count = mssql_cur.fetchone()[0]
        
        if test_count > 0:
            print(f"   ✅ Test row found after additional wait! CDC is working!")
        else:
            print(f"   ⚠️  Test row still not found")
            print(f"   This might indicate CDC is not capturing changes")
            print(f"   Check Debezium connector logs on VPS")
    
    # Check total row count
    mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple;")
    total_count = mssql_cur.fetchone()[0]
    print(f"\n   Total rows in SQL Server: {total_count}")
    
    mssql_cur.close()
    mssql_conn.close()
    
except Exception as e:
    print(f"   [ERROR] Failed to check: {e}")

print("\n" + "=" * 80)
print("CDC Verification Complete!")
print("=" * 80)
print("\nIf CDC is not working:")
print("1. Check Debezium connector logs: docker logs kafka-connect-cdc")
print("2. Verify snapshot mode is 'never' (for CDC after full load)")
print("3. Check Kafka topics for messages")
print("4. Verify sink connector is writing to SQL Server")


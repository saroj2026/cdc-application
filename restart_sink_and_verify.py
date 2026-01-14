"""Restart Sink connector and verify it processes messages."""

import requests
import json
import time
import pyodbc

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"

MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "trust_server_certificate": True
}

print("="*80)
print("Restarting Sink Connector and Verifying Message Processing")
print("="*80)

try:
    # Step 1: Get current config
    print("\n1. Getting current Sink connector configuration...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        connector_data = response.json()
        config = connector_data.get('config', {})
        print("   [OK] Got configuration")
        
        # Check key settings
        print(f"   Topics: {config.get('topics')}")
        print(f"   Transforms: {config.get('transforms')}")
        print(f"   Table format: {config.get('table.name.format')}")
        print(f"   Errors tolerance: {config.get('errors.tolerance', 'NOT SET')}")
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        exit(1)
    
    # Step 2: Restart connector
    print("\n2. Restarting Sink connector...")
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    
    if response.status_code == 204:
        print("   [OK] Restart command sent")
    else:
        print(f"   [WARN] Restart response: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Step 3: Wait for restart
    print("\n3. Waiting for connector to restart (5 seconds)...")
    time.sleep(5)
    
    # Step 4: Check status
    status_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/status"
    response = requests.get(status_url, timeout=10)
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state', 'UNKNOWN') if tasks else 'UNKNOWN'
        
        print(f"   Connector: {connector_state}")
        print(f"   Task: {task_state}")
        
        if connector_state == 'RUNNING' and task_state == 'RUNNING':
            print("   [OK] Connector restarted and is RUNNING")
        else:
            print("   [ERROR] Connector is not fully operational")
    
    # Step 5: Check SQL Server for row 110
    print("\n4. Checking SQL Server for row 110 (after restart)...")
    print("   Waiting 10 seconds for messages to be processed...")
    time.sleep(10)
    
    mssql_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
        f"DATABASE={MSSQL_CONFIG['database']};"
        f"UID={MSSQL_CONFIG['username']};"
        f"PWD={MSSQL_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    
    found = False
    for attempt in range(1, 6):
        try:
            mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
            mssql_cur = mssql_conn.cursor()
            
            mssql_cur.execute("SELECT * FROM dbo.projects_simple WHERE project_id = ?", (110,))
            row = mssql_cur.fetchone()
            
            if row:
                columns = [column[0] for column in mssql_cur.description]
                row_dict = dict(zip(columns, row))
                print(f"   [OK] Row found in SQL Server (attempt {attempt}):")
                print(f"   {row_dict}")
                found = True
                mssql_cur.close()
                mssql_conn.close()
                break
            else:
                print(f"   [WARN] Row not found yet (attempt {attempt}/5)...")
                mssql_cur.close()
                mssql_conn.close()
                time.sleep(3)
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
            time.sleep(3)
    
    # Step 6: Check row counts
    print("\n5. Checking row counts...")
    try:
        mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
        mssql_cur = mssql_conn.cursor()
        mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple")
        mssql_count = mssql_cur.fetchone()[0]
        mssql_cur.close()
        mssql_conn.close()
        print(f"   SQL Server: {mssql_count} rows")
    except Exception as e:
        print(f"   [ERROR] Error checking count: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    
    if found:
        print("[OK] SUCCESS: Row 110 is now in SQL Server!")
        print("  The Sink connector is processing messages from Kafka.")
        print("  CDC flow is working: PostgreSQL -> Debezium -> Kafka -> Sink -> SQL Server")
    else:
        print("[ERROR] Row 110 is still not in SQL Server")
        print("\nThe Sink connector may be:")
        print("  1. Not consuming from Kafka topic (check Kafka consumer lag)")
        print("  2. Failing to process messages (check logs with errors.tolerance=all)")
        print("  3. Having transform errors (ExtractField may not be working)")
        print("  4. Having SQL insert errors (check table structure match)")
        print("\nNext steps:")
        print("  - Check Kafka Connect worker logs on server 72.61.233.209")
        print("  - Look for errors related to JDBC Sink connector")
        print("  - Verify message format in Kafka matches what Sink expects")
        print("  - Check if ExtractField transform is working correctly")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


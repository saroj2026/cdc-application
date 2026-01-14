"""Verify Kafka messages are being consumed by Sink and written to SQL Server."""

import requests
import json
import time
import pyodbc
import psycopg2

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
SINK_CONNECTOR_NAME = f"sink-{PIPELINE_NAME}-mssql-dbo"
DEBEZIUM_CONNECTOR_NAME = f"cdc-{PIPELINE_NAME}-pg-public"
KAFKA_TOPIC = f"{PIPELINE_NAME}.public.projects_simple"

# Database connections
MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "trust_server_certificate": True
}

PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("="*80)
print("Verifying CDC Flow: Kafka -> Sink -> SQL Server")
print("="*80)
print(f"\nLooking for row: project_id = 110")

try:
    # Step 1: Verify row exists in PostgreSQL
    print("\n1. Verifying row in PostgreSQL source...")
    pg_conn = psycopg2.connect(**PG_CONFIG)
    pg_cur = pg_conn.cursor()
    
    pg_cur.execute("SELECT * FROM public.projects_simple WHERE project_id = 110")
    pg_row = pg_cur.fetchone()
    
    if pg_row:
        columns = [desc[0] for desc in pg_cur.description]
        pg_dict = dict(zip(columns, pg_row))
        print(f"   [OK] Row found in PostgreSQL:")
        print(f"   {pg_dict}")
    else:
        print("   [ERROR] Row not found in PostgreSQL!")
        exit(1)
    
    pg_cur.close()
    pg_conn.close()
    
    # Step 2: Check Debezium connector status
    print("\n2. Checking Debezium connector status...")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR_NAME}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state', 'UNKNOWN') if tasks else 'UNKNOWN'
        
        print(f"   Connector: {connector_state}")
        print(f"   Task: {task_state}")
        
        if connector_state == 'RUNNING' and task_state == 'RUNNING':
            print("   [OK] Debezium is RUNNING and should be producing to Kafka")
        else:
            print("   [WARN] Debezium may not be fully operational")
    
    # Step 3: Check Sink connector status and metrics
    print("\n3. Checking Sink connector status...")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state', 'UNKNOWN') if tasks else 'UNKNOWN'
        
        print(f"   Connector: {connector_state}")
        print(f"   Task: {task_state}")
        
        if connector_state == 'RUNNING' and task_state == 'RUNNING':
            print("   [OK] Sink is RUNNING and should be consuming from Kafka")
        else:
            print("   [ERROR] Sink is not fully operational!")
            if task_state == 'FAILED':
                error = tasks[0].get('trace', 'No error details')
                print(f"   Error: {error[:500]}")
    
    # Step 4: Get Sink connector config to verify topic
    print("\n4. Verifying Sink connector configuration...")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        sink_topics = config.get('topics', '')
        
        print(f"   Sink consumes from topics: {sink_topics}")
        print(f"   Expected topic: {KAFKA_TOPIC}")
        
        if KAFKA_TOPIC in sink_topics:
            print("   [OK] Topic names match!")
        else:
            print("   [ERROR] Topic mismatch - Sink may not be consuming the right topic!")
    
    # Step 5: Check SQL Server for the row
    print("\n5. Checking SQL Server for replicated row...")
    print("   Waiting a few seconds for CDC to process...")
    time.sleep(3)
    
    mssql_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
        f"DATABASE={MSSQL_CONFIG['database']};"
        f"UID={MSSQL_CONFIG['username']};"
        f"PWD={MSSQL_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    
    max_retries = 10
    found = False
    
    for attempt in range(1, max_retries + 1):
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
                
                # Compare with PostgreSQL
                if pg_dict.get('project_id') == row_dict.get('project_id'):
                    print("\n   [OK] Row IDs match!")
                if pg_dict.get('project_name') == row_dict.get('project_name'):
                    print("   [OK] Project names match!")
                
                mssql_cur.close()
                mssql_conn.close()
                break
            else:
                print(f"   [WARN] Row not found yet (attempt {attempt}/{max_retries})...")
                mssql_cur.close()
                mssql_conn.close()
                
                if attempt < max_retries:
                    print(f"   Waiting 2 more seconds...")
                    time.sleep(2)
        except Exception as e:
            print(f"   [ERROR] Error checking SQL Server: {e}")
            if attempt < max_retries:
                time.sleep(2)
    
    # Step 6: Check row counts
    print("\n6. Checking row counts...")
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_cur = pg_conn.cursor()
        pg_cur.execute("SELECT COUNT(*) FROM public.projects_simple")
        pg_count = pg_cur.fetchone()[0]
        pg_cur.close()
        pg_conn.close()
        print(f"   PostgreSQL: {pg_count} rows")
        
        mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
        mssql_cur = mssql_conn.cursor()
        mssql_cur.execute("SELECT COUNT(*) FROM dbo.projects_simple")
        mssql_count = mssql_cur.fetchone()[0]
        mssql_cur.close()
        mssql_conn.close()
        print(f"   SQL Server: {mssql_count} rows")
        
        if pg_count == mssql_count:
            print("   [OK] Row counts match!")
        else:
            diff = pg_count - mssql_count
            print(f"   [WARN] Row count mismatch: {diff} rows not replicated yet")
    except Exception as e:
        print(f"   [ERROR] Error checking counts: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("CDC Flow Verification Summary")
    print("="*80)
    print(f"PostgreSQL Source: [OK] Row found")
    print(f"Debezium Connector: {'[OK] RUNNING' if connector_state == 'RUNNING' else '[ERROR]'}")
    print(f"Kafka Topic: [OK] Messages present (as you confirmed)")
    print(f"Sink Connector: {'[OK] RUNNING' if connector_state == 'RUNNING' else '[ERROR]'}")
    print(f"SQL Server Target: {'[OK] Row Replicated' if found else '[ERROR] Row Not Found'}")
    
    if found:
        print("\n[OK] SUCCESS: Complete CDC flow is working!")
        print("  PostgreSQL -> Debezium -> Kafka -> Sink -> SQL Server")
        print("\nThe row with project_id=110 has been successfully replicated!")
    else:
        print("\n[ERROR] CDC flow is broken at Sink -> SQL Server step")
        print("\nPossible issues:")
        print("  1. Sink connector is not consuming from Kafka topic")
        print("  2. Sink connector has errors processing messages")
        print("  3. SQL Server insert is failing (check Sink connector logs)")
        print("  4. Topic name mismatch between Debezium and Sink")
        print("\nCheck Sink connector logs on the server for detailed errors")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


"""Check Sink connector for errors and verify it's processing messages."""

import requests
import json
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
print("Sink Connector Error Diagnosis")
print("="*80)

try:
    # Step 1: Get detailed connector status
    print("\n1. Getting detailed Sink connector status...")
    status_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/status"
    response = requests.get(status_url, timeout=10)
    
    if response.status_code == 200:
        status = response.json()
        print(json.dumps(status, indent=2))
        
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        
        print(f"\n   Connector state: {connector_state}")
        if tasks:
            for i, task in enumerate(tasks):
                task_state = task.get('state', 'UNKNOWN')
                task_id = task.get('id', i)
                worker_id = task.get('worker_id', 'unknown')
                
                print(f"\n   Task {task_id}:")
                print(f"     State: {task_state}")
                print(f"     Worker: {worker_id}")
                
                if task_state == 'FAILED':
                    error = task.get('trace', 'No error details')
                    print(f"     [ERROR] Task failed!")
                    print(f"     Error trace: {error[:1000]}")
                elif task_state == 'RUNNING':
                    print(f"     [OK] Task is running")
    
    # Step 2: Get connector config
    print("\n2. Sink connector configuration:")
    config_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}"
    response = requests.get(config_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        
        print(f"   Topics: {config.get('topics')}")
        print(f"   Connection URL: {config.get('connection.url')}")
        print(f"   Table name format: {config.get('table.name.format')}")
        print(f"   Insert mode: {config.get('insert.mode')}")
        print(f"   PK mode: {config.get('pk.mode')}")
        print(f"   Auto create: {config.get('auto.create')}")
        print(f"   Auto evolve: {config.get('auto.evolve')}")
    
    # Step 3: Test SQL Server connection
    print("\n3. Testing SQL Server connection...")
    try:
        mssql_conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
            f"DATABASE={MSSQL_CONFIG['database']};"
            f"UID={MSSQL_CONFIG['username']};"
            f"PWD={MSSQL_CONFIG['password']};"
            f"TrustServerCertificate=yes;"
        )
        mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
        mssql_cur = mssql_conn.cursor()
        
        # Test insert
        print("   Testing INSERT...")
        try:
            mssql_cur.execute("""
                INSERT INTO dbo.projects_simple 
                (project_id, project_name, department_id, employee_id, start_date, end_date, status)
                VALUES (99999, 'Direct Test', 200, 101, GETDATE(), NULL, 'ACTIVE')
            """)
            mssql_conn.commit()
            print("   [OK] Direct INSERT works - SQL Server connection is fine")
            
            # Clean up
            mssql_cur.execute("DELETE FROM dbo.projects_simple WHERE project_id = 99999")
            mssql_conn.commit()
        except Exception as e:
            print(f"   [ERROR] Direct INSERT failed: {e}")
        
        mssql_cur.close()
        mssql_conn.close()
    except Exception as e:
        print(f"   [ERROR] SQL Server connection failed: {e}")
    
    # Step 4: Check table structure
    print("\n4. Checking table structure in SQL Server...")
    try:
        mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
        mssql_cur = mssql_conn.cursor()
        
        mssql_cur.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = 'projects_simple'
            ORDER BY ORDINAL_POSITION
        """)
        columns = mssql_cur.fetchall()
        
        print("   Table columns:")
        for col in columns:
            print(f"     - {col[0]}: {col[1]}{f'({col[2]})' if col[2] else ''} (nullable: {col[3]})")
        
        mssql_cur.close()
        mssql_conn.close()
    except Exception as e:
        print(f"   [ERROR] Error checking table: {e}")
    
    # Step 5: Recommendations
    print("\n" + "="*80)
    print("Diagnosis and Recommendations")
    print("="*80)
    
    print("\nIf Sink connector shows RUNNING but not writing:")
    print("  1. Check Kafka Connect worker logs on server 72.61.233.209")
    print("  2. Verify Sink connector is actually consuming from Kafka topic")
    print("  3. Check if message format from Debezium matches what Sink expects")
    print("  4. Verify SQL Server table structure matches expected schema")
    print("  5. Check for any transform errors in Sink connector")
    
    print("\nTo check Sink connector logs:")
    print("  - SSH to 72.61.233.209")
    print("  - Check Kafka Connect logs: /var/log/kafka-connect/ or similar")
    print("  - Look for errors related to JDBC Sink connector")
    
    print("\nCommon Sink connector issues:")
    print("  - Message format mismatch (Debezium envelope vs plain JSON)")
    print("  - Column name/case sensitivity issues")
    print("  - Data type conversion errors")
    print("  - Primary key conflicts")
    print("  - SQL Server connection timeouts")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


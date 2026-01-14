"""Verify CDC flow: Debezium -> Kafka -> Sink -> SQL Server."""

import requests
import json
import time
from ingestion.connectors.postgresql import PostgreSQLConnector
from ingestion.connectors.sqlserver import SQLServerConnector

# Configuration
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"

# Database connections
PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "username": "cdc_user",
    "password": "cdc_pass",
    "schema": "public"
}

MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "schema": "dbo",
    "trust_server_certificate": True
}

def check_debezium_connector():
    """Check Debezium connector status."""
    print("\n" + "="*80)
    print("1. Checking Debezium Connector Status")
    print("="*80)
    
    connector_name = f"cdc-{PIPELINE_NAME}-pg-public"
    url = f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"[OK] Connector: {connector_name}")
            print(f"  State: {status.get('connector', {}).get('state', 'UNKNOWN')}")
            
            tasks = status.get('tasks', [])
            if tasks:
                for i, task in enumerate(tasks):
                    print(f"  Task {i}: {task.get('state', 'UNKNOWN')}")
                    if task.get('state') == 'FAILED':
                        print(f"    Error: {task.get('trace', 'No error details')}")
            else:
                print("  No tasks found")
            
            return status.get('connector', {}).get('state') == 'RUNNING'
        else:
            print(f"[ERROR] Connector not found or error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error checking Debezium connector: {e}")
        return False

def check_kafka_topics():
    """Check Kafka topics for messages."""
    print("\n" + "="*80)
    print("2. Checking Kafka Topics")
    print("="*80)
    
    # Expected topic name pattern
    topic_name = f"cdctest.public.projects_simple"
    
    try:
        # Get connector config to find exact topic name
        connector_name = f"cdc-{PIPELINE_NAME}-pg-public"
        url = f"{KAFKA_CONNECT_URL}/connectors/{connector_name}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            topic_prefix = config.get('config', {}).get('topic.prefix', 'cdctest')
            topic_name = f"{topic_prefix}.public.projects_simple"
            print(f"  Topic prefix: {topic_prefix}")
        
        print(f"  Expected topic: {topic_name}")
        print(f"  Note: To check messages, use Kafka console consumer or Kafka UI")
        print(f"  Command: kafka-console-consumer --bootstrap-server localhost:9092 --topic {topic_name} --from-beginning")
        
        return True
    except Exception as e:
        print(f"✗ Error checking Kafka topics: {e}")
        return False

def check_sink_connector():
    """Check Sink connector status."""
    print("\n" + "="*80)
    print("3. Checking Sink Connector Status")
    print("="*80)
    
    connector_name = f"sink-{PIPELINE_NAME}-mssql-dbo"
    url = f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"[OK] Connector: {connector_name}")
            print(f"  State: {status.get('connector', {}).get('state', 'UNKNOWN')}")
            
            tasks = status.get('tasks', [])
            if tasks:
                for i, task in enumerate(tasks):
                    print(f"  Task {i}: {task.get('state', 'UNKNOWN')}")
                    if task.get('state') == 'FAILED':
                        print(f"    Error: {task.get('trace', 'No error details')}")
            else:
                print("  No tasks found")
            
            return status.get('connector', {}).get('state') == 'RUNNING'
        else:
            print(f"[ERROR] Connector not found or error: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error checking Sink connector: {e}")
        return False

def check_postgresql_data():
    """Check data in PostgreSQL source."""
    print("\n" + "="*80)
    print("4. Checking PostgreSQL Source Data")
    print("="*80)
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=PG_CONFIG["host"],
            port=PG_CONFIG["port"],
            database=PG_CONFIG["database"],
            user=PG_CONFIG["username"],
            password=PG_CONFIG["password"]
        )
        cur = conn.cursor()
        
        # Query for the new row
        cur.execute("SELECT * FROM public.projects_simple WHERE project_id = 109")
        row = cur.fetchone()
        
        if row:
            # Get column names
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'projects_simple'
                ORDER BY ordinal_position
            """)
            columns = [col[0] for col in cur.fetchall()]
            
            row_dict = dict(zip(columns, row))
            print(f"[OK] Found new row (ID: 109) in PostgreSQL:")
            print(f"  {row_dict}")
            
            # Also get total count
            cur.execute("SELECT COUNT(*) FROM public.projects_simple")
            count = cur.fetchone()[0]
            print(f"  Total rows in table: {count}")
            
            cur.close()
            conn.close()
            return True
        else:
            print(f"[ERROR] Row with ID 109 not found in PostgreSQL")
            cur.execute("SELECT COUNT(*) FROM public.projects_simple")
            count = cur.fetchone()[0]
            print(f"  Total rows in table: {count}")
            cur.close()
            conn.close()
            return False
    except Exception as e:
        print(f"[ERROR] Error checking PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_sqlserver_data():
    """Check data in SQL Server target."""
    print("\n" + "="*80)
    print("5. Checking SQL Server Target Data")
    print("="*80)
    
    try:
        import pyodbc
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
            f"DATABASE={MSSQL_CONFIG['database']};"
            f"UID={MSSQL_CONFIG['username']};"
            f"PWD={MSSQL_CONFIG['password']};"
            f"TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str, timeout=10)
        cur = conn.cursor()
        
        # Query for the new row
        cur.execute("SELECT * FROM dbo.projects_simple WHERE project_id = 109")
        row = cur.fetchone()
        
        if row:
            # Get column names
            columns = [column[0] for column in cur.description]
            row_dict = dict(zip(columns, row))
            print(f"[OK] Found new row (ID: 109) in SQL Server:")
            print(f"  {row_dict}")
            
            # Also get total count
            cur.execute("SELECT COUNT(*) FROM dbo.projects_simple")
            count = cur.fetchone()[0]
            print(f"  Total rows in table: {count}")
            
            cur.close()
            conn.close()
            return True
        else:
            print(f"[WARN] Row with ID 109 not found in SQL Server yet")
            cur.execute("SELECT COUNT(*) FROM dbo.projects_simple")
            count = cur.fetchone()[0]
            print(f"  Total rows in table: {count}")
            cur.close()
            conn.close()
            return False
    except Exception as e:
        print(f"[ERROR] Error checking SQL Server: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("CDC Flow Verification")
    print("="*80)
    print(f"\nPipeline: {PIPELINE_NAME}")
    print(f"New Row: project_id=109, project_name='CDC Pipeline Setup'")
    print("\nChecking CDC flow: PostgreSQL -> Debezium -> Kafka -> Sink -> SQL Server")
    
    # Step 1: Check Debezium
    debezium_ok = check_debezium_connector()
    
    # Step 2: Check Kafka (informational)
    kafka_ok = check_kafka_topics()
    
    # Step 3: Check Sink
    sink_ok = check_sink_connector()
    
    # Step 4: Check PostgreSQL source
    pg_ok = check_postgresql_data()
    
    # Step 5: Check SQL Server target (with retry)
    print("\n" + "="*80)
    print("Waiting for CDC replication...")
    print("="*80)
    
    max_retries = 6
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        print(f"\nAttempt {attempt}/{max_retries}...")
        mssql_ok = check_sqlserver_data()
        
        if mssql_ok:
            break
        
        if attempt < max_retries:
            print(f"  Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)
    
    # Summary
    print("\n" + "="*80)
    print("CDC Flow Verification Summary")
    print("="*80)
    print(f"Debezium Connector: {'[OK] RUNNING' if debezium_ok else '[ERROR] NOT RUNNING'}")
    print(f"Kafka Topics: {'[OK] Available' if kafka_ok else '[ERROR] Error'}")
    print(f"Sink Connector: {'[OK] RUNNING' if sink_ok else '[ERROR] NOT RUNNING'}")
    print(f"PostgreSQL Source: {'[OK] Row Found' if pg_ok else '[ERROR] Row Not Found'}")
    print(f"SQL Server Target: {'[OK] Row Replicated' if mssql_ok else '[WARN] Row Not Replicated Yet'}")
    
    if all([debezium_ok, sink_ok, pg_ok, mssql_ok]):
        print("\n[OK] CDC Flow is working correctly!")
        print("  The new row has been successfully replicated from PostgreSQL to SQL Server.")
    else:
        print("\n[WARN] CDC Flow has issues. Check the details above.")
        if not debezium_ok:
            print("  - Debezium connector is not running")
        if not sink_ok:
            print("  - Sink connector is not running")
        if not pg_ok:
            print("  - Row not found in PostgreSQL source")
        if not mssql_ok:
            print("  - Row not replicated to SQL Server yet (may need more time)")

if __name__ == "__main__":
    main()


"""Diagnose why CDC is not sending data to Kafka and MS SQL."""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import pyodbc

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
DEBEZIUM_CONNECTOR = f"cdc-{PIPELINE_NAME}-pg-public"
SINK_CONNECTOR = f"sink-{PIPELINE_NAME}-mssql-dbo"

PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "user": "sa",
    "password": "Segmetriq@2025",
    "driver": "ODBC Driver 18 for SQL Server",
    "TrustServerCertificate": "yes",
    "Encrypt": "yes"
}

print("=" * 70)
print("CDC DIAGNOSIS - Why No Data to Kafka and MS SQL")
print("=" * 70)

# Step 1: Check Debezium Connector
print("\n1. DEBEZIUM CONNECTOR STATUS:")
print("-" * 70)
try:
    status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/status").json()
    connector_state = status.get('connector', {}).get('state')
    tasks = status.get('tasks', [])
    print(f"   State: {connector_state}")
    print(f"   Tasks: {len(tasks)}")
    for task in tasks:
        print(f"   Task {task.get('id')}: {task.get('state')}")
        if task.get('state') == 'FAILED':
            print(f"      Error: {task.get('trace', 'No trace')[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 2: Check Debezium Config
print("\n2. DEBEZIUM CONFIGURATION:")
print("-" * 70)
try:
    config = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/config").json()
    snapshot_mode = config.get('snapshot.mode', 'NOT SET')
    slot_name = config.get('slot.name', 'NOT SET')
    table_include = config.get('table.include.list', 'NOT SET')
    print(f"   Snapshot Mode: {snapshot_mode}")
    print(f"   Slot Name: {slot_name}")
    print(f"   Table Include: {table_include}")
    
    if snapshot_mode == 'never':
        print(f"   ⚠️  Snapshot mode is 'never' - only NEW changes will be captured")
    elif snapshot_mode == 'initial_only':
        print(f"   ✅ Snapshot mode is 'initial_only' - schema only, then CDC")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 3: Check Replication Slot
print("\n3. REPLICATION SLOT STATUS:")
print("-" * 70)
try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('''
        SELECT 
            slot_name,
            confirmed_flush_lsn AS cdc_lsn,
            pg_current_wal_lsn() AS current_lsn,
            pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
            active
        FROM pg_replication_slots
        WHERE slot_name = 'pg_to_mssql_projects_simple_slot'
    ''')
    slot = cursor.fetchone()
    
    if slot:
        print(f"   Slot: {slot['slot_name']}")
        print(f"   CDC LSN: {slot['cdc_lsn']}")
        print(f"   Current WAL LSN: {slot['current_lsn']}")
        print(f"   Lag: {slot['lag_bytes']} bytes ({slot['lag_bytes'] / 1024:.2f} KB)")
        print(f"   Active: {slot['active']}")
        
        if slot['lag_bytes'] > 0:
            print(f"   ⚠️  There is {slot['lag_bytes']} bytes of lag")
            print(f"   This means there ARE changes waiting to be processed!")
        else:
            print(f"   ✅ No lag - CDC is caught up")
            print(f"   This means either:")
            print(f"     - No new changes have been made")
            print(f"     - Or CDC has processed all changes")
    else:
        print(f"   ❌ Replication slot not found!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 4: Check PostgreSQL Table
print("\n4. POSTGRESQL TABLE STATUS:")
print("-" * 70)
try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT COUNT(*) as count FROM projects_simple")
    count = cursor.fetchone()['count']
    print(f"   Total rows: {count}")
    
    # Check REPLICA IDENTITY
    cursor.execute('''
        SELECT relreplident 
        FROM pg_class 
        WHERE relname = 'projects_simple'
    ''')
    replica_identity = cursor.fetchone()
    if replica_identity:
        ri = replica_identity['relreplident']
        ri_map = {'d': 'DEFAULT', 'n': 'NOTHING', 'f': 'FULL', 'i': 'INDEX'}
        print(f"   REPLICA IDENTITY: {ri_map.get(ri, 'UNKNOWN')}")
        if ri != 'f':
            print(f"   ⚠️  REPLICA IDENTITY is not FULL - UPDATE/DELETE may not work!")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 5: Check Sink Connector
print("\n5. SINK CONNECTOR STATUS:")
print("-" * 70)
try:
    status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/status").json()
    connector_state = status.get('connector', {}).get('state')
    tasks = status.get('tasks', [])
    print(f"   State: {connector_state}")
    print(f"   Tasks: {len(tasks)}")
    for task in tasks:
        print(f"   Task {task.get('id')}: {task.get('state')}")
        if task.get('state') == 'FAILED':
            print(f"      Error: {task.get('trace', 'No trace')[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 6: Check SQL Server
print("\n6. SQL SERVER TABLE STATUS:")
print("-" * 70)
try:
    conn_str = (
        f"DRIVER={MSSQL_CONFIG['driver']};"
        f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
        f"DATABASE={MSSQL_CONFIG['database']};"
        f"UID={MSSQL_CONFIG['user']};"
        f"PWD={MSSQL_CONFIG['password']};"
        f"TrustServerCertificate={MSSQL_CONFIG['TrustServerCertificate']};"
        f"Encrypt={MSSQL_CONFIG['Encrypt']};"
    )
    conn = pyodbc.connect(conn_str, timeout=10)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM dbo.projects_simple")
    count = cursor.fetchone()[0]
    print(f"   Total rows: {count}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 7: Recommendations
print("\n" + "=" * 70)
print("DIAGNOSIS & RECOMMENDATIONS:")
print("=" * 70)

print("\nPossible Issues:")
print("1. ⚠️  If replication slot has lag but no data in Kafka:")
print("   - Debezium might not be reading from the slot")
print("   - Check Kafka Connect worker logs")
print("   - Restart Debezium connector")

print("\n2. ⚠️  If no lag in replication slot:")
print("   - No new changes have been made to the table")
print("   - Make a test INSERT/UPDATE to trigger CDC")

print("\n3. ⚠️  If data in Kafka but not in SQL Server:")
print("   - Sink connector might have errors")
print("   - Check sink connector logs")
print("   - Verify SQL Server connection")

print("\n4. ⚠️  REPLICA IDENTITY not FULL:")
print("   - UPDATE/DELETE operations won't be captured")
print("   - Run: ALTER TABLE projects_simple REPLICA IDENTITY FULL;")

print("\n" + "=" * 70)
print("TEST: Make a change and check again")
print("=" * 70)
print("\nRun this in PostgreSQL:")
print("INSERT INTO projects_simple (project_id, project_name, department_id, employee_id, start_date, status)")
print("VALUES (999, 'CDC Test', 1, 1, '2024-01-01', 'ACTIVE');")
print("\nThen wait 10 seconds and check:")
print("1. Replication slot lag (should increase)")
print("2. Kafka topic (should have new message)")
print("3. SQL Server (should have new row)")



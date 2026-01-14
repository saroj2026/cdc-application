"""Monitor if Debezium is actually capturing changes by checking LSN position."""

import psycopg2
import time
import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-pg_to_mssql_projects_simple-pg-public"

print("="*80)
print("Monitoring Debezium Change Capture")
print("="*80)

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass"
    )
    cur = conn.cursor()
    
    # Get initial LSN position
    print("\n1. Getting initial replication slot LSN position...")
    cur.execute("""
        SELECT slot_name, confirmed_flush_lsn, restart_lsn,
               pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes
        FROM pg_replication_slots
        WHERE slot_name = 'pg_to_mssql_projects_simple_slot'
    """)
    initial = cur.fetchone()
    
    if initial:
        print(f"   Slot: {initial[0]}")
        print(f"   Confirmed flush LSN: {initial[1]}")
        print(f"   Restart LSN: {initial[2]}")
        print(f"   Lag: {initial[3]} bytes")
        initial_lsn = initial[1]
    else:
        print("   [ERROR] Replication slot not found!")
        exit(1)
    
    # Make a test change
    print("\n2. Making a test change in PostgreSQL...")
    # First check if row exists
    cur.execute("SELECT project_id FROM public.projects_simple WHERE project_id = 9999")
    if cur.fetchone():
        print("   Test row already exists, deleting it first...")
        cur.execute("DELETE FROM public.projects_simple WHERE project_id = 9999")
        conn.commit()
        time.sleep(1)
    
    cur.execute("""
        INSERT INTO public.projects_simple 
        (project_id, project_name, department_id, employee_id, start_date, end_date, status)
        VALUES (9999, 'LSN Test', 200, 101, CURRENT_DATE, NULL, 'ACTIVE')
    """)
    conn.commit()
    print("   [OK] Inserted test row (project_id=9999)")
    
    # Wait a bit
    print("\n3. Waiting 5 seconds for Debezium to process...")
    time.sleep(5)
    
    # Check LSN position again
    print("\n4. Checking LSN position after change...")
    cur.execute("""
        SELECT slot_name, confirmed_flush_lsn, restart_lsn,
               pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) as lag_bytes
        FROM pg_replication_slots
        WHERE slot_name = 'pg_to_mssql_projects_simple_slot'
    """)
    after = cur.fetchone()
    
    if after:
        print(f"   Confirmed flush LSN: {after[1]}")
        print(f"   Restart LSN: {after[2]}")
        print(f"   Lag: {after[3]} bytes")
        
        # Compare LSNs
        if after[1] and initial_lsn:
            if after[1] != initial_lsn:
                print("\n   [OK] LSN position ADVANCED - Debezium is capturing changes!")
                print("   This means Debezium is reading from the WAL")
            else:
                print("\n   [ERROR] LSN position did NOT advance")
                print("   This means Debezium is NOT capturing changes")
                print("   Possible issues:")
                print("     - Connector is not actually reading from WAL")
                print("     - Publication is not configured correctly")
                print("     - Table changes are not being logged")
        else:
            print("\n   [WARN] Could not compare LSN positions")
    
    # Check current WAL position
    cur.execute("SELECT pg_current_wal_lsn()")
    current_wal = cur.fetchone()[0]
    print(f"\n   Current WAL LSN: {current_wal}")
    
    # Check if table has REPLICA IDENTITY set
    print("\n5. Checking table replication settings...")
    cur.execute("""
        SELECT relreplident
        FROM pg_class
        WHERE relname = 'projects_simple'
    """)
    repl_ident = cur.fetchone()[0]
    repl_ident_map = {'d': 'default', 'n': 'nothing', 'f': 'full', 'i': 'index'}
    print(f"   REPLICA IDENTITY: {repl_ident_map.get(repl_ident, repl_ident)}")
    
    if repl_ident != 'f':
        print("   [WARN] REPLICA IDENTITY is not FULL")
        print("   For UPDATE/DELETE operations, you need:")
        print("   ALTER TABLE public.projects_simple REPLICA IDENTITY FULL;")
    
    cur.close()
    conn.close()
    
    # Check Debezium connector status
    print("\n6. Checking Debezium connector status...")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status", timeout=10)
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state', 'UNKNOWN') if tasks else 'UNKNOWN'
        
        print(f"   Connector: {connector_state}")
        print(f"   Task: {task_state}")
        
        if connector_state == 'RUNNING' and task_state == 'RUNNING':
            print("   [OK] Connector is running")
        else:
            print("   [ERROR] Connector is not fully operational")
    
    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    print("If LSN advanced: Debezium is capturing changes, check Kafka topic")
    print("If LSN did NOT advance: Debezium is not capturing, check connector logs")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


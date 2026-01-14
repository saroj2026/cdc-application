"""Debug Debezium connector configuration and check for issues."""

import requests
import json
import psycopg2

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-pg_to_mssql_projects_simple-pg-public"

print("="*80)
print("Debezium Connector Debug")
print("="*80)

try:
    # Get connector config
    print("\n1. Connector Configuration:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}", timeout=10)
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        
        print(f"   Connector class: {config.get('connector.class')}")
        print(f"   Database hostname: {config.get('database.hostname')}")
        print(f"   Database port: {config.get('database.port')}")
        print(f"   Database name: {config.get('database.dbname')}")
        print(f"   Database user: {config.get('database.user')}")
        print(f"   Slot name: {config.get('slot.name')}")
        print(f"   Plugin name: {config.get('plugin.name')}")
        print(f"   Topic prefix: {config.get('topic.prefix')}")
        print(f"   Table include list: {config.get('table.include.list', 'NOT SET')}")
        print(f"   Schema include list: {config.get('schema.include.list', 'NOT SET')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode')}")
        print(f"   Publication name: {config.get('publication.name', 'NOT SET')}")
        print(f"   Publication autocreate: {config.get('publication.autocreate.mode', 'NOT SET')}")
    
    # Get connector status
    print("\n2. Connector Status:")
    response = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status", timeout=10)
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
    
    # Check PostgreSQL publication
    print("\n3. Checking PostgreSQL Publication:")
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass"
    )
    cur = conn.cursor()
    
    # Check publications
    cur.execute("""
        SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete
        FROM pg_publication
        WHERE pubname LIKE '%pg_to_mssql%' OR pubname = 'dbz_publication'
    """)
    pubs = cur.fetchall()
    
    if pubs:
        print("   Found publications:")
        for pub in pubs:
            print(f"     - {pub[0]} (all_tables: {pub[1]}, insert: {pub[2]}, update: {pub[3]}, delete: {pub[4]})")
    else:
        print("   [WARN] No publication found!")
        print("   Debezium needs a publication to capture changes")
    
    # Check if table is in publication
    cur.execute("""
        SELECT pt.schemaname, pt.tablename
        FROM pg_publication_tables pt
        JOIN pg_publication p ON pt.pubname = p.pubname
        WHERE pt.tablename = 'projects_simple'
    """)
    tables = cur.fetchall()
    
    if tables:
        print("\n   Tables in publications:")
        for table in tables:
            print(f"     - {table[0]}.{table[1]}")
    else:
        print("\n   [ERROR] projects_simple table is NOT in any publication!")
        print("   This is why changes are not being captured!")
    
    # Check replication slot
    print("\n4. Checking Replication Slot:")
    slot_name = config.get('slot.name', 'unknown')
    cur.execute("""
        SELECT slot_name, active, confirmed_flush_lsn, restart_lsn
        FROM pg_replication_slots
        WHERE slot_name = %s
    """, (slot_name,))
    slot = cur.fetchone()
    
    if slot:
        print(f"   Slot: {slot[0]}")
        print(f"   Active: {slot[1]}")
        print(f"   Confirmed flush LSN: {slot[2]}")
        print(f"   Restart LSN: {slot[3]}")
    else:
        print(f"   [ERROR] Slot '{slot_name}' not found!")
    
    cur.close()
    conn.close()
    
    # Recommendations
    print("\n" + "="*80)
    print("Recommendations")
    print("="*80)
    
    if not tables:
        print("\n[CRITICAL] The table is not in a publication!")
        print("Solution: Create or update the publication to include the table:")
        print("  CREATE PUBLICATION dbz_publication FOR TABLE public.projects_simple;")
        print("  Or update Debezium config to use publication.autocreate.mode=all_tables")
    
    print("\nTo verify CDC is working:")
    print("  1. Ensure table is in publication")
    print("  2. Make a NEW change: INSERT INTO public.projects_simple VALUES (...)")
    print("  3. Check Kafka topic for messages")
    print("  4. Check SQL Server for replicated row")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


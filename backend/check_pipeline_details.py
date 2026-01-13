"""Check detailed pipeline information from database."""

import psycopg2
import json

print("=" * 80)
print("Checking Pipeline Details from Database")
print("=" * 80)

pipeline_id = "79ba9d9e-5561-456d-8115-1d70466dfb67"

try:
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        user="cdc_user",
        password="cdc_pass",
        database="cdctest"
    )
    cur = conn.cursor()
    
    # Get pipeline details
    print(f"\n1. Getting pipeline details for: {pipeline_id}...")
    cur.execute("""
        SELECT 
            id, name, mode, enable_full_load, full_load_status, 
            full_load_lsn, full_load_completed_at,
            cdc_status, status,
            source_connection_id, target_connection_id,
            source_database, source_schema, source_tables,
            target_database, target_schema, target_tables
        FROM pipelines 
        WHERE id = %s;
    """, (pipeline_id,))
    
    row = cur.fetchone()
    if row:
        print(f"   [OK] Pipeline found: {row[1]}")
        print(f"   Mode: {row[2]}")
        print(f"   Enable Full Load: {row[3]}")
        print(f"   Full Load Status: {row[4]}")
        print(f"   Full Load LSN: {row[5]}")
        print(f"   Full Load Completed At: {row[6]}")
        print(f"   CDC Status: {row[7]}")
        print(f"   Status: {row[8]}")
        print(f"   Source Connection: {row[9]}")
        print(f"   Target Connection: {row[10]}")
        print(f"   Source: {row[11]}.{row[12]}.{row[13]}")
        print(f"   Target: {row[14]}.{row[15]}.{row[16]}")
        
        # Check connections
        print(f"\n2. Checking source connection...")
        cur.execute("""
            SELECT id, name, database_type, host, port, database, 
                   additional_config
            FROM connections 
            WHERE id = %s;
        """, (row[9],))
        
        source_conn = cur.fetchone()
        if source_conn:
            print(f"   [OK] Source: {source_conn[1]} ({source_conn[2]})")
            print(f"   Host: {source_conn[3]}:{source_conn[4]}")
            print(f"   Database: {source_conn[5]}")
        
        print(f"\n3. Checking target connection...")
        cur.execute("""
            SELECT id, name, database_type, host, port, database, 
                   additional_config
            FROM connections 
            WHERE id = %s;
        """, (row[10],))
        
        target_conn = cur.fetchone()
        if target_conn:
            print(f"   [OK] Target: {target_conn[1]} ({target_conn[2]})")
            print(f"   Host: {target_conn[3]}:{target_conn[4]}")
            print(f"   Database: {target_conn[5]}")
            print(f"   Additional Config: {target_conn[6]}")
            
            if target_conn[2] == 'sqlserver':
                if not target_conn[6] or not target_conn[6].get('trust_server_certificate'):
                    print(f"   ⚠️  Missing trust_server_certificate in additional_config!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   [ERROR] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

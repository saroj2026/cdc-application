"""Check pipeline details from PostgreSQL database."""

import psycopg2
import json
from datetime import datetime

# Database connection
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Pipeline Database Check")
print("=" * 70)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get pipeline details
    pipeline_id = "ae7bb432-2fa8-48eb-90a0-d6bb4c164441"
    
    print(f"\n1. Pipeline Details (ID: {pipeline_id}):")
    cursor.execute("""
        SELECT 
            id, name, status, mode, 
            source_connection_id, target_connection_id,
            source_database, source_schema, source_tables,
            target_database, target_schema, target_tables,
            full_load_status, cdc_status,
            debezium_connector_name, sink_connector_name,
            kafka_topics, auto_create_target,
            created_at, updated_at
        FROM pipelines
        WHERE id = %s
    """, (pipeline_id,))
    
    pipeline = cursor.fetchone()
    if pipeline:
        print(f"   Name: {pipeline[1]}")
        print(f"   Status: {pipeline[2]}")
        print(f"   Mode: {pipeline[3]}")
        print(f"   Full Load Status: {pipeline[12]}")
        print(f"   CDC Status: {pipeline[13]}")
        print(f"   Debezium Connector: {pipeline[14] or 'N/A'}")
        print(f"   Sink Connector: {pipeline[15] or 'N/A'}")
        print(f"   Kafka Topics: {pipeline[16] or []}")
        print(f"   Source: {pipeline[6]}.{pipeline[7]} (Tables: {pipeline[8]})")
        print(f"   Target: {pipeline[9]}.{pipeline[10]} (Tables: {pipeline[11]})")
        print(f"   Created: {pipeline[18]}")
        print(f"   Updated: {pipeline[19]}")
    else:
        print("   Pipeline not found!")
    
    # Get connection details
    print(f"\n2. Connection Details:")
    if pipeline:
        source_conn_id = pipeline[4]
        target_conn_id = pipeline[5]
        
        # Source connection
        cursor.execute("""
            SELECT id, name, database_type, host, port, database, username, schema, additional_config
            FROM connections
            WHERE id = %s
        """, (source_conn_id,))
        source_conn = cursor.fetchone()
        if source_conn:
            print(f"   Source Connection: {source_conn[1]} ({source_conn[2]})")
            print(f"      Host: {source_conn[3]}:{source_conn[4]}")
            print(f"      Database: {source_conn[5]}, Schema: {source_conn[7]}")
        
        # Target connection
        cursor.execute("""
            SELECT id, name, database_type, host, port, database, username, schema, additional_config
            FROM connections
            WHERE id = %s
        """, (target_conn_id,))
        target_conn = cursor.fetchone()
        if target_conn:
            print(f"   Target Connection: {target_conn[1]} ({target_conn[2]})")
            print(f"      Host: {target_conn[3] or 'N/A'}")
            print(f"      Database: {target_conn[5]}, Schema: {target_conn[7]}")
            if target_conn[8]:  # additional_config
                config = target_conn[8] if isinstance(target_conn[8], dict) else json.loads(target_conn[8])
                print(f"      Account: {config.get('account', 'N/A')}")
                print(f"      Warehouse: {config.get('warehouse', 'N/A')}")
                print(f"      Role: {config.get('role', 'N/A')}")
    
    # List all pipelines
    print(f"\n3. All Pipelines:")
    cursor.execute("""
        SELECT id, name, status, mode, full_load_status, cdc_status, 
               debezium_connector_name, sink_connector_name
        FROM pipelines
        ORDER BY created_at DESC
        LIMIT 10
    """)
    pipelines = cursor.fetchall()
    for p in pipelines:
        print(f"   {p[1]}: Status={p[2]}, Mode={p[3]}, FullLoad={p[4]}, CDC={p[5]}")
        print(f"      Debezium: {p[6] or 'N/A'}, Sink: {p[7] or 'N/A'}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()



#!/usr/bin/env python3
"""Check Kafka messages and Snowflake table to diagnose CDC flow."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import snowflake.connector
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING KAFKA MESSAGES AND SNOWFLAKE TABLE")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
topic_name = "oracle_sf_p.CDC_USER.TEST"
sink_connector = "sink-oracle_sf_p-snow-public"

# Get Snowflake connection
db = next(get_db())
try:
    pipeline = db.query(PipelineModel).filter_by(name="oracle_sf_p").first()
    snowflake_conn_model = db.query(ConnectionModel).filter_by(id=pipeline.target_connection_id).first()
    snowflake_config = snowflake_conn_model.additional_config or {}
    
    sf_account = snowflake_config.get('account') or snowflake_conn_model.host
    sf_user = snowflake_conn_model.username
    sf_password = snowflake_conn_model.password
    sf_warehouse = snowflake_config.get('warehouse')
    sf_database = snowflake_config.get('database') or 'seg'
    sf_schema = snowflake_config.get('schema') or 'public'
    sf_role = snowflake_config.get('role')
    
    print("\n1. Checking Sink Connector Consumer Group Offsets...")
    print("-" * 70)
    
    # Try to get task status which includes offset info
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        tasks = status.get('tasks', [])
        for task in tasks:
            print(f"   Task {task.get('id')}: {task.get('state')}")
            # Check if there's offset info
            worker_id = task.get('worker_id', '')
            if worker_id:
                print(f"   Worker: {worker_id}")
    
    print("\n2. Checking Snowflake Table Structure...")
    print("-" * 70)
    
    # Connect to Snowflake
    sf_conn = snowflake.connector.connect(
        account=sf_account,
        user=sf_user,
        password=sf_password,
        warehouse=sf_warehouse,
        database=sf_database,
        schema=sf_schema,
        role=sf_role
    )
    
    sf_cursor = sf_conn.cursor()
    
    # Check table structure
    sf_cursor.execute(f"DESC TABLE {sf_database}.{sf_schema}.TEST")
    columns = sf_cursor.fetchall()
    
    print(f"   Table columns:")
    has_record_content = False
    has_record_metadata = False
    
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        print(f"     {col_name}: {col_type}")
        if col_name == 'RECORD_CONTENT':
            has_record_content = True
        if col_name == 'RECORD_METADATA':
            has_record_metadata = True
    
    if not has_record_content or not has_record_metadata:
        print(f"\n   ⚠ WARNING: Missing required columns!")
        print(f"     RECORD_CONTENT: {'✅' if has_record_content else '❌'}")
        print(f"     RECORD_METADATA: {'✅' if has_record_metadata else '❌'}")
    
    print(f"\n3. Checking Recent Records in Snowflake...")
    print("-" * 70)
    
    # Get recent records
    sf_cursor.execute(f"""
        SELECT 
            RECORD_METADATA:CreateTime as create_time,
            RECORD_CONTENT:op as operation,
            RECORD_CONTENT:after:id as id_after,
            RECORD_CONTENT:after:name as name_after
        FROM {sf_database}.{sf_schema}.TEST
        ORDER BY RECORD_METADATA:CreateTime DESC
        LIMIT 10
    """)
    
    recent_records = sf_cursor.fetchall()
    
    if recent_records:
        print(f"   Found {len(recent_records)} recent records:")
        for idx, row in enumerate(recent_records[:5], 1):
            print(f"     {idx}. Operation: {row[1]}, ID: {row[2]}, Name: {row[3]}")
    else:
        print(f"   ⚠ No recent records found")
    
    print(f"\n4. Checking Total Record Count...")
    print("-" * 70)
    
    sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.TEST")
    total_count = sf_cursor.fetchone()[0]
    print(f"   Total records: {total_count}")
    
    print(f"\n5. Checking for CDC Operations (c, u, d)...")
    print("-" * 70)
    
    # Count by operation type
    sf_cursor.execute(f"""
        SELECT 
            RECORD_CONTENT:op as operation,
            COUNT(*) as count
        FROM {sf_database}.{sf_schema}.TEST
        WHERE RECORD_CONTENT:op IN ('c', 'u', 'd', 'r')
        GROUP BY RECORD_CONTENT:op
        ORDER BY operation
    """)
    
    op_counts = sf_cursor.fetchall()
    
    if op_counts:
        print(f"   Operation counts:")
        for op, count in op_counts:
            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ/Snapshot'}.get(op, op)
            print(f"     {op_name} ({op}): {count}")
    else:
        print(f"   ⚠ No operation types found (may all be 'r' for snapshot)")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("  If no CDC events (c/u/d) found:")
print("    1. Check Kafka topic has new messages")
print("    2. Check sink connector is consuming (LAG should be 0)")
print("    3. Wait for buffer flush (60 seconds or 3000 records)")
print("    4. Check sink connector logs for errors")
print("=" * 70)


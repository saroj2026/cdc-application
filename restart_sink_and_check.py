#!/usr/bin/env python3
"""Restart sink connector to force buffer flush and check for new records."""

import requests
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("RESTARTING SINK CONNECTOR TO FORCE BUFFER FLUSH")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector = "sink-oracle_sf_p-snow-public"
test_id = 73032

print("\n1. Restarting Sink Connector...")
print("-" * 70)

try:
    restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector}/restart", timeout=10)
    if restart_r.status_code == 204:
        print(f"   ✅ Connector restart initiated")
        print(f"   Waiting 30 seconds for restart and buffer flush...")
        time.sleep(30)
    else:
        print(f"   ⚠ Restart response: {restart_r.status_code} - {restart_r.text}")
except Exception as e:
    print(f"   ❌ Error restarting: {e}")

print("\n2. Checking Connector Status After Restart...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        print(f"   Connector state: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'N/A')
            print(f"   Task {task.get('id')}: {task_state}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Checking Snowflake for New Records...")
print("-" * 70)

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
    
    # Get total count
    sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.TEST")
    total = sf_cursor.fetchone()[0]
    print(f"   Total records: {total}")
    
    # Get most recent records with full details
    query = f"""
    SELECT 
        RECORD_CONTENT,
        RECORD_METADATA:CreateTime as create_time
    FROM {sf_database}.{sf_schema}.TEST
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 10
    """
    
    sf_cursor.execute(query)
    recent = sf_cursor.fetchall()
    
    if recent:
        print(f"\n   Most recent 10 records:")
        import json
        from datetime import datetime
        
        for idx, row in enumerate(recent, 1):
            record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            create_time = row[1]
            
            if isinstance(record_content, dict):
                operation = record_content.get('op', '?')
                op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(operation, operation)
                
                # Try to get ID
                id_value = None
                if 'after' in record_content and record_content['after']:
                    after = record_content['after']
                    id_value = after.get('ID') or after.get('id')
                elif 'before' in record_content and record_content['before']:
                    before = record_content['before']
                    id_value = before.get('ID') or before.get('id')
                
                # Format timestamp
                time_str = "N/A"
                if create_time:
                    try:
                        dt = datetime.fromtimestamp(create_time / 1000)
                        time_ago = (datetime.now() - dt).total_seconds()
                        time_str = f"{time_ago:.0f}s ago"
                    except:
                        time_str = str(create_time)
                
                print(f"     {idx}. {op_name} - ID: {id_value} - {time_str}")
                
                # Check if this is our test ID (might be encoded)
                if id_value:
                    # Check if it's a dict (Oracle NUMBER encoding)
                    if isinstance(id_value, dict) and 'value' in id_value:
                        # This is base64 encoded, hard to match directly
                        pass
                    elif isinstance(id_value, (int, str)):
                        try:
                            if int(id_value) == test_id:
                                print(f"        ✅✅✅ THIS IS TEST ID {test_id}!")
                        except:
                            pass
    
    # Check for CDC operations count
    sf_cursor.execute(f"""
        SELECT 
            RECORD_CONTENT:op as operation,
            COUNT(*) as count
        FROM {sf_database}.{sf_schema}.TEST
        WHERE RECORD_CONTENT:op IN ('c', 'u', 'd')
        GROUP BY RECORD_CONTENT:op
    """)
    cdc_ops = sf_cursor.fetchall()
    
    if cdc_ops:
        print(f"\n   CDC operations summary:")
        for op, count in cdc_ops:
            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE'}.get(op, op)
            print(f"     {op_name} ({op}): {count}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
print("SUMMARY:")
print("  If test ID 73032 still not found:")
print("  1. Check Kafka topic to verify messages are there")
print("  2. Check sink connector logs for errors")
print("  3. Verify the INSERT/UPDATE/DELETE actually happened in Oracle")
print("  4. Check if there are any schema mismatches")
print("=" * 70)


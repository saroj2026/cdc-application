#!/usr/bin/env python3
"""Investigate why test ID 73032 is not appearing in Snowflake after 60+ seconds."""

import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("INVESTIGATING MISSING RECORDS - TEST ID 73032")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
topic_name = "oracle_sf_p.CDC_USER.TEST"
sink_connector = "sink-oracle_sf_p-snow-public"
test_id = 73032

print("\n1. Checking Sink Connector Status...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        
        print(f"   Connector state: {connector_state}")
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            worker_id = task.get('worker_id', 'N/A')
            print(f"   Task {task_id}: {task_state} on {worker_id}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"\n   ⚠ TASK FAILED - Error:")
                    print(f"   {trace[:1000]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking Sink Connector Configuration...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Buffer flush time: {config.get('buffer.flush.time', 'N/A')} seconds")
        print(f"   Buffer count: {config.get('buffer.count.records', 'N/A')} records")
        
        # Check if topic matches
        configured_topics = config.get('topics', '')
        if topic_name not in configured_topics:
            print(f"\n   ⚠ WARNING: Topic '{topic_name}' not in configured topics!")
            print(f"   Configured: {configured_topics}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Checking Source Connector (Debezium) Status...")
print("-" * 70)

source_connector = "cdc-oracle_sf_p-ora-cdc_user"
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{source_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        
        print(f"   Connector state: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'N/A')
            print(f"   Task {task.get('id')}: {task_state}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"     ⚠ Error: {trace[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n4. Checking Source Connector Topics...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{source_connector}/topics", timeout=5)
    if r.status_code == 200:
        topics = r.json()
        print(f"   Topics: {topics}")
        
        if source_connector in topics:
            connector_topics = topics[source_connector].get('topics', [])
            if topic_name in connector_topics:
                print(f"   ✅ Topic '{topic_name}' is being produced by source connector")
            else:
                print(f"   ⚠ Topic '{topic_name}' not in source connector topics")
                print(f"   Available topics: {connector_topics}")
except Exception as e:
    print(f"   ⚠ Error getting topics: {e}")

print("\n5. Checking Snowflake for Recent Records...")
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
    
    # Get most recent records by timestamp
    query = f"""
    SELECT 
        RECORD_METADATA:CreateTime as create_time,
        RECORD_CONTENT:op as operation
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_METADATA:CreateTime IS NOT NULL
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 5
    """
    
    sf_cursor.execute(query)
    recent = sf_cursor.fetchall()
    
    if recent:
        print(f"\n   Most recent records:")
        for idx, row in enumerate(recent, 1):
            create_time = row[0]
            operation = row[1]
            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(operation, operation)
            
            # Convert timestamp to readable format
            if create_time:
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(create_time / 1000)
                    time_ago = (datetime.now() - dt).total_seconds()
                    print(f"     {idx}. {op_name} - {time_ago:.0f} seconds ago ({dt.strftime('%H:%M:%S')})")
                except:
                    print(f"     {idx}. {op_name} - Timestamp: {create_time}")
    else:
        print(f"   ⚠ No recent records with timestamps found")
    
    # Check for CDC operations
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
        print(f"\n   CDC operations found:")
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

print("\n6. Recommendations...")
print("-" * 70)
print("   If records are still not appearing:")
print("   1. Check Kafka topic message count (use Kafka UI or kafka-console-consumer)")
print("   2. Check sink connector logs for errors")
print("   3. Verify sink connector is consuming from the correct topic")
print("   4. Check if buffer flush is actually happening")
print("   5. Try restarting the sink connector to force a flush")

print("\n" + "=" * 70)


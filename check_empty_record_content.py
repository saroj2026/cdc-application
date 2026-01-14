#!/usr/bin/env python3
"""Check why RECORD_CONTENT is empty and fix the transform configuration."""

import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("INVESTIGATING EMPTY RECORD_CONTENT")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Checking Sink Connector Transform Configuration...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        
        transforms = config.get('transforms', 'N/A')
        transform_type = config.get('transforms.unwrap.type', 'N/A')
        drop_tombstones = config.get('transforms.unwrap.drop.tombstones', 'N/A')
        delete_handling = config.get('transforms.unwrap.delete.handling.mode', 'N/A')
        
        print(f"   Transforms: {transforms}")
        print(f"   Transform type: {transform_type}")
        print(f"   Drop tombstones: {drop_tombstones}")
        print(f"   Delete handling mode: {delete_handling}")
        
        print(f"\n   ⚠ ISSUE DETECTED:")
        print(f"   The ExtractNewRecordState transform extracts 'after' field.")
        print(f"   For DELETE operations, 'after' is null, so RECORD_CONTENT becomes empty.")
        print(f"   For UPDATE operations, it only shows 'after', losing 'before' data.")
        print(f"   ")
        print(f"   SOLUTION: Remove the transform to preserve full Debezium envelope")
        print(f"   This will keep 'op', 'after', 'before' fields in RECORD_CONTENT")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking Snowflake Records...")
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
    
    # Check for empty RECORD_CONTENT
    query = f"""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN RECORD_CONTENT IS NULL OR RECORD_CONTENT = '{{}}' THEN 1 ELSE 0 END) as empty_count
    FROM {sf_database}.{sf_schema}.TEST
    """
    
    sf_cursor.execute(query)
    result = sf_cursor.fetchone()
    total = result[0]
    empty_count = result[1]
    
    print(f"   Total records: {total}")
    print(f"   Empty RECORD_CONTENT: {empty_count}")
    print(f"   Records with data: {total - empty_count}")
    
    # Check sample of records with different structures
    query2 = f"""
    SELECT RECORD_CONTENT
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_CONTENT IS NOT NULL AND RECORD_CONTENT != '{{}}'
    LIMIT 5
    """
    
    sf_cursor.execute(query2)
    samples = sf_cursor.fetchall()
    
    print(f"\n   Sample records with data:")
    for idx, row in enumerate(samples, 1):
        record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        if isinstance(record_content, dict):
            keys = list(record_content.keys())
            print(f"     {idx}. Keys: {keys}")
            if 'op' in keys:
                print(f"        Operation: {record_content['op']}")
            if 'after' in keys:
                after = record_content['after']
                print(f"        After: {'null' if after is None else 'has data'}")
            if 'before' in keys:
                before = record_content['before']
                print(f"        Before: {'null' if before is None else 'has data'}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("  Remove ExtractNewRecordState transform to preserve full Debezium envelope.")
print("  This will keep 'op', 'after', 'before' fields for all operations.")
print("=" * 70)


#!/usr/bin/env python3
"""Check raw RECORD_CONTENT structure to understand the data format."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING RAW RECORD_CONTENT STRUCTURE")
print("=" * 70)

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
    
    # Get the most recent record (by row number, not timestamp)
    # Since we can't query by timestamp properly, get the last few rows
    query = f"""
    SELECT 
        RECORD_CONTENT,
        RECORD_METADATA
    FROM {sf_database}.{sf_schema}.TEST
    ORDER BY RECORD_METADATA:CreateTime DESC NULLS LAST
    LIMIT 5
    """
    
    sf_cursor.execute(query)
    results = sf_cursor.fetchall()
    
    print(f"\n1. Latest 5 records (raw structure):")
    print("-" * 70)
    
    for idx, row in enumerate(results, 1):
        record_content_raw = row[0]
        record_metadata_raw = row[1]
        
        print(f"\n   Record {idx}:")
        print(f"   RECORD_CONTENT type: {type(record_content_raw)}")
        print(f"   RECORD_METADATA type: {type(record_metadata_raw)}")
        
        # Try to parse as JSON if it's a string
        if isinstance(record_content_raw, str):
            try:
                record_content = json.loads(record_content_raw)
                print(f"   RECORD_CONTENT (parsed): {json.dumps(record_content, indent=2)[:500]}")
            except:
                print(f"   RECORD_CONTENT (string): {record_content_raw[:200]}")
        elif isinstance(record_content_raw, dict):
            print(f"   RECORD_CONTENT keys: {list(record_content_raw.keys())}")
            if 'op' in record_content_raw:
                print(f"   Operation: {record_content_raw['op']}")
            if 'after' in record_content_raw:
                after = record_content_raw['after']
                print(f"   After keys: {list(after.keys()) if isinstance(after, dict) else 'N/A'}")
                if isinstance(after, dict):
                    print(f"   After data: {json.dumps(after, indent=4)[:300]}")
            if 'before' in record_content_raw:
                before = record_content_raw['before']
                print(f"   Before keys: {list(before.keys()) if isinstance(before, dict) else 'N/A'}")
        else:
            print(f"   RECORD_CONTENT: {str(record_content_raw)[:200]}")
    
    # Also try a simpler query to get total count and check if we can access fields
    print(f"\n2. Testing field access...")
    print("-" * 70)
    
    # Try different query approaches
    test_queries = [
        ("Direct field access", f"SELECT RECORD_CONTENT:op FROM {sf_database}.{sf_schema}.TEST LIMIT 1"),
        ("Using GET", f"SELECT GET(RECORD_CONTENT, 'op') FROM {sf_database}.{sf_schema}.TEST LIMIT 1"),
        ("Using PARSE_JSON", f"SELECT PARSE_JSON(RECORD_CONTENT) FROM {sf_database}.{sf_schema}.TEST LIMIT 1"),
    ]
    
    for query_name, query_sql in test_queries:
        try:
            sf_cursor.execute(query_sql)
            result = sf_cursor.fetchone()
            print(f"   {query_name}: {result[0] if result else 'None'}")
        except Exception as e:
            print(f"   {query_name}: Error - {str(e)[:100]}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)


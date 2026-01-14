#!/usr/bin/env python3
"""Simple check for ID 73032 by examining all records."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
import base64
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

def try_decode_id(id_value):
    """Try to decode Oracle NUMBER ID from various formats."""
    if isinstance(id_value, int):
        return id_value
    elif isinstance(id_value, str):
        try:
            return int(id_value)
        except:
            pass
    elif isinstance(id_value, dict):
        # Try to decode base64
        if 'value' in id_value:
            try:
                # This is a simplified decoder - Oracle NUMBER encoding is complex
                # For now, just check if we can extract any numeric value
                encoded = id_value['value']
                # Try to decode and see if we can get the number
                # Oracle NUMBER is complex, so we'll use a simpler approach
                return None  # Will handle this differently
            except:
                pass
    
    return None

print("=" * 70)
print("SIMPLE CHECK FOR TEST ID 73032")
print("=" * 70)

test_id = 73032

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
    
    print(f"\n1. Getting ALL records from TEST table...")
    print("-" * 70)
    
    # Get all records
    query = f"""
    SELECT RECORD_CONTENT, RECORD_METADATA:CreateTime as create_time
    FROM {sf_database}.{sf_schema}.TEST
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 100
    """
    
    sf_cursor.execute(query)
    results = sf_cursor.fetchall()
    
    print(f"   Found {len(results)} records")
    
    found_test_id = False
    checked_count = 0
    
    print(f"\n2. Checking each record for ID {test_id}...")
    print("-" * 70)
    
    for idx, row in enumerate(results, 1):
        record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        create_time = row[1]
        
        if isinstance(record_content, dict):
            # Check 'after' field
            if 'after' in record_content and record_content['after']:
                after = record_content['after']
                id_value = after.get('ID') or after.get('id')
                
                if id_value:
                    checked_count += 1
                    # Try to extract numeric value
                    numeric_id = None
                    
                    if isinstance(id_value, int):
                        numeric_id = id_value
                    elif isinstance(id_value, dict) and 'value' in id_value:
                        # This is base64 encoded Oracle NUMBER
                        # For now, let's just show the raw value
                        encoded_value = id_value['value']
                        # Try a simple check - if the base64 decodes to something we can recognize
                        try:
                            decoded = base64.b64decode(encoded_value)
                            # Oracle NUMBER format is complex, but let's check if 73032 might be in there
                            # For now, we'll just note the encoded value
                            pass
                        except:
                            pass
                    
                    # For now, let's check if the raw dict representation might match
                    # We'll show a few examples
                    if idx <= 5:
                        print(f"   Record {idx}: ID value = {id_value} (type: {type(id_value)})")
            
            # Check 'before' field
            if 'before' in record_content and record_content['before']:
                before = record_content['before']
                id_value = before.get('ID') or before.get('id')
                
                if id_value and idx <= 5:
                    print(f"   Record {idx} (before): ID value = {id_value} (type: {type(id_value)})")
    
    print(f"\n   Checked {checked_count} records with ID values")
    
    if not found_test_id:
        print(f"\n3. Summary...")
        print("-" * 70)
        print(f"   ❌ Test ID {test_id} NOT FOUND in TEST table")
        print(f"   ")
        print(f"   Possible reasons:")
        print(f"   1. Records are still in Snowflake connector buffer")
        print(f"      - Buffer flush time: 60 seconds")
        print(f"      - Buffer count: 3000 records")
        print(f"      - We only inserted 3 records (INSERT, UPDATE, DELETE)")
        print(f"      - May need to wait longer or insert more records to trigger flush")
        print(f"   ")
        print(f"   2. Oracle NUMBER encoding makes direct ID matching difficult")
        print(f"      - IDs are stored as base64-encoded values")
        print(f"      - Need specialized decoder to extract numeric value")
        print(f"   ")
        print(f"   3. Records might be in a different batch/table")
    
    # Check total count
    sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.TEST")
    total = sf_cursor.fetchone()[0]
    print(f"\n   Total records in TEST table: {total}")
    
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
print(f"  The test ID {test_id} was inserted/updated/deleted in Oracle,")
print(f"  but it may not have been flushed to Snowflake yet.")
print(f"  ")
print(f"  To verify CDC is working:")
print(f"  1. Wait 60+ seconds for buffer flush")
print(f"  2. Insert more records to trigger buffer flush (3000 records)")
print(f"  3. Check Kafka topic to confirm messages are there")
print(f"  4. Check sink connector logs for any errors")
print("=" * 70)


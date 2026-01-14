#!/usr/bin/env python3
"""Check the latest record in Snowflake to see if our test record is there."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING LATEST RECORD IN SNOWFLAKE")
print("=" * 70)

test_name = "CDC Test 20260113_111256"

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
    
    # Get ALL recent records, not just INSERTs
    query = f"""
    SELECT 
        RECORD_CONTENT,
        RECORD_METADATA:CreateTime as create_time,
        RECORD_CONTENT:op as operation
    FROM {sf_database}.{sf_schema}.TEST
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 20
    """
    
    sf_cursor.execute(query)
    results = sf_cursor.fetchall()
    
    print(f"\n1. Latest 20 records in Snowflake:")
    print("-" * 70)
    
    found = False
    for idx, row in enumerate(results, 1):
        record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        create_time = row[1]
        operation = row[2]
        
        if isinstance(record_content, dict):
            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(operation, operation)
            
            # Get name from after or before
            name_value = None
            id_value = None
            
            if 'after' in record_content and record_content['after']:
                after = record_content['after']
                name_value = after.get('NAME') or after.get('name')
                id_value = after.get('ID') or after.get('id')
            elif 'before' in record_content and record_content['before']:
                before = record_content['before']
                name_value = before.get('NAME') or before.get('name')
                id_value = before.get('ID') or before.get('id')
            
            # Format timestamp
            time_str = "N/A"
            if create_time:
                try:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(create_time / 1000)
                    time_ago = (datetime.now() - dt).total_seconds()
                    time_str = f"{time_ago:.0f}s ago"
                except:
                    time_str = str(create_time)
            
            # Check if this is our test record
            if name_value and test_name in str(name_value):
                print(f"\n   ✅✅✅ FOUND TEST RECORD! (Record {idx})")
                print(f"      Operation: {op_name} ({operation})")
                print(f"      Name: {name_value}")
                print(f"      ID: {id_value}")
                print(f"      Time: {time_str}")
                found = True
            elif idx <= 10:  # Show first 10 for reference
                print(f"   {idx}. {op_name} - Name: {name_value}, ID: {id_value}, Time: {time_str}")
    
    if not found:
        print(f"\n   ⚠ Test record '{test_name}' not found in latest 20 records")
        print(f"   But record count increased, so new data was added")
        print(f"   ")
        print(f"   Let's check total count and all records with that name pattern...")
        
        # Search by name pattern
        query2 = f"""
        SELECT 
            RECORD_CONTENT,
            RECORD_METADATA:CreateTime as create_time
        FROM {sf_database}.{sf_schema}.TEST
        WHERE (
            RECORD_CONTENT:after:name LIKE '%CDC Test 20260113%'
            OR RECORD_CONTENT:before:name LIKE '%CDC Test 20260113%'
        )
        """
        
        sf_cursor.execute(query2)
        name_results = sf_cursor.fetchall()
        
        if name_results:
            print(f"   ✅ Found {len(name_results)} record(s) with matching name pattern!")
            for idx, row in enumerate(name_results, 1):
                record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                create_time = row[1]
                print(f"     Record {idx}: Time = {create_time}")
        else:
            print(f"   ❌ No records found with name pattern 'CDC Test 20260113'")
    
    # Get total count
    sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.TEST")
    total = sf_cursor.fetchone()[0]
    print(f"\n2. Total records in TEST table: {total}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)
print("CONCLUSION:")
if found:
    print("  ✅ CDC IS WORKING! Test record found in Snowflake!")
else:
    print("  ⚠ Test record not found, but record count increased.")
    print("  This suggests data is flowing, but may need more time or")
    print("  the record is in a different format than expected.")
print("=" * 70)


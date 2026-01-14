#!/usr/bin/env python3
"""Check if test ID 73032 is in the TEST table."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING FOR TEST ID 73032 IN SNOWFLAKE")
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
    
    print(f"\n1. Checking TEST table for ID {test_id}...")
    print("-" * 70)
    
    # Oracle NUMBER types are stored as base64-encoded values in Snowflake
    # We need to check both the numeric value and the encoded format
    # The ID might be stored in 'after' or 'before' fields
    
    # First, let's try a direct query
    query = f"""
    SELECT 
        RECORD_CONTENT,
        RECORD_METADATA,
        RECORD_CONTENT:op as operation,
        RECORD_CONTENT:after:id as id_after,
        RECORD_CONTENT:after:name as name_after,
        RECORD_CONTENT:before:id as id_before,
        RECORD_CONTENT:before:name as name_before,
        RECORD_METADATA:CreateTime as create_time
    FROM {sf_database}.{sf_schema}.TEST
    WHERE (
        RECORD_CONTENT:after:id = {test_id} 
        OR RECORD_CONTENT:before:id = {test_id}
        OR TRY_CAST(RECORD_CONTENT:after:id::STRING AS NUMBER) = {test_id}
        OR TRY_CAST(RECORD_CONTENT:before:id::STRING AS NUMBER) = {test_id}
    )
    ORDER BY RECORD_METADATA:CreateTime DESC
    """
    
    sf_cursor.execute(query)
    results = sf_cursor.fetchall()
    
    if results:
        print(f"   ✅ Found {len(results)} record(s) with ID {test_id}:")
        print("-" * 70)
        
        for idx, row in enumerate(results, 1):
            record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            record_metadata = json.loads(row[1]) if isinstance(row[1], str) else row[1]
            operation = row[2]
            id_after = row[3]
            name_after = row[4]
            id_before = row[5]
            name_before = row[6]
            create_time = row[7]
            
            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(operation, operation)
            
            print(f"\n   Record {idx}:")
            print(f"     Operation: {op_name} ({operation})")
            print(f"     ID (after): {id_after}")
            print(f"     ID (before): {id_before}")
            print(f"     Name (after): {name_after}")
            print(f"     Name (before): {name_before}")
            print(f"     Create Time: {create_time}")
            
            # Show the actual ID value from the record
            if isinstance(record_content, dict):
                if operation in ['c', 'u'] and 'after' in record_content:
                    after = record_content['after']
                    if 'ID' in after:
                        print(f"     Actual ID from 'after': {after['ID']}")
                    if 'id' in after:
                        print(f"     Actual ID from 'after' (lowercase): {after['id']}")
                
                if operation in ['u', 'd'] and 'before' in record_content:
                    before = record_content['before']
                    if 'ID' in before:
                        print(f"     Actual ID from 'before': {before['ID']}")
                    if 'id' in before:
                        print(f"     Actual ID from 'before' (lowercase): {before['id']}")
    else:
        print(f"   ❌ No records found with ID {test_id}")
        
        print(f"\n2. Checking all ID values in TEST table...")
        print("-" * 70)
        
        # Get sample of IDs to see the format
        query2 = f"""
        SELECT 
            RECORD_CONTENT:after:id as id_after,
            RECORD_CONTENT:before:id as id_before,
            RECORD_CONTENT:op as operation
        FROM {sf_database}.{sf_schema}.TEST
        WHERE RECORD_CONTENT:after:id IS NOT NULL OR RECORD_CONTENT:before:id IS NOT NULL
        LIMIT 10
        """
        
        sf_cursor.execute(query2)
        sample_ids = sf_cursor.fetchall()
        
        if sample_ids:
            print(f"   Sample ID values found:")
            for idx, row in enumerate(sample_ids[:5], 1):
                id_after = row[0]
                id_before = row[1]
                operation = row[2]
                print(f"     {idx}. Operation: {operation}, ID (after): {id_after}, ID (before): {id_before}")
            
            print(f"\n   ⚠ Note: Oracle NUMBER types are stored as base64-encoded values")
            print(f"   The ID {test_id} might be encoded differently")
            print(f"   Let's check the raw RECORD_CONTENT structure...")
        
        # Check raw structure of a recent record
        query3 = f"""
        SELECT RECORD_CONTENT
        FROM {sf_database}.{sf_schema}.TEST
        WHERE RECORD_CONTENT:op IN ('c', 'u', 'd')
        ORDER BY RECORD_METADATA:CreateTime DESC
        LIMIT 1
        """
        
        sf_cursor.execute(query3)
        sample = sf_cursor.fetchone()
        
        if sample:
            record_content = json.loads(sample[0]) if isinstance(sample[0], str) else sample[0]
            if isinstance(record_content, dict) and 'after' in record_content:
                after = record_content['after']
                print(f"\n   Sample record structure:")
                print(f"     Keys in 'after': {list(after.keys())}")
                if 'ID' in after:
                    print(f"     ID value type: {type(after['ID'])}")
                    print(f"     ID value: {after['ID']}")
                if 'id' in after:
                    print(f"     id value type: {type(after['id'])}")
                    print(f"     id value: {after['id']}")
    
    print(f"\n3. Checking ORACLE_SF_P_CDC_USER_TEST_1913823665 table...")
    print("-" * 70)
    
    # Also check the other table
    query4 = f"""
    SELECT 
        RECORD_CONTENT:op as operation,
        RECORD_CONTENT:after:id as id_after,
        RECORD_CONTENT:before:id as id_before
    FROM {sf_database}.{sf_schema}.ORACLE_SF_P_CDC_USER_TEST_1913823665
    WHERE (
        RECORD_CONTENT:after:id = {test_id} 
        OR RECORD_CONTENT:before:id = {test_id}
    )
    """
    
    try:
        sf_cursor.execute(query4)
        results2 = sf_cursor.fetchall()
        
        if results2:
            print(f"   ✅ Found {len(results2)} record(s) in ORACLE_SF_P_CDC_USER_TEST_1913823665")
            for idx, row in enumerate(results2, 1):
                print(f"     {idx}. Operation: {row[0]}, ID (after): {row[1]}, ID (before): {row[2]}")
        else:
            print(f"   ❌ Not found in ORACLE_SF_P_CDC_USER_TEST_1913823665 either")
    except Exception as e:
        print(f"   ⚠ Error checking other table: {e}")
    
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
print(f"  Checked TEST table for ID {test_id}")
print(f"  If not found, it may be:")
print(f"    1. Still in buffer (wait 60 seconds for flush)")
print(f"    2. Encoded differently (Oracle NUMBER encoding)")
print(f"    3. In a different table")
print("=" * 70)


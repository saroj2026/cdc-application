#!/usr/bin/env python3
"""Decode Oracle NUMBER IDs from base64 to find test ID 73032."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
import json
import base64
import struct
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

def decode_oracle_number(encoded_value):
    """Decode Oracle NUMBER from base64 encoded format."""
    if isinstance(encoded_value, dict):
        if 'value' in encoded_value:
            # Base64 encoded value
            try:
                decoded_bytes = base64.b64decode(encoded_value['value'])
                # Oracle NUMBER format: first byte is exponent, rest are digits
                if len(decoded_bytes) > 0:
                    exponent = decoded_bytes[0] - 193  # Oracle bias
                    digits = []
                    for byte in decoded_bytes[1:]:
                        # Each byte represents 2 digits (BCD format)
                        digit1 = (byte >> 4) & 0x0F
                        digit2 = byte & 0x0F
                        if digit1 != 0:
                            digits.append(str(digit1))
                        if digit2 != 0:
                            digits.append(str(digit2))
                    
                    if digits:
                        # Reconstruct number
                        num_str = ''.join(digits)
                        # Apply exponent
                        if exponent > 0:
                            num_str = num_str + '0' * exponent
                        elif exponent < 0:
                            num_str = num_str[:exponent] if abs(exponent) < len(num_str) else '0'
                        
                        try:
                            return int(num_str)
                        except:
                            return None
            except:
                pass
    elif isinstance(encoded_value, (int, float)):
        return int(encoded_value)
    elif isinstance(encoded_value, str):
        try:
            return int(encoded_value)
        except:
            pass
    
    return None

print("=" * 70)
print("DECODING ORACLE NUMBER IDs TO FIND TEST ID 73032")
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
    
    print(f"\n1. Getting recent records and decoding IDs...")
    print("-" * 70)
    
    # Get recent records with CDC operations
    query = f"""
    SELECT 
        RECORD_CONTENT,
        RECORD_METADATA,
        RECORD_CONTENT:op as operation
    FROM {sf_database}.{sf_schema}.TEST
    WHERE RECORD_CONTENT:op IN ('c', 'u', 'd')
    ORDER BY RECORD_METADATA:CreateTime DESC
    LIMIT 20
    """
    
    sf_cursor.execute(query)
    results = sf_cursor.fetchall()
    
    found_test_id = False
    
    if results:
        print(f"   Checking {len(results)} recent CDC records...")
        print("-" * 70)
        
        for idx, row in enumerate(results, 1):
            record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            operation = row[2]
            
            if isinstance(record_content, dict):
                decoded_id = None
                
                # Check 'after' field for INSERT/UPDATE
                if operation in ['c', 'u'] and 'after' in record_content:
                    after = record_content['after']
                    id_value = after.get('ID') or after.get('id')
                    if id_value:
                        decoded_id = decode_oracle_number(id_value)
                
                # Check 'before' field for UPDATE/DELETE
                if not decoded_id and operation in ['u', 'd'] and 'before' in record_content:
                    before = record_content['before']
                    id_value = before.get('ID') or before.get('id')
                    if id_value:
                        decoded_id = decode_oracle_number(id_value)
                
                if decoded_id:
                    op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE'}.get(operation, operation)
                    
                    if decoded_id == test_id:
                        print(f"\n   ✅✅✅ FOUND TEST ID {test_id}!")
                        print(f"   Record {idx}:")
                        print(f"     Operation: {op_name} ({operation})")
                        print(f"     Decoded ID: {decoded_id}")
                        print(f"     Raw ID value: {id_value}")
                        found_test_id = True
                    elif idx <= 10:  # Show first 10 for reference
                        print(f"   Record {idx}: {op_name} - Decoded ID: {decoded_id}")
    
    if not found_test_id:
        print(f"\n   ❌ Test ID {test_id} not found in recent CDC records")
        print(f"\n2. Checking all records in TEST table...")
        print("-" * 70)
        
        # Get all records with IDs
        query2 = f"""
        SELECT 
            RECORD_CONTENT,
            RECORD_CONTENT:op as operation
        FROM {sf_database}.{sf_schema}.TEST
        WHERE RECORD_CONTENT:after:id IS NOT NULL OR RECORD_CONTENT:before:id IS NOT NULL
        """
        
        sf_cursor.execute(query2)
        all_results = sf_cursor.fetchall()
        
        print(f"   Checking {len(all_results)} total records...")
        
        found_count = 0
        for row in all_results:
            record_content = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            operation = row[1]
            
            if isinstance(record_content, dict):
                decoded_id = None
                
                if 'after' in record_content:
                    after = record_content['after']
                    id_value = after.get('ID') or after.get('id')
                    if id_value:
                        decoded_id = decode_oracle_number(id_value)
                
                if not decoded_id and 'before' in record_content:
                    before = record_content['before']
                    id_value = before.get('ID') or before.get('id')
                    if id_value:
                        decoded_id = decode_oracle_number(id_value)
                
                if decoded_id == test_id:
                    found_count += 1
                    op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(operation, operation)
                    print(f"   ✅ Found: {op_name} operation with ID {decoded_id}")
        
        if found_count > 0:
            print(f"\n   ✅✅✅ Found {found_count} record(s) with test ID {test_id}!")
        else:
            print(f"\n   ❌ Test ID {test_id} not found in any records")
            print(f"   Possible reasons:")
            print(f"     1. Records are still in buffer (wait 60+ seconds)")
            print(f"     2. Records were written to a different table")
            print(f"     3. The INSERT/UPDATE/DELETE operations didn't complete")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)


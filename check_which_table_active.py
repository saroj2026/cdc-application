#!/usr/bin/env python3
"""Check which table the connector is actively writing to."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
from datetime import datetime, timedelta
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING WHICH TABLE IS ACTIVELY RECEIVING DATA")
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
    
    tables_to_check = ['TEST', 'ORACLE_SF_P_CDC_USER_TEST_1913823665']
    
    print("\n1. Checking Recent Activity (Last 10 minutes)...")
    print("-" * 70)
    
    for table_name in tables_to_check:
        try:
            # Get most recent records by CreateTime
            query = f"""
            SELECT 
                RECORD_METADATA:CreateTime as create_time,
                RECORD_CONTENT:op as operation,
                RECORD_CONTENT:after:id as id_after,
                RECORD_CONTENT:before:id as id_before
            FROM {sf_database}.{sf_schema}.{table_name}
            WHERE RECORD_METADATA:CreateTime IS NOT NULL
            ORDER BY RECORD_METADATA:CreateTime DESC
            LIMIT 5
            """
            
            sf_cursor.execute(query)
            recent = sf_cursor.fetchall()
            
            if recent:
                print(f"\n   Table: {table_name}")
                print(f"   Most recent records:")
                
                # Get the most recent timestamp
                most_recent_time = recent[0][0] if recent[0][0] else 0
                
                # Convert timestamp (milliseconds) to datetime
                if most_recent_time:
                    try:
                        dt = datetime.fromtimestamp(most_recent_time / 1000)
                        time_ago = datetime.now() - dt
                        print(f"     Most recent: {dt.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago.total_seconds():.0f} seconds ago)")
                    except:
                        print(f"     Most recent timestamp: {most_recent_time}")
                
                # Show recent operations
                for idx, row in enumerate(recent[:3], 1):
                    op = row[1]
                    op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(op, op)
                    id_val = row[2] or row[3]
                    print(f"     {idx}. {op_name} - ID: {id_val}")
                
                # Check if this table has very recent activity (within last 5 minutes)
                if most_recent_time:
                    try:
                        dt = datetime.fromtimestamp(most_recent_time / 1000)
                        time_ago = datetime.now() - dt
                        if time_ago.total_seconds() < 300:  # 5 minutes
                            print(f"     ✅ ACTIVE - Has recent data (within 5 minutes)")
                        else:
                            print(f"     ⚠ INACTIVE - Last data was {time_ago.total_seconds()/60:.1f} minutes ago")
                    except:
                        pass
            else:
                print(f"\n   Table: {table_name}")
                print(f"   ⚠ No records with timestamps found")
                
        except Exception as e:
            print(f"\n   Table: {table_name}")
            print(f"   ❌ Error: {e}")
    
    print("\n2. Checking Total Records and CDC Operations...")
    print("-" * 70)
    
    for table_name in tables_to_check:
        try:
            # Total count
            sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.{table_name}")
            total = sf_cursor.fetchone()[0]
            
            # CDC operations count
            sf_cursor.execute(f"""
                SELECT 
                    RECORD_CONTENT:op as operation,
                    COUNT(*) as count
                FROM {sf_database}.{sf_schema}.{table_name}
                WHERE RECORD_CONTENT:op IN ('c', 'u', 'd')
                GROUP BY RECORD_CONTENT:op
            """)
            cdc_ops = sf_cursor.fetchall()
            
            print(f"\n   Table: {table_name}")
            print(f"     Total records: {total}")
            if cdc_ops:
                print(f"     CDC operations:")
                for op, count in cdc_ops:
                    op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE'}.get(op, op)
                    print(f"       {op_name} ({op}): {count}")
        except Exception as e:
            print(f"\n   Table: {table_name}")
            print(f"     ❌ Error: {e}")
    
    print("\n3. Connector Configuration Says...")
    print("-" * 70)
    print(f"   Topic: oracle_sf_p.CDC_USER.TEST")
    print(f"   Should write to: test (lowercase)")
    print(f"   But Snowflake table names are case-insensitive, so 'test' = 'TEST'")
    
    print("\n4. Recommendation...")
    print("-" * 70)
    print(f"   The connector is configured to write to 'test' table.")
    print(f"   The table 'ORACLE_SF_P_CDC_USER_TEST_1913823665' appears to be:")
    print(f"     - An old table from previous connector configuration")
    print(f"     - Or a table created during full load with auto-naming")
    print(f"   ")
    print(f"   Current active table: Check which has more recent timestamps above")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 70)


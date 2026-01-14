#!/usr/bin/env python3
"""Check what table name Snowflake sink connector is using."""

import requests
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import snowflake.connector
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("CHECKING SNOWFLAKE TABLE NAME")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Checking Sink Connector Configuration...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Database: {config.get('snowflake.database.name', 'N/A')}")
        print(f"   Schema: {config.get('snowflake.schema.name', 'N/A')}")
        
        # Parse the topic2table map
        topic_map = config.get('snowflake.topic2table.map', '')
        if topic_map:
            # Format is: "topic:table,topic:table"
            mappings = topic_map.split(',')
            print(f"\n   Table mappings:")
            for mapping in mappings:
                parts = mapping.split(':')
                if len(parts) == 2:
                    topic = parts[0]
                    table = parts[1]
                    print(f"     Topic: {topic} → Table: {table}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking Actual Tables in Snowflake...")
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
    
    # List all tables in the schema
    sf_cursor.execute(f"SHOW TABLES IN SCHEMA {sf_database}.{sf_schema}")
    tables = sf_cursor.fetchall()
    
    print(f"   Tables in {sf_database}.{sf_schema}:")
    
    test_tables = []
    for table in tables:
        table_name = table[1]  # Table name is in second column
        print(f"     - {table_name}")
        
        # Check if it matches the pattern the user mentioned
        if 'test' in table_name.lower() or 'oracle_sf_p' in table_name.lower():
            test_tables.append(table_name)
    
    if test_tables:
        print(f"\n   ⚠ Found {len(test_tables)} table(s) matching 'test' pattern:")
        for table_name in test_tables:
            print(f"     - {table_name}")
            
            # Check record count
            try:
                sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.{table_name}")
                count = sf_cursor.fetchone()[0]
                print(f"       Record count: {count}")
                
                # Check if it has RECORD_CONTENT and RECORD_METADATA
                sf_cursor.execute(f"DESC TABLE {sf_database}.{sf_schema}.{table_name}")
                columns = sf_cursor.fetchall()
                has_record_content = any(col[0] == 'RECORD_CONTENT' for col in columns)
                has_record_metadata = any(col[0] == 'RECORD_METADATA' for col in columns)
                
                if has_record_content and has_record_metadata:
                    print(f"       ✅ Has RECORD_CONTENT and RECORD_METADATA (CDC table)")
                    
                    # Check for CDC operations
                    sf_cursor.execute(f"""
                        SELECT 
                            RECORD_CONTENT:op as operation,
                            COUNT(*) as count
                        FROM {sf_database}.{sf_schema}.{table_name}
                        WHERE RECORD_CONTENT:op IS NOT NULL
                        GROUP BY RECORD_CONTENT:op
                    """)
                    op_counts = sf_cursor.fetchall()
                    if op_counts:
                        print(f"       CDC operations:")
                        for op, count in op_counts:
                            op_name = {'c': 'INSERT', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ'}.get(op, op)
                            print(f"         {op_name} ({op}): {count}")
                else:
                    print(f"       ⚠ Missing RECORD_CONTENT or RECORD_METADATA")
            except Exception as e:
                print(f"       ⚠ Error checking table: {e}")
    
    # Check specifically for the table name the user mentioned
    user_table_name = "oracle_sf_p_cdc_user_test_1913823665"
    print(f"\n3. Checking for table: {user_table_name}")
    print("-" * 70)
    
    try:
        sf_cursor.execute(f"SELECT COUNT(*) FROM {sf_database}.{sf_schema}.{user_table_name}")
        count = sf_cursor.fetchone()[0]
        print(f"   ✅ Table '{user_table_name}' EXISTS!")
        print(f"   Record count: {count}")
    except Exception as e:
        if "does not exist" in str(e).lower() or "not found" in str(e).lower():
            print(f"   ❌ Table '{user_table_name}' does NOT exist")
        else:
            print(f"   ⚠ Error: {e}")
    
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
print("  The sink connector should write to the table specified in")
print("  'snowflake.topic2table.map' configuration.")
print("  Check the mapping above to see which table is being used.")
print("=" * 70)


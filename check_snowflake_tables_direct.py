#!/usr/bin/env python3
"""Check Snowflake tables directly."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING SNOWFLAKE TABLES DIRECTLY")
print("=" * 70)

db = SessionLocal()
try:
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == "oracle_sf_p").first()
    if not pipeline:
        print("❌ Pipeline not found!")
        exit(1)
    
    snowflake_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.target_connection_id
    ).first()
    
    if not snowflake_conn_model:
        print("❌ Snowflake connection not found!")
        exit(1)
    
    snowflake_config = {
        'host': snowflake_conn_model.host,
        'port': snowflake_conn_model.port,
        'database': snowflake_conn_model.database,
        'user': snowflake_conn_model.username,
        'password': snowflake_conn_model.password,
    }
    
    if snowflake_conn_model.additional_config:
        if snowflake_conn_model.additional_config.get('account'):
            snowflake_config['account'] = snowflake_conn_model.additional_config['account']
        if snowflake_conn_model.additional_config.get('private_key'):
            snowflake_config['private_key'] = snowflake_conn_model.additional_config['private_key']
        if snowflake_conn_model.additional_config.get('warehouse'):
            snowflake_config['warehouse'] = snowflake_conn_model.additional_config['warehouse']
        if snowflake_conn_model.additional_config.get('role'):
            snowflake_config['role'] = snowflake_conn_model.additional_config['role']
    
    snowflake_schema = snowflake_conn_model.schema or 'public'
    
    sf_conn = SnowflakeConnector(snowflake_config)
    sf_c = sf_conn.connect()
    sf_cur = sf_c.cursor()
    
    sf_cur.execute(f'USE DATABASE {snowflake_config["database"]}')
    sf_cur.execute(f'USE SCHEMA {snowflake_schema}')
    
    print(f"\n1. Listing all tables in schema {snowflake_schema}...")
    print("-" * 70)
    
    sf_cur.execute(f"SHOW TABLES IN SCHEMA {snowflake_schema}")
    tables = sf_cur.fetchall()
    
    print(f"   Found {len(tables)} tables:")
    for table in tables:
        print(f"     - {table[1]}")  # Second column is table name
    
    print(f"\n2. Checking TEST table structure...")
    print("-" * 70)
    
    try:
        sf_cur.execute(f"DESCRIBE TABLE {snowflake_schema}.TEST")
        columns = sf_cur.fetchall()
        
        print("   TEST table columns:")
        for col in columns:
            col_name = col[0]
            col_type = col[1]
            nullable = col[3]
            print(f"     - {col_name}: {col_type} (nullable: {nullable})")
        
        column_names = [col[0].upper() for col in columns]
        has_record_content = 'RECORD_CONTENT' in column_names
        has_record_metadata = 'RECORD_METADATA' in column_names
        
        print(f"\n   RECORD_CONTENT: {'✅ Present' if has_record_content else '❌ Missing'}")
        print(f"   RECORD_METADATA: {'✅ Present' if has_record_metadata else '❌ Missing'}")
        
        if not (has_record_content and has_record_metadata):
            print(f"\n   ❌ Table is missing required columns!")
            print(f"   The Snowflake Kafka connector requires these columns.")
            print(f"   Need to recreate table with RECORD_CONTENT and RECORD_METADATA")
    except Exception as e:
        print(f"   ❌ Error describing table: {e}")
    
    print(f"\n3. Checking PROJECTS_SIMPLE table structure (working pipeline)...")
    print("-" * 70)
    
    try:
        sf_cur.execute(f"DESCRIBE TABLE {snowflake_schema}.PROJECTS_SIMPLE")
        ps_columns = sf_cur.fetchall()
        
        print("   PROJECTS_SIMPLE table columns:")
        for col in ps_columns:
            col_name = col[0]
            col_type = col[1]
            nullable = col[3]
            print(f"     - {col_name}: {col_type} (nullable: {nullable})")
        
        ps_column_names = [col[0].upper() for col in ps_columns]
        ps_has_record_content = 'RECORD_CONTENT' in ps_column_names
        ps_has_record_metadata = 'RECORD_METADATA' in ps_column_names
        
        print(f"\n   RECORD_CONTENT: {'✅ Present' if ps_has_record_content else '❌ Missing'}")
        print(f"   RECORD_METADATA: {'✅ Present' if ps_has_record_metadata else '❌ Missing'}")
        
        if ps_has_record_content and ps_has_record_metadata:
            print(f"\n   ✅ This table has the correct schema!")
            print(f"   This is why ps_sn_p pipeline works!")
    except Exception as e:
        print(f"   ⚠ Could not describe table: {e}")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


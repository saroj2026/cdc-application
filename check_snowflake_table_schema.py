#!/usr/bin/env python3
"""Check Snowflake table schema and compare with connector expectations."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING SNOWFLAKE TABLE SCHEMA")
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
    
    print("\n1. Checking TEST table schema...")
    print("-" * 70)
    
    sf_cur.execute(f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{snowflake_schema}' AND TABLE_NAME = 'TEST'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = sf_cur.fetchall()
    
    print("   Current TEST table columns:")
    if columns:
        for col in columns:
            print(f"     - {col[0]}: {col[1]} (nullable: {col[3]})")
    else:
        print("     ⚠ No columns found or table doesn't exist")
    
    # Check if RECORD_CONTENT and RECORD_METADATA exist
    column_names = [col[0].upper() for col in columns] if columns else []
    has_record_content = 'RECORD_CONTENT' in column_names
    has_record_metadata = 'RECORD_METADATA' in column_names
    
    print(f"\n   RECORD_CONTENT column: {'✅ Present' if has_record_content else '❌ Missing'}")
    print(f"   RECORD_METADATA column: {'✅ Present' if has_record_metadata else '❌ Missing'}")
    
    # Check ps_sn_p table schema for comparison
    print("\n2. Checking ps_sn_p table schema (working pipeline)...")
    print("-" * 70)
    
    try:
        sf_cur.execute(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                CHARACTER_MAXIMUM_LENGTH,
                IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{snowflake_schema}' AND TABLE_NAME = 'PROJECTS_SIMPLE'
            ORDER BY ORDINAL_POSITION
        """)
        
        ps_columns = sf_cur.fetchall()
        
        print("   PROJECTS_SIMPLE table columns:")
        if ps_columns:
            for col in ps_columns:
                print(f"     - {col[0]}: {col[1]} (nullable: {col[3]})")
        else:
            print("     ⚠ No columns found or table doesn't exist")
        
        ps_column_names = [col[0].upper() for col in ps_columns] if ps_columns else []
        ps_has_record_content = 'RECORD_CONTENT' in ps_column_names
        ps_has_record_metadata = 'RECORD_METADATA' in ps_column_names
        
        print(f"\n   RECORD_CONTENT column: {'✅ Present' if ps_has_record_content else '❌ Missing'}")
        print(f"   RECORD_METADATA column: {'✅ Present' if ps_has_record_metadata else '❌ Missing'}")
        
        print("\n3. Comparison:")
        print("-" * 70)
        if ps_has_record_content and ps_has_record_metadata:
            print("   ✅ ps_sn_p table has RECORD_CONTENT and RECORD_METADATA")
            if not (has_record_content and has_record_metadata):
                print("   ❌ TEST table is missing these columns!")
                print("   This is why the connector is failing!")
    except Exception as e:
        print(f"   ⚠ Could not check ps_sn_p table: {e}")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("The Snowflake Kafka connector expects tables to have:")
print("  - RECORD_CONTENT (VARIANT) - stores the actual record data")
print("  - RECORD_METADATA (OBJECT) - stores metadata (operation, source, etc.)")
print("\nIf the table doesn't have these columns, the connector will fail")
print("with 'Incompatible table - Table doesn't have a compatible schema'")
print("=" * 70)


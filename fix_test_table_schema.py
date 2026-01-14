#!/usr/bin/env python3
"""Fix TEST table schema - change RECORD_METADATA from OBJECT to VARIANT."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("FIXING TEST TABLE SCHEMA")
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
    
    print("\n1. Checking current TEST table schema...")
    print("-" * 70)
    
    sf_cur.execute(f"DESCRIBE TABLE {snowflake_schema}.TEST")
    columns = sf_cur.fetchall()
    
    print("   Current columns:")
    for col in columns:
        col_name = col[0]
        col_type = col[1]
        print(f"     - {col_name}: {col_type}")
    
    # Check if RECORD_METADATA is OBJECT instead of VARIANT
    record_metadata_type = None
    for col in columns:
        if col[0].upper() == 'RECORD_METADATA':
            record_metadata_type = col[1]
            break
    
    print(f"\n   RECORD_METADATA type: {record_metadata_type}")
    
    if record_metadata_type and record_metadata_type.upper() != 'VARIANT':
        print(f"\n   ⚠ RECORD_METADATA is {record_metadata_type}, should be VARIANT")
        print(f"   The Snowflake connector expects RECORD_METADATA to be VARIANT")
        
        print(f"\n2. Fixing table schema...")
        print("-" * 70)
        
        # Alter the column type
        try:
            # First, check if we need to preserve data
            sf_cur.execute(f"SELECT COUNT(*) FROM {snowflake_schema}.TEST")
            row_count = sf_cur.fetchone()[0]
            print(f"   Current row count: {row_count}")
            
            if row_count > 0:
                print(f"   ⚠ Table has {row_count} rows. Need to preserve data.")
                print(f"   Creating backup table...")
                
                # Create backup
                sf_cur.execute(f"CREATE TABLE {snowflake_schema}.TEST_BACKUP AS SELECT * FROM {snowflake_schema}.TEST")
                print(f"   ✅ Backup created: TEST_BACKUP")
            
            # Drop and recreate table with correct schema
            print(f"   Dropping and recreating table with correct schema...")
            sf_cur.execute(f"DROP TABLE {snowflake_schema}.TEST")
            
            # Create table with correct schema (VARIANT for both columns)
            create_sql = f"""
            CREATE TABLE {snowflake_schema}.TEST (
                RECORD_CONTENT VARIANT,
                RECORD_METADATA VARIANT
            )
            """
            sf_cur.execute(create_sql)
            print(f"   ✅ Table recreated with RECORD_CONTENT VARIANT, RECORD_METADATA VARIANT")
            
            if row_count > 0:
                print(f"   Restoring data from backup...")
                # Copy data back (OBJECT can be cast to VARIANT)
                sf_cur.execute(f"""
                    INSERT INTO {snowflake_schema}.TEST (RECORD_CONTENT, RECORD_METADATA)
                    SELECT RECORD_CONTENT, RECORD_METADATA::VARIANT
                    FROM {snowflake_schema}.TEST_BACKUP
                """)
                print(f"   ✅ Data restored")
                
                # Drop backup
                sf_cur.execute(f"DROP TABLE {snowflake_schema}.TEST_BACKUP")
                print(f"   ✅ Backup table dropped")
            
            sf_c.commit()
            print(f"\n   ✅✅✅ Table schema fixed!")
            
        except Exception as e:
            print(f"   ❌ Error fixing schema: {e}")
            sf_c.rollback()
            import traceback
            traceback.print_exc()
    else:
        print(f"\n   ✅ RECORD_METADATA is already VARIANT")
        print(f"   Schema is correct!")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)
print("Next Steps:")
print("  1. Restart the sink connector")
print("  2. Wait for buffer flush")
print("  3. Check Snowflake for CDC events")
print("=" * 70)


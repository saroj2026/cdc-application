#!/usr/bin/env python3
"""Check table name case in Snowflake."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING TABLE NAME CASE")
print("=" * 70)

db = SessionLocal()
try:
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == "oracle_sf_p").first()
    snowflake_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.target_connection_id
    ).first()
    
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
    
    print("\n1. Checking table names (case-sensitive)...")
    print("-" * 70)
    
    # Check if "test" (lowercase) exists
    try:
        sf_cur.execute("SELECT COUNT(*) FROM test")
        count = sf_cur.fetchone()[0]
        print(f"   ✅ Table 'test' (lowercase) exists: {count} rows")
    except Exception as e:
        print(f"   ❌ Table 'test' (lowercase) does NOT exist: {e}")
    
    # Check if "TEST" (uppercase) exists
    try:
        sf_cur.execute("SELECT COUNT(*) FROM TEST")
        count = sf_cur.fetchone()[0]
        print(f"   ✅ Table 'TEST' (uppercase) exists: {count} rows")
    except Exception as e:
        print(f"   ❌ Table 'TEST' (uppercase) does NOT exist: {e}")
    
    # Check what the connector is looking for
    print("\n2. Connector configuration:")
    print("-" * 70)
    print(f"   Topic2Table map: oracle_sf_p.CDC_USER.TEST:test")
    print(f"   Connector is looking for table: 'test' (lowercase)")
    
    print("\n3. Recommendation:")
    print("-" * 70)
    print(f"   If table is 'TEST' (uppercase) but connector looks for 'test' (lowercase),")
    print(f"   we need to either:")
    print(f"   1. Rename table to lowercase: ALTER TABLE TEST RENAME TO test")
    print(f"   2. Or update topic2table map to use uppercase: oracle_sf_p.CDC_USER.TEST:TEST")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


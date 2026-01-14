#!/usr/bin/env python3
"""Check raw data structure in Snowflake."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING RAW SNOWFLAKE DATA")
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
    
    print("\n1. Getting raw RECORD_METADATA and RECORD_CONTENT...")
    print("-" * 70)
    
    # Get raw data as strings
    sf_cur.execute("""
        SELECT 
            RECORD_METADATA::STRING as metadata_str,
            RECORD_CONTENT::STRING as content_str
        FROM TEST
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC NULLS LAST
        LIMIT 3
    """)
    
    records = sf_cur.fetchall()
    
    for i, record in enumerate(records, 1):
        metadata_str = record[0]
        content_str = record[1]
        
        print(f"\n   Record {i}:")
        print(f"     RECORD_METADATA (first 500 chars):")
        print(f"     {metadata_str[:500] if metadata_str else 'NULL'}")
        print(f"     RECORD_CONTENT (first 300 chars):")
        print(f"     {content_str[:300] if content_str else 'NULL'}")
    
    # Check total count and see if we can identify CDC vs snapshot
    print("\n2. Summary:")
    print("-" * 70)
    
    sf_cur.execute("SELECT COUNT(*) FROM TEST")
    total = sf_cur.fetchone()[0]
    print(f"   Total records: {total}")
    
    # Try to count records with different metadata structures
    sf_cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN RECORD_METADATA:operation IS NOT NULL THEN 1 END) as has_op,
            COUNT(CASE WHEN RECORD_METADATA:source IS NOT NULL THEN 1 END) as has_source,
            COUNT(CASE WHEN RECORD_METADATA IS NULL THEN 1 END) as null_metadata
        FROM TEST
    """)
    
    counts = sf_cur.fetchone()
    print(f"   Records with operation field: {counts[1]}")
    print(f"   Records with source field: {counts[2]}")
    print(f"   Records with NULL metadata: {counts[3]}")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)
print("The Snowflake connector should automatically add RECORD_METADATA")
print("with operation, source, and timestamp fields.")
print("If metadata is missing, the connector configuration might need adjustment.")
print("=" * 70)


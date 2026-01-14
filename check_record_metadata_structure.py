#!/usr/bin/env python3
"""Check the RECORD_METADATA structure of new records."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector
import json

print("=" * 70)
print("CHECKING RECORD_METADATA STRUCTURE")
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
    
    print("\n1. Checking latest records with full RECORD_METADATA...")
    print("-" * 70)
    
    # Get the latest 5 records with full metadata
    sf_cur.execute("""
        SELECT 
            RECORD_METADATA,
            RECORD_CONTENT
        FROM TEST
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC NULLS LAST
        LIMIT 5
    """)
    
    records = sf_cur.fetchall()
    
    print(f"   Latest {len(records)} records:")
    for i, record in enumerate(records, 1):
        metadata = record[0]
        content = record[1]
        
        print(f"\n   Record {i}:")
        print(f"     RECORD_METADATA keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'N/A'}")
        
        if isinstance(metadata, dict):
            # Check for operation field
            op = metadata.get('operation') or metadata.get('__op') or 'N/A'
            print(f"     Operation: {op}")
            
            # Check for source field
            source = metadata.get('source', {})
            if source:
                print(f"     Source: {source}")
            
            # Print full metadata (first 500 chars)
            metadata_str = json.dumps(metadata, indent=2, default=str)
            print(f"     Full metadata (first 500 chars):")
            print(f"     {metadata_str[:500]}")
        
        # Check content
        if isinstance(content, dict):
            content_id = content.get('ID') or content.get('id') or 'N/A'
            print(f"     Content ID: {content_id}")
    
    # Check if operation is in a different location
    print("\n2. Checking for operation in different metadata locations...")
    print("-" * 70)
    
    sf_cur.execute("""
        SELECT 
            RECORD_METADATA:operation::STRING as op1,
            RECORD_METADATA:__op::STRING as op2,
            RECORD_METADATA:payload.operation::STRING as op3,
            RECORD_METADATA:payload.op::STRING as op4,
            RECORD_METADATA
        FROM TEST
        WHERE RECORD_METADATA:source.ts_ms::NUMBER IS NOT NULL
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
        LIMIT 5
    """)
    
    ops = sf_cur.fetchall()
    
    for i, op_record in enumerate(ops, 1):
        op1, op2, op3, op4, metadata = op_record
        print(f"   Record {i}:")
        print(f"     operation: {op1}")
        print(f"     __op: {op2}")
        print(f"     payload.operation: {op3}")
        print(f"     payload.op: {op4}")
        if op1 or op2 or op3 or op4:
            print(f"     ✅ Found operation!")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


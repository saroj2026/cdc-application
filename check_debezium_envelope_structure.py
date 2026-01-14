#!/usr/bin/env python3
"""Check Debezium envelope structure in Snowflake to extract operation."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING DEBEZIUM ENVELOPE STRUCTURE")
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
    
    print("\n1. Checking RECORD_CONTENT structure (Debezium envelope)...")
    print("-" * 70)
    
    # Check if RECORD_CONTENT has payload structure
    sf_cur.execute("""
        SELECT 
            RECORD_CONTENT::STRING as content_str,
            RECORD_CONTENT:payload::OBJECT as payload,
            RECORD_CONTENT:payload.op::STRING as op_from_payload,
            RECORD_CONTENT:payload.operation::STRING as operation_from_payload,
            RECORD_METADATA::STRING as metadata_str
        FROM TEST
        WHERE RECORD_CONTENT IS NOT NULL
        ORDER BY RECORD_METADATA:CreateTime::NUMBER DESC
        LIMIT 3
    """)
    
    records = sf_cur.fetchall()
    
    for i, record in enumerate(records, 1):
        content_str = record[0]
        payload = record[1]
        op_from_payload = record[2]
        operation_from_payload = record[3]
        metadata_str = record[4]
        
        print(f"\n   Record {i}:")
        print(f"     RECORD_CONTENT (first 500 chars): {content_str[:500] if content_str else 'NULL'}")
        print(f"     payload.op: {op_from_payload}")
        print(f"     payload.operation: {operation_from_payload}")
        print(f"     RECORD_METADATA (first 300 chars): {metadata_str[:300] if metadata_str else 'NULL'}")
        
        if op_from_payload or operation_from_payload:
            print(f"     ✅ Found operation in payload!")
    
    # Check operation distribution using payload.op
    print("\n2. Operation distribution from payload.op:")
    print("-" * 70)
    
    sf_cur.execute("""
        SELECT 
            RECORD_CONTENT:payload.op::STRING as op,
            COUNT(*) as count
        FROM TEST
        WHERE RECORD_CONTENT:payload.op IS NOT NULL
        GROUP BY RECORD_CONTENT:payload.op::STRING
        ORDER BY op
    """)
    
    op_counts = sf_cur.fetchall()
    op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
    
    if op_counts:
        for op_count in op_counts:
            op = op_count[0] if op_count[0] else 'N/A'
            count = op_count[1]
            display_name = op_map.get(op, op)
            print(f"     {display_name} ({op}): {count} records")
    else:
        print(f"     ⚠ No operations found in payload.op")
    
    # Check CDC events using payload.op
    sf_cur.execute("""
        SELECT COUNT(*) as cdc_count
        FROM TEST
        WHERE RECORD_CONTENT:payload.op::STRING IN ('c', 'u', 'd')
    """)
    cdc_count = sf_cur.fetchone()[0]
    
    print(f"\n3. CDC Events Summary (from payload.op):")
    print("-" * 70)
    print(f"   Total CDC events (INSERT/UPDATE/DELETE): {cdc_count}")
    
    if cdc_count > 0:
        print(f"\n   ✅✅✅ CDC EVENTS FOUND IN SNOWFLAKE!")
        print(f"   ✅✅✅ CDC IS WORKING END-TO-END!")
        print(f"   Operation is stored in RECORD_CONTENT:payload.op")
    else:
        print(f"\n   ⚠ No CDC events found in payload.op")
        print(f"   Need to check if operation is in a different location")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)
print("The operation field is in RECORD_CONTENT:payload.op for Debezium envelope format")
print("We need to query using this path to identify CDC events")
print("=" * 70)


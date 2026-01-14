#!/usr/bin/env python3
"""Check the new records in Snowflake to see their operation type."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector

print("=" * 70)
print("CHECKING NEW RECORDS IN SNOWFLAKE")
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
    
    print("\n1. Checking latest records in TEST table...")
    print("-" * 70)
    
    # Get the latest 10 records with their operation type
    sf_cur.execute("""
        SELECT 
            RECORD_CONTENT,
            RECORD_METADATA,
            RECORD_METADATA:operation::STRING as op,
            RECORD_METADATA:source.ts_ms::NUMBER as ts_ms
        FROM TEST
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
        LIMIT 10
    """)
    
    records = sf_cur.fetchall()
    
    print(f"   Latest {len(records)} records:")
    for i, record in enumerate(records, 1):
        op = record[2] if record[2] else 'N/A'
        ts_ms = record[3] if record[3] else 'N/A'
        op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
        op_name = op_map.get(op, op)
        
        # Get ID from RECORD_CONTENT if available
        try:
            record_content = record[0]
            if record_content:
                record_id = record_content.get('ID') if isinstance(record_content, dict) else 'N/A'
            else:
                record_id = 'N/A'
        except:
            record_id = 'N/A'
        
        print(f"     {i}. ID={record_id}, OP={op_name} ({op}), TS={ts_ms}")
    
    # Check operation distribution
    print("\n2. Operation distribution:")
    print("-" * 70)
    
    sf_cur.execute("""
        SELECT 
            RECORD_METADATA:operation::STRING as op,
            COUNT(*) as count
        FROM TEST
        GROUP BY RECORD_METADATA:operation::STRING
        ORDER BY op
    """)
    
    op_counts = sf_cur.fetchall()
    op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
    
    for op_count in op_counts:
        op = op_count[0] if op_count[0] else 'N/A'
        count = op_count[1]
        display_name = op_map.get(op, op)
        print(f"     {display_name} ({op}): {count} records")
    
    # Check for CDC events
    sf_cur.execute("""
        SELECT COUNT(*) as cdc_count
        FROM TEST
        WHERE RECORD_METADATA:operation::STRING IN ('c', 'u', 'd')
    """)
    cdc_count = sf_cur.fetchone()[0]
    
    print(f"\n3. CDC Events Summary:")
    print("-" * 70)
    print(f"   Total CDC events (INSERT/UPDATE/DELETE): {cdc_count}")
    
    if cdc_count > 0:
        print(f"\n   ✅✅✅ CDC EVENTS FOUND IN SNOWFLAKE!")
        print(f"   ✅✅✅ CDC IS WORKING END-TO-END!")
    else:
        print(f"\n   ⚠ No CDC events yet (only snapshot records)")
        print(f"   The 4 new records might be from the connector restart")
        print(f"   Need to test with new INSERT/UPDATE/DELETE operations")
    
    sf_cur.close()
    sf_c.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


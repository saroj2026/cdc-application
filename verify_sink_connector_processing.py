#!/usr/bin/env python3
"""Verify sink connector is processing CDC messages to Snowflake."""

import requests
import time

print("=" * 70)
print("VERIFYING SINK CONNECTOR PROCESSING")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Checking sink connector status...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector state: {connector_state}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_state = task.get('state', 'N/A')
            task_id = task.get('id', 'N/A')
            print(f"   Task {task_id} state: {task_state}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"\n   ⚠ Task Error:")
                    print(f"   {trace[:500]}")
    
    print("\n2. Checking sink connector configuration...")
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        topics = config.get('topics', 'N/A')
        print(f"   Topics: {topics}")
        print(f"   Table mapping: {config.get('snowflake.topic2table.map', 'N/A')}")
    
    print("\n3. The sink connector should be processing messages from Kafka topic")
    print("   Topic: oracle_sf_p.CDC_USER.TEST (has 23 messages)")
    print("   Waiting a bit longer for sink to process...")
    time.sleep(20)
    
    print("\n4. Checking Snowflake for CDC events...")
    from ingestion.connectors.snowflake import SnowflakeConnector
    from ingestion.database.models_db import ConnectionModel, PipelineModel
    from ingestion.database.session import SessionLocal
    
    db = SessionLocal()
    try:
        pipeline = db.query(PipelineModel).filter(PipelineModel.name == "oracle_sf_p").first()
        if pipeline:
            snowflake_conn_model = db.query(ConnectionModel).filter(
                ConnectionModel.id == pipeline.target_connection_id
            ).first()
            
            if snowflake_conn_model:
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
                
                # Check operation counts
                sf_cur.execute("""
                    SELECT 
                        RECORD_METADATA:operation::STRING as op,
                        COUNT(*) as count
                    FROM TEST
                    GROUP BY RECORD_METADATA:operation::STRING
                    ORDER BY op
                """)
                op_counts = sf_cur.fetchall()
                
                print("\n   Operation counts in Snowflake:")
                op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
                for op_count in op_counts:
                    op = op_count[0] or 'N/A'
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
                
                if cdc_count > 0:
                    print(f"\n   ✓✓✓ CDC EVENTS FOUND: {cdc_count} CDC event(s) in Snowflake!")
                    print(f"   ✓✓✓ CDC IS WORKING END-TO-END!")
                else:
                    print(f"\n   ⚠ No CDC events in Snowflake yet")
                    print(f"   Sink connector may still be processing...")
                    print(f"   Wait a bit longer and check again")
                
                # Get latest records
                sf_cur.execute("""
                    SELECT 
                        RECORD_CONTENT:ID::INTEGER as id,
                        RECORD_CONTENT:NAME::STRING as name,
                        RECORD_METADATA:operation::STRING as op,
                        RECORD_METADATA:source.ts_ms::NUMBER as ts_ms
                    FROM TEST
                    WHERE RECORD_METADATA:operation::STRING IN ('c', 'u', 'd')
                    ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
                    LIMIT 5
                """)
                
                cdc_rows = sf_cur.fetchall()
                if cdc_rows:
                    print(f"\n   Latest CDC events in Snowflake:")
                    for i, row in enumerate(cdc_rows, 1):
                        op = row[2] if row[2] else 'N/A'
                        op_name = op_map.get(op, op)
                        print(f"     {i}. ID={row[0]}, NAME={row[1]}, OP={op_name} ({op}), TS={row[3]}")
                
                sf_cur.close()
                sf_c.close()
    finally:
        db.close()
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


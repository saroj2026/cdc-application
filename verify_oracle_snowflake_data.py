#!/usr/bin/env python3
"""Verify data flow from Oracle to Snowflake - compare what was inserted vs what was received."""

from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal
from ingestion.connectors.snowflake import SnowflakeConnector
from ingestion.connectors.oracle import OracleConnector
import json

print("=" * 70)
print("VERIFYING ORACLE → SNOWFLAKE DATA FLOW")
print("=" * 70)

db = SessionLocal()
try:
    # Get pipeline
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == "oracle_sf_p").first()
    if not pipeline:
        print("❌ Pipeline 'oracle_sf_p' not found")
        exit(1)
    
    # Get connections
    oracle_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.source_connection_id
    ).first()
    snowflake_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.target_connection_id
    ).first()
    
    if not oracle_conn_model or not snowflake_conn_model:
        print("❌ Connections not found")
        exit(1)
    
    # Oracle connection config
    oracle_config = {
        'host': oracle_conn_model.host,
        'port': oracle_conn_model.port,
        'user': oracle_conn_model.username,
        'password': oracle_conn_model.password,
    }
    
    if oracle_conn_model.additional_config:
        if oracle_conn_model.additional_config.get('service_name'):
            oracle_config['service_name'] = oracle_conn_model.additional_config['service_name']
        elif oracle_conn_model.additional_config.get('database'):
            oracle_config['database'] = oracle_conn_model.additional_config['database']
        elif oracle_conn_model.additional_config.get('sid'):
            oracle_config['database'] = oracle_conn_model.additional_config['sid']
    
    if not oracle_config.get('database') and not oracle_config.get('service_name'):
        oracle_config['database'] = oracle_conn_model.database
    
    oracle_schema = pipeline.source_schema or oracle_conn_model.schema or 'cdc_user'
    
    # Snowflake connection config
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
    
    print("\n1. CHECKING ORACLE TABLE (cdc_user.test)")
    print("-" * 70)
    
    # Connect to Oracle
    oracle_conn = OracleConnector(oracle_config)
    oracle_c = oracle_conn.connect()
    oracle_cur = oracle_c.cursor()
    
    # Get all records from Oracle
    oracle_cur.execute(f'SELECT ID, NAME, CREATED_AT FROM {oracle_schema}.test ORDER BY ID')
    oracle_rows = oracle_cur.fetchall()
    
    print(f"   Total records in Oracle: {len(oracle_rows)}")
    print(f"\n   Oracle Records:")
    oracle_data = {}
    for row in oracle_rows:
        record_id = row[0]
        name = row[1]
        created_at = row[2]
        oracle_data[record_id] = {
            'ID': record_id,
            'NAME': name,
            'CREATED_AT': str(created_at) if created_at else None
        }
        print(f"     ID={record_id}, NAME='{name}', CREATED_AT={created_at}")
    
    oracle_cur.close()
    oracle_c.close()
    
    print("\n2. CHECKING SNOWFLAKE TABLE (public.test)")
    print("-" * 70)
    
    # Connect to Snowflake
    sf_conn = SnowflakeConnector(snowflake_config)
    sf_c = sf_conn.connect()
    sf_cur = sf_c.cursor()
    
    sf_cur.execute(f'USE DATABASE {snowflake_config["database"]}')
    sf_cur.execute(f'USE SCHEMA {snowflake_schema}')
    
    # Get all records from Snowflake with operation type
    sf_cur.execute("""
        SELECT 
            RECORD_CONTENT::STRING as content_str,
            RECORD_METADATA::STRING as metadata_str,
            COALESCE(
                RECORD_METADATA:operation::STRING,
                RECORD_CONTENT:op::STRING,
                'N/A'
            ) as operation,
            RECORD_METADATA:CreateTime::NUMBER as create_time
        FROM TEST
        ORDER BY RECORD_METADATA:CreateTime::NUMBER ASC NULLS LAST
    """)
    
    sf_rows = sf_cur.fetchall()
    
    print(f"   Total records in Snowflake: {len(sf_rows)}")
    
    # Group by operation type
    snapshot_records = []
    cdc_records = []
    
    op_map = {'c': 'CREATE (INSERT)', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
    
    print(f"\n   Snowflake Records:")
    for i, row in enumerate(sf_rows, 1):
        content_str = row[0]
        metadata_str = row[1]
        operation = row[2] if row[2] else 'N/A'
        create_time = row[3]
        
        op_display = op_map.get(operation, operation)
        
        # Parse RECORD_CONTENT from JSON string
        try:
            if content_str:
                record_content = json.loads(content_str)
            else:
                record_content = {}
        except (json.JSONDecodeError, TypeError):
            # If it's already a dict, use it as is
            record_content = content_str if isinstance(content_str, dict) else {}
        
        # Extract data from RECORD_CONTENT
        if isinstance(record_content, dict):
            # Check if it's Debezium envelope format (has 'after' field)
            if 'after' in record_content:
                # Debezium envelope format
                after_data = record_content.get('after', {})
                before_data = record_content.get('before', {})
                op_from_content = record_content.get('op', 'N/A')
                
                if after_data:
                    record_id = after_data.get('ID') or after_data.get('id')
                    name = after_data.get('NAME') or after_data.get('name')
                    created_at = after_data.get('CREATED_AT') or after_data.get('created_at')
                elif before_data:
                    record_id = before_data.get('ID') or before_data.get('id')
                    name = before_data.get('NAME') or before_data.get('name')
                    created_at = before_data.get('CREATED_AT') or before_data.get('created_at')
                else:
                    record_id = 'N/A'
                    name = 'N/A'
                    created_at = 'N/A'
                
                print(f"     {i}. ID={record_id}, NAME='{name}', OP={op_display} ({op_from_content}), TS={create_time}")
                
                if operation in ['c', 'u', 'd'] or op_from_content in ['c', 'u', 'd']:
                    cdc_records.append({
                        'id': record_id,
                        'name': name,
                        'operation': op_from_content or operation,
                        'data': after_data or before_data
                    })
                else:
                    snapshot_records.append({
                        'id': record_id,
                        'name': name,
                        'operation': operation
                    })
            else:
                # Direct format (full load)
                record_id = record_content.get('ID') or record_content.get('id')
                name = record_content.get('NAME') or record_content.get('name')
                created_at = record_content.get('CREATED_AT') or record_content.get('created_at')
                
                print(f"     {i}. ID={record_id}, NAME='{name}', OP={op_display} ({operation}), TS={create_time}")
                
                if operation == 'r':
                    snapshot_records.append({
                        'id': record_id,
                        'name': name,
                        'operation': operation
                    })
                else:
                    cdc_records.append({
                        'id': record_id,
                        'name': name,
                        'operation': operation,
                        'data': record_content
                    })
        else:
            print(f"     {i}. RECORD_CONTENT is not a dict: {type(record_content)}")
    
    sf_cur.close()
    sf_c.close()
    
    print("\n3. COMPARISON SUMMARY")
    print("-" * 70)
    print(f"   Oracle records: {len(oracle_rows)}")
    print(f"   Snowflake total records: {len(sf_rows)}")
    print(f"   Snowflake snapshot records (r): {len(snapshot_records)}")
    print(f"   Snowflake CDC records (c/u/d): {len(cdc_records)}")
    
    # Check if Oracle records match Snowflake snapshot records
    print("\n4. DATA VERIFICATION")
    print("-" * 70)
    
    oracle_ids = set([row[0] for row in oracle_rows])
    snapshot_ids = set([r['id'] for r in snapshot_records if r['id'] != 'N/A'])
    
    if oracle_ids == snapshot_ids:
        print(f"   ✅ Oracle IDs match Snowflake snapshot IDs!")
    else:
        missing_in_sf = oracle_ids - snapshot_ids
        extra_in_sf = snapshot_ids - oracle_ids
        if missing_in_sf:
            print(f"   ⚠ Missing in Snowflake: {missing_in_sf}")
        if extra_in_sf:
            print(f"   ⚠ Extra in Snowflake: {extra_in_sf}")
    
    if cdc_records:
        print(f"\n   ✅ CDC Events Found:")
        for cdc in cdc_records:
            op_name = op_map.get(cdc['operation'], cdc['operation'])
            print(f"     - {op_name}: ID={cdc['id']}, NAME='{cdc.get('name', 'N/A')}'")
    else:
        print(f"\n   ⚠ No CDC events found (only snapshot records)")
    
    print("\n5. LATEST OPERATIONS IN SNOWFLAKE")
    print("-" * 70)
    
    # Reconnect to get latest records
    sf_c = sf_conn.connect()
    sf_cur = sf_c.cursor()
    sf_cur.execute(f'USE DATABASE {snowflake_config["database"]}')
    sf_cur.execute(f'USE SCHEMA {snowflake_schema}')
    
    sf_cur.execute("""
        SELECT 
            RECORD_CONTENT::STRING as content_str,
            COALESCE(
                RECORD_METADATA:operation::STRING,
                RECORD_CONTENT:op::STRING,
                'N/A'
            ) as operation,
            RECORD_METADATA:CreateTime::NUMBER as create_time
        FROM TEST
        ORDER BY RECORD_METADATA:CreateTime::NUMBER DESC
        LIMIT 5
    """)
    
    latest = sf_cur.fetchall()
    
    for i, row in enumerate(latest, 1):
        content_str = row[0]
        operation = row[1] if row[1] else 'N/A'
        create_time = row[2]
        
        op_display = op_map.get(operation, operation)
        
        # Parse RECORD_CONTENT from JSON string
        try:
            if content_str:
                record_content = json.loads(content_str)
            else:
                record_content = {}
        except (json.JSONDecodeError, TypeError):
            record_content = content_str if isinstance(content_str, dict) else {}
        
        # Extract ID and NAME
        if isinstance(record_content, dict):
            if 'after' in record_content:
                data = record_content.get('after') or record_content.get('before') or {}
            else:
                data = record_content
            
            record_id = data.get('ID') or data.get('id') or 'N/A'
            name = data.get('NAME') or data.get('name') or 'N/A'
        else:
            record_id = 'N/A'
            name = 'N/A'
        
        print(f"   {i}. ID={record_id}, NAME='{name}', OP={op_display}, TS={create_time}")
    
    sf_cur.close()
    sf_c.close()
    
    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    
finally:
    db.close()


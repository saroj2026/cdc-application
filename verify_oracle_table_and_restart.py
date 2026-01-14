#!/usr/bin/env python3
"""Verify Oracle table exists and restart connector if needed."""

import requests
import time
from ingestion.connectors.oracle import OracleConnector
from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal

PIPELINE_NAME = "oracle_sf_p"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("VERIFYING ORACLE TABLE AND CONNECTOR CONFIGURATION")
print("=" * 70)

# Get pipeline and connection from database
db = SessionLocal()
try:
    pipeline = db.query(PipelineModel).filter(PipelineModel.name == PIPELINE_NAME).first()
    if not pipeline:
        print(f"❌ Pipeline '{PIPELINE_NAME}' not found!")
        exit(1)
    
    oracle_conn_model = db.query(ConnectionModel).filter(
        ConnectionModel.id == pipeline.source_connection_id
    ).first()
    
    if not oracle_conn_model:
        print("❌ Source connection not found!")
        exit(1)
    
    # Build Oracle config
    oracle_config = {
        'host': oracle_conn_model.host,
        'port': oracle_conn_model.port,
        'database': oracle_conn_model.database,
        'user': oracle_conn_model.username,
        'password': oracle_conn_model.password,
    }
    
    if oracle_conn_model.additional_config and oracle_conn_model.additional_config.get('service_name'):
        oracle_config['service_name'] = oracle_conn_model.additional_config['service_name']
    
    source_table = pipeline.source_tables[0] if pipeline.source_tables else None
    if source_table:
        parts = source_table.split('.')
        if len(parts) == 2:
            oracle_schema = parts[0]
            oracle_table = parts[1]
        else:
            oracle_schema = oracle_conn_model.schema or oracle_conn_model.username
            oracle_table = parts[0]
    else:
        oracle_schema = oracle_conn_model.schema or oracle_conn_model.username
        oracle_table = 'test'
    
    print(f"\n✓ Pipeline: {pipeline.name}")
    print(f"✓ Oracle schema: {oracle_schema}, table: {oracle_table}")
    print(f"✓ Connector config table.include.list: {oracle_schema}.{oracle_table}")
    
finally:
    db.close()

# Connect to Oracle and verify table
print("\n1. Verifying Oracle Table:")
try:
    oracle_conn = OracleConnector(oracle_config)
    oracle_c = oracle_conn.connect()
    oracle_cur = oracle_c.cursor()
    
    # Check if table exists (try different case combinations)
    print(f"\n   Checking table: {oracle_schema}.{oracle_table}")
    
    # Try exact case first
    try:
        oracle_cur.execute(f'SELECT COUNT(*) FROM {oracle_schema}.{oracle_table}')
        count = oracle_cur.fetchone()[0]
        print(f"   ✓ Table exists (exact case): {count} rows")
        table_exists = True
    except Exception as e:
        print(f"   ⚠ Table not found with exact case: {e}")
        table_exists = False
        
        # Try uppercase (Oracle default)
        try:
            oracle_cur.execute(f'SELECT COUNT(*) FROM {oracle_schema.upper()}.{oracle_table.upper()}')
            count = oracle_cur.fetchone()[0]
            print(f"   ✓ Table exists (uppercase): {count} rows")
            print(f"   ⚠ NOTE: Oracle uppercases identifiers, so actual table is {oracle_schema.upper()}.{oracle_table.upper()}")
            table_exists = True
        except Exception as e2:
            print(f"   ✗ Table not found with uppercase either: {e2}")
            table_exists = False
    
    oracle_cur.close()
    oracle_c.close()
    
except Exception as e:
    print(f"   ❌ Error connecting to Oracle: {e}")
    import traceback
    traceback.print_exc()

# Check connector config
print("\n2. Checking Connector Configuration:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
    if r.status_code == 200:
        config = r.json()
        table_include = config.get('table.include.list', 'N/A')
        print(f"   table.include.list: {table_include}")
        print(f"   snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        print(f"   log.mining.strategy: {config.get('log.mining.strategy', 'N/A')}")
        print(f"   log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
        
        # Check if config matches actual table
        if table_include and table_include.lower() == f"{oracle_schema}.{oracle_table}".lower():
            print(f"   ✓ Config matches actual table")
        else:
            print(f"   ⚠ Config might not match actual table case")
except Exception as e:
    print(f"   Error: {e}")

# Check connector status
print("\n3. Checking Connector Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
    if r.status_code == 200:
        status = r.json()
        state = status.get('connector', {}).get('state', 'N/A')
        print(f"   State: {state}")
        
        tasks = status.get('tasks', [])
        for i, task in enumerate(tasks):
            task_state = task.get('state', 'N/A')
            print(f"   Task {i}: {task_state}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("1. If table exists, try INSERT/UPDATE/DELETE operations in Oracle")
print("2. Wait 10-20 seconds")
print("3. Check Kafka topic for new messages")
print("4. If still no messages, check Debezium connector logs on the server")
print("=" * 70)


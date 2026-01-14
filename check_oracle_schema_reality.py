#!/usr/bin/env python3
"""Check actual Oracle schema and table setup."""

from ingestion.connectors.oracle import OracleConnector
from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal

PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("CHECKING ACTUAL ORACLE SCHEMA AND TABLE SETUP")
print("=" * 70)

# Get pipeline from database
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
    
    print(f"\n✓ Pipeline: {pipeline.name}")
    print(f"✓ Pipeline source_schema: {pipeline.source_schema}")
    print(f"✓ Pipeline source_tables: {pipeline.source_tables}")
    print(f"✓ Oracle connection user: {oracle_conn_model.username}")
    print(f"✓ Oracle connection schema: {oracle_conn_model.schema}")
    
finally:
    db.close()

# Connect to Oracle and check actual schemas
print("\n1. Checking Oracle Schemas and Tables:")
try:
    oracle_conn = OracleConnector(oracle_config)
    oracle_c = oracle_conn.connect()
    oracle_cur = oracle_c.cursor()
    
    # Check what schemas exist
    print(f"\n   Checking for schemas with 'cdc' in the name...")
    
    # Try to find cdc_user and c##cdc_user schemas
    oracle_cur.execute("""
        SELECT username 
        FROM all_users 
        WHERE UPPER(username) LIKE '%CDC%'
        ORDER BY username
    """)
    
    cdc_users = oracle_cur.fetchall()
    print(f"\n   Found {len(cdc_users)} user(s) with 'CDC' in name:")
    for user in cdc_users:
        print(f"     - {user[0]}")
    
    # Check if cdc_user schema exists and has test table
    print(f"\n2. Checking cdc_user schema (without ##):")
    try:
        oracle_cur.execute('SELECT COUNT(*) FROM cdc_user.test')
        count = oracle_cur.fetchone()[0]
        print(f"   ✓ cdc_user.test table exists: {count} rows")
        cdc_user_exists = True
    except Exception as e:
        print(f"   ✗ cdc_user.test not found: {e}")
        cdc_user_exists = False
    
    # Check if c##cdc_user schema exists and has test table
    print(f"\n3. Checking c##cdc_user schema (with ##):")
    try:
        oracle_cur.execute('SELECT COUNT(*) FROM "c##cdc_user".test')
        count = oracle_cur.fetchone()[0]
        print(f"   ✓ c##cdc_user.test table exists: {count} rows")
        c_cdc_user_exists = True
    except Exception as e:
        print(f"   ✗ c##cdc_user.test not found: {e}")
        c_cdc_user_exists = False
    
    # Check what user we're connected as and what tables it can see
    print(f"\n4. Checking current user and accessible tables:")
    oracle_cur.execute("SELECT USER FROM DUAL")
    current_user = oracle_cur.fetchone()[0]
    print(f"   Current user: {current_user}")
    
    oracle_cur.execute("""
        SELECT owner, table_name 
        FROM all_tables 
        WHERE UPPER(table_name) = 'TEST' 
        AND UPPER(owner) LIKE '%CDC%'
        ORDER BY owner
    """)
    
    test_tables = oracle_cur.fetchall()
    print(f"\n   Found TEST tables in CDC schemas:")
    for owner, table_name in test_tables:
        print(f"     - {owner}.{table_name}")
    
    oracle_cur.close()
    oracle_c.close()
    
except Exception as e:
    print(f"   ❌ Error connecting to Oracle: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
if cdc_user_exists and not c_cdc_user_exists:
    print("  ✓ Use cdc_user schema (without ##)")
    print("  ✓ This avoids special character issues in Kafka topic names")
elif c_cdc_user_exists and not cdc_user_exists:
    print("  ⚠ Only c##cdc_user exists")
    print("  ⚠ May need to create cdc_user or update connector to handle ##")
elif cdc_user_exists and c_cdc_user_exists:
    print("  ✓ Both schemas exist")
    print("  ✓ Recommend using cdc_user (without ##) to avoid connector issues")
else:
    print("  ⚠ Neither schema found - need to create one")
print("=" * 70)


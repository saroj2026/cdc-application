#!/usr/bin/env python3
"""Check cdc_user.test table structure and grant necessary permissions."""

from ingestion.connectors.oracle import OracleConnector
from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal

PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("CHECKING TABLE STRUCTURE AND GRANTING PERMISSIONS")
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
    
    # Build Oracle config (connects as c##cdc_user)
    oracle_config = {
        'host': oracle_conn_model.host,
        'port': oracle_conn_model.port,
        'database': oracle_conn_model.database,
        'user': oracle_conn_model.username,
        'password': oracle_conn_model.password,
    }
    
    if oracle_conn_model.additional_config and oracle_conn_model.additional_config.get('service_name'):
        oracle_config['service_name'] = oracle_conn_model.additional_config['service_name']
    
finally:
    db.close()

# Connect to Oracle and check table structure
print("\n1. Checking cdc_user.test table structure...")
try:
    oracle_conn = OracleConnector(oracle_config)
    oracle_c = oracle_conn.connect()
    oracle_cur = oracle_c.cursor()
    
    # Get table columns
    oracle_cur.execute("""
        SELECT column_name, data_type, nullable 
        FROM all_tab_columns 
        WHERE owner = 'CDC_USER' 
        AND table_name = 'TEST'
        ORDER BY column_id
    """)
    
    columns = oracle_cur.fetchall()
    print(f"\n   Table: CDC_USER.TEST")
    print(f"   Columns ({len(columns)}):")
    for col_name, data_type, nullable in columns:
        nullable_str = "NULL" if nullable == "Y" else "NOT NULL"
        print(f"     - {col_name} ({data_type}, {nullable_str})")
    
    # Try a simple SELECT with sample data
    print(f"\n2. Sample data from table:")
    oracle_cur.execute('SELECT * FROM cdc_user.test WHERE ROWNUM <= 1')
    sample_row = oracle_cur.fetchone()
    if sample_row:
        column_names = [desc[0] for desc in oracle_cur.description]
        print(f"   Columns in result: {', '.join(column_names)}")
        print(f"   Sample row: {dict(zip(column_names, sample_row))}")
    
    oracle_cur.close()
    oracle_c.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("PERMISSIONS NEEDED:")
print("=" * 70)
print("For CDC to work, c##cdc_user needs:")
print("  1. SELECT (already has)")
print("  2. INSERT (needed for capturing inserts)")
print("  3. UPDATE (needed for capturing updates)")
print("  4. DELETE (needed for capturing deletes)")
print("")
print("SQL to grant permissions (run as SYSDBA):")
print("  GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;")
print("")
print("Or grant on all tables in schema:")
print("  GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;")
print("=" * 70)


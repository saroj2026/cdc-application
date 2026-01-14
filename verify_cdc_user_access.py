#!/usr/bin/env python3
"""Verify that c##cdc_user can access cdc_user.test table."""

from ingestion.connectors.oracle import OracleConnector
from ingestion.database.models_db import ConnectionModel, PipelineModel
from ingestion.database.session import SessionLocal

PIPELINE_NAME = "oracle_sf_p"

print("=" * 70)
print("VERIFYING ACCESS TO cdc_user.test TABLE")
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
    
    print(f"\n✓ Oracle connection user: {oracle_conn_model.username}")
    print(f"✓ Pipeline source_schema: {pipeline.source_schema}")
    print(f"✓ Target table: {pipeline.source_schema}.test")
    
finally:
    db.close()

# Connect to Oracle and verify access
print("\n1. Testing access to cdc_user.test table (as c##cdc_user)...")
try:
    oracle_conn = OracleConnector(oracle_config)
    oracle_c = oracle_conn.connect()
    oracle_cur = oracle_c.cursor()
    
    # Check current user
    oracle_cur.execute("SELECT USER FROM DUAL")
    current_user = oracle_cur.fetchone()[0]
    print(f"   Current user: {current_user}")
    
    # Try to access cdc_user.test table
    try:
        oracle_cur.execute('SELECT COUNT(*) FROM cdc_user.test')
        count = oracle_cur.fetchone()[0]
        print(f"   ✓ SUCCESS: Can access cdc_user.test table")
        print(f"   ✓ Table has {count} rows")
        
        # Try to insert a test record to verify write access
        print(f"\n2. Testing write access (INSERT)...")
        try:
            oracle_cur.execute("""
                INSERT INTO cdc_user.test (ID, NAME, EMAIL, CREATED_DATE, UPDATED_DATE, STATUS) 
                VALUES (999999, 'CDC Access Test', 'access_test@example.com', SYSDATE, SYSDATE, 'active')
            """)
            oracle_c.commit()
            print(f"   ✓ SUCCESS: Can INSERT into cdc_user.test table")
            
            # Clean up test record
            oracle_cur.execute("DELETE FROM cdc_user.test WHERE ID = 999999")
            oracle_c.commit()
            print(f"   ✓ Test record deleted")
            
        except Exception as e:
            print(f"   ✗ Cannot INSERT into cdc_user.test: {e}")
            print(f"   ⚠ May need to grant INSERT permission to c##cdc_user")
        
        # Try to update
        print(f"\n3. Testing update access (UPDATE)...")
        try:
            oracle_cur.execute("""
                UPDATE cdc_user.test 
                SET UPDATED_DATE = SYSDATE 
                WHERE ID = (SELECT MIN(ID) FROM cdc_user.test)
            """)
            oracle_c.commit()
            print(f"   ✓ SUCCESS: Can UPDATE cdc_user.test table")
        except Exception as e:
            print(f"   ✗ Cannot UPDATE cdc_user.test: {e}")
            print(f"   ⚠ May need to grant UPDATE permission to c##cdc_user")
        
        # Try to delete
        print(f"\n4. Testing delete access (DELETE)...")
        try:
            # Only test if there are rows
            oracle_cur.execute('SELECT COUNT(*) FROM cdc_user.test')
            count = oracle_cur.fetchone()[0]
            if count > 0:
                oracle_cur.execute("""
                    DELETE FROM cdc_user.test 
                    WHERE ID = 999999
                """)
                oracle_c.commit()
                print(f"   ✓ SUCCESS: Can DELETE from cdc_user.test table (test record)")
            else:
                print(f"   ⚠ Skipped DELETE test (no rows in table)")
        except Exception as e:
            print(f"   ✗ Cannot DELETE from cdc_user.test: {e}")
            print(f"   ⚠ May need to grant DELETE permission to c##cdc_user")
        
    except Exception as e:
        print(f"   ✗ ERROR: Cannot access cdc_user.test table: {e}")
        print(f"   ⚠ Need to grant SELECT permission to c##cdc_user")
        print(f"   ⚠ Run: GRANT SELECT, INSERT, UPDATE, DELETE ON cdc_user.test TO c##cdc_user;")
    
    oracle_cur.close()
    oracle_c.close()
    
except Exception as e:
    print(f"   ❌ Error connecting to Oracle: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ACCESS VERIFICATION COMPLETE")
print("=" * 70)
print("If all permissions are granted, CDC should work now!")
print("=" * 70)


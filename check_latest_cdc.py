#!/usr/bin/env python3
"""Check for latest CDC changes in Snowflake."""

from ingestion.connectors.snowflake import SnowflakeConnector
from ingestion.database.models_db import ConnectionModel
from ingestion.database.session import SessionLocal

db = SessionLocal()
try:
    sf = db.query(ConnectionModel).filter_by(name='snowflake-s').first()
    
    config = {
        'host': sf.host,
        'port': sf.port,
        'database': sf.database,
        'user': sf.username,
        'password': sf.password,
        'account': sf.additional_config.get('account'),
        'private_key': sf.additional_config.get('private_key')
    }
    
    conn = SnowflakeConnector(config).connect()
    cur = conn.cursor()
    
    cur.execute('USE DATABASE SEG')
    cur.execute('USE SCHEMA PUBLIC')
    
    # Check for the latest records
    print("=" * 70)
    print("CHECKING LATEST CDC CHANGES")
    print("=" * 70)
    
    # Get latest records ordered by timestamp
    print("\nLatest 5 records (ordered by timestamp):")
    cur.execute("""
        SELECT 
            RECORD_CONTENT:ID::INTEGER as id,
            RECORD_CONTENT:NAME::STRING as name,
            RECORD_METADATA:operation::STRING as op,
            RECORD_METADATA:source.ts_ms::NUMBER as ts_ms
        FROM TEST
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC NULLS LAST
        LIMIT 5
    """)
    
    rows = cur.fetchall()
    for i, row in enumerate(rows, 1):
        print(f"  {i}. ID={row[0]}, NAME={row[1]}, OP={row[2]}, TS={row[3]}")
    
    # Check for the new test record (ID=103713)
    print("\nChecking for test record ID=103713:")
    cur.execute("""
        SELECT 
            RECORD_CONTENT:ID::INTEGER as id,
            RECORD_CONTENT:NAME::STRING as name,
            RECORD_METADATA:operation::STRING as op
        FROM TEST
        WHERE RECORD_CONTENT:ID::INTEGER = 103713
    """)
    
    test_rows = cur.fetchall()
    if test_rows:
        print(f"  ✓ Found test record:")
        for row in test_rows:
            print(f"    ID={row[0]}, NAME={row[1]}, OP={row[2]}")
    else:
        print("  ⚠ Test record (ID=103713) not found yet")
    
    # Count by operation type
    print("\nOperation counts:")
    cur.execute("""
        SELECT 
            RECORD_METADATA:operation::STRING as op,
            COUNT(*) as count
        FROM TEST
        GROUP BY RECORD_METADATA:operation::STRING
        ORDER BY op
    """)
    
    for row in cur.fetchall():
        op = row[0] or 'N/A'
        count = row[1]
        op_map = {'c': 'CREATE', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
        display = op_map.get(op, op)
        print(f"  {display} ({op}): {count} records")
    
    # Get total count
    cur.execute("SELECT COUNT(*) FROM TEST")
    total = cur.fetchone()[0]
    print(f"\nTotal records: {total}")
    
    cur.close()
    conn.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


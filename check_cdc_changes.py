#!/usr/bin/env python3
"""Check if CDC changes (INSERT/UPDATE) are captured in Snowflake."""

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
    
    # Check operation counts
    print("=" * 70)
    print("CDC Operation Counts in Snowflake TEST table")
    print("=" * 70)
    cur.execute("""
        SELECT 
            RECORD_METADATA:operation::STRING as op,
            COUNT(*) as count
        FROM TEST
        GROUP BY RECORD_METADATA:operation::STRING
        ORDER BY op
    """)
    
    op_map = {'c': 'CREATE', 'u': 'UPDATE', 'd': 'DELETE', 'r': 'READ (snapshot)'}
    print("\nOperation counts:")
    for row in cur.fetchall():
        op = row[0] or 'N/A'
        count = row[1]
        display_name = op_map.get(op, op)
        print(f"  {display_name} ({op}): {count} records")
    
    # Check for recent CDC events (INSERT/UPDATE)
    print("\n" + "=" * 70)
    print("Latest CDC Events (INSERT/UPDATE) - Last 10")
    print("=" * 70)
    cur.execute("""
        SELECT 
            RECORD_CONTENT:ID::INTEGER as id,
            RECORD_CONTENT:NAME::STRING as name,
            RECORD_METADATA:operation::STRING as op,
            RECORD_METADATA:source.ts_ms::NUMBER as ts_ms
        FROM TEST
        WHERE RECORD_METADATA:operation::STRING IN ('c', 'u')
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
        LIMIT 10
    """)
    
    cdc_rows = cur.fetchall()
    if cdc_rows:
        print(f"\nFound {len(cdc_rows)} CDC events (INSERT/UPDATE):")
        for row in cdc_rows:
            print(f"  ID={row[0]}, NAME={row[1]}, OPERATION={row[2]}, TS={row[3]}")
    else:
        print("\n⚠ No CDC events (INSERT/UPDATE) found yet.")
        print("  All records are from snapshot (operation='r').")
        print("  This might mean:")
        print("    - CDC changes haven't been captured yet")
        print("    - Connector is still in snapshot mode")
        print("    - Check connector status: http://72.61.233.209:8083/connectors/")
    
    # Check for the test ID we inserted (102259)
    print("\n" + "=" * 70)
    print("Checking for test record (ID=102259)")
    print("=" * 70)
    cur.execute("""
        SELECT 
            RECORD_CONTENT:ID::INTEGER as id,
            RECORD_CONTENT:NAME::STRING as name,
            RECORD_METADATA:operation::STRING as op
        FROM TEST
        WHERE RECORD_CONTENT:ID::INTEGER = 102259
        ORDER BY RECORD_METADATA:source.ts_ms::NUMBER DESC
        LIMIT 5
    """)
    
    test_rows = cur.fetchall()
    if test_rows:
        print(f"\n✓ Found test record (ID=102259):")
        for row in test_rows:
            print(f"  ID={row[0]}, NAME={row[1]}, OPERATION={row[2]}")
    else:
        print("\n⚠ Test record (ID=102259) not found in Snowflake yet.")
        print("  This might mean CDC changes haven't been captured yet.")
    
    cur.close()
    conn.close()
    
finally:
    db.close()

print("\n" + "=" * 70)


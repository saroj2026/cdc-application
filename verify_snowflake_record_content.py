"""Verify data in Snowflake RECORD_CONTENT column."""

import snowflake.connector
import psycopg2
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Verifying Data in Snowflake RECORD_CONTENT")
print("=" * 70)

try:
    # Get Snowflake connection details
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT host, username, password, database, schema, additional_config
        FROM connections
        WHERE name = 'snowflake-s' AND database_type = 'snowflake'
    """)
    
    row = cursor.fetchone()
    host, username, password, db, schema, additional_config = row
    
    if isinstance(additional_config, str):
        additional_config = json.loads(additional_config)
    elif additional_config is None:
        additional_config = {}
    
    account = host or additional_config.get('account', '')
    account = account.replace("https://", "").replace("http://", "")
    account = account.replace(".snowflakecomputing.com", "")
    account = account.rstrip('/')
    
    private_key = additional_config.get('private_key')
    warehouse = additional_config.get('warehouse', '')
    role = additional_config.get('role', '')
    
    cursor.close()
    conn.close()
    
    # Connect to Snowflake
    connect_params = {
        'account': account,
        'user': username,
        'database': db,
        'schema': schema or 'public',
    }
    
    if private_key:
        private_key_pem = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        private_key_bytes = private_key_pem.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        connect_params['private_key'] = private_key_bytes
    
    if warehouse:
        connect_params['warehouse'] = warehouse
    if role:
        connect_params['role'] = role
    
    sf_conn = snowflake.connector.connect(**connect_params)
    sf_cursor = sf_conn.cursor()
    
    # Check table structure
    print("\n1. Checking table structure...")
    sf_cursor.execute("DESCRIBE TABLE projects_simple")
    columns = sf_cursor.fetchall()
    
    print(f"   Columns ({len(columns)}):")
    for col in columns:
        col_name, data_type, nullable = col[0], col[1], col[3]
        print(f"      - {col_name}: {data_type} ({nullable})")
    
    # Check if RECORD_CONTENT exists
    has_record_content = any(col[0] == 'RECORD_CONTENT' for col in columns)
    
    if not has_record_content:
        print("\n   ⚠️  RECORD_CONTENT column not found!")
        print("   The connector should have created it. Checking row count...")
    
    # Check row count
    print("\n2. Checking row count...")
    sf_cursor.execute("SELECT COUNT(*) FROM projects_simple")
    count = sf_cursor.fetchone()[0]
    print(f"   Total rows: {count}")
    
    if count > 0:
        # Check RECORD_CONTENT data
        if has_record_content:
            print("\n3. Checking RECORD_CONTENT data...")
            sf_cursor.execute("""
                SELECT RECORD_CONTENT, 
                       RECORD_CONTENT:after AS after_data
                FROM projects_simple 
                LIMIT 3
            """)
            
            rows = sf_cursor.fetchall()
            print(f"   Found {len(rows)} rows with data")
            
            for i, row in enumerate(rows, 1):
                record_content = row[0]
                after_data = row[1]
                print(f"\n   Row {i}:")
                if record_content:
                    print(f"      RECORD_CONTENT: {str(record_content)[:200]}...")
                if after_data:
                    print(f"      After data: {str(after_data)[:200]}...")
        else:
            # Check regular columns
            print("\n3. Checking data in regular columns...")
            sf_cursor.execute("SELECT * FROM projects_simple LIMIT 3")
            rows = sf_cursor.fetchall()
            print(f"   Found {len(rows)} rows")
            for i, row in enumerate(rows, 1):
                print(f"   Row {i}: {row}")
    else:
        print("\n   ⚠️  No rows found in table")
        print("   The connector may not have written data yet")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


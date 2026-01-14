"""Modify Snowflake table to work with connector - add RECORD_CONTENT column."""

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
print("Modifying Snowflake Table for Connector")
print("=" * 70)

try:
    # Get Snowflake connection details
    print("\n1. Getting Snowflake connection details...")
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
    print("\n2. Connecting to Snowflake...")
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
    print("   ✅ Connected to Snowflake")
    
    # Check if table exists
    print("\n3. Checking current table structure...")
    try:
        sf_cursor.execute("DESCRIBE TABLE projects_simple")
        columns = sf_cursor.fetchall()
        print(f"   Table exists with {len(columns)} columns")
        
        # Check if RECORD_CONTENT exists
        has_record_content = any(col[0] == 'RECORD_CONTENT' for col in columns)
        
        if has_record_content:
            print("   ✅ RECORD_CONTENT column already exists")
        else:
            print("   ⚠️  RECORD_CONTENT column missing")
            print("\n4. Adding RECORD_CONTENT column...")
            sf_cursor.execute("ALTER TABLE projects_simple ADD COLUMN RECORD_CONTENT VARIANT")
            print("   ✅ RECORD_CONTENT column added")
            
            # Make other columns nullable (Snowflake requirement)
            print("\n5. Making existing columns nullable (Snowflake connector requirement)...")
            for col in columns:
                col_name = col[0]
                if col_name != 'RECORD_CONTENT' and col[3] == 'NOT NULL':
                    try:
                        sf_cursor.execute(f"ALTER TABLE projects_simple ALTER COLUMN {col_name} DROP NOT NULL")
                        print(f"   ✅ Made {col_name} nullable")
                    except Exception as e:
                        print(f"   ⚠️  Could not make {col_name} nullable: {e}")
    except Exception as e:
        if "does not exist" in str(e):
            print("   Table does not exist - connector will auto-create it")
        else:
            print(f"   Error: {e}")
    
    sf_cursor.close()
    sf_conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Table modification complete!")
    print("=" * 70)
    print("\nThe table now has RECORD_CONTENT column.")
    print("The connector will store Debezium envelope in RECORD_CONTENT.")
    print("You can extract 'after' field using:")
    print("  SELECT RECORD_CONTENT:after FROM projects_simple")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


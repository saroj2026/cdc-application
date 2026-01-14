"""Verify CDC is working - check data in Snowflake."""

import snowflake.connector
import psycopg2
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Get connection details
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Verifying CDC: PostgreSQL -> Kafka -> Snowflake")
print("=" * 70)

try:
    # Get Snowflake connection details
    print("\n1. Getting connection details...")
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
    
    # Check PostgreSQL source
    print("\n2. Checking PostgreSQL source table...")
    pg_conn = psycopg2.connect(**DB_CONFIG)
    pg_cursor = pg_conn.cursor()
    
    pg_cursor.execute("SELECT COUNT(*) FROM public.projects_simple")
    pg_count = pg_cursor.fetchone()[0]
    print(f"   PostgreSQL rows: {pg_count}")
    
    pg_cursor.execute("SELECT * FROM public.projects_simple ORDER BY project_id LIMIT 5")
    pg_rows = pg_cursor.fetchall()
    print(f"\n   Sample rows from PostgreSQL:")
    for row in pg_rows:
        print(f"      {row}")
    
    pg_cursor.close()
    pg_conn.close()
    
    # Check Snowflake target
    print("\n3. Checking Snowflake target table...")
    
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
    
    try:
        sf_cursor.execute("SELECT COUNT(*) FROM projects_simple")
        sf_count = sf_cursor.fetchone()[0]
        print(f"   Snowflake rows: {sf_count}")
        
        if sf_count > 0:
            sf_cursor.execute("SELECT * FROM projects_simple ORDER BY project_id LIMIT 5")
            sf_rows = sf_cursor.fetchall()
            print(f"\n   Sample rows from Snowflake:")
            for row in sf_rows:
                print(f"      {row}")
        else:
            print("   ⚠️  No rows in Snowflake yet")
            print("   This might mean:")
            print("      - CDC is still processing")
            print("      - No new changes since connector started")
            print("      - Check connector logs for issues")
        
        # Compare counts
        print(f"\n4. Comparison:")
        print(f"   PostgreSQL: {pg_count} rows")
        print(f"   Snowflake: {sf_count} rows")
        
        if sf_count > 0:
            print(f"   ✅ CDC is working! Data is flowing to Snowflake")
        elif pg_count > 0:
            print(f"   ⚠️  PostgreSQL has data but Snowflake doesn't")
            print(f"   This could mean:")
            print(f"      - Connector just started (wait a bit)")
            print(f"      - Only new changes are replicated (not existing data)")
            print(f"      - Check connector status and logs")
        else:
            print(f"   ℹ️  No data in either table yet")
        
    except Exception as e:
        print(f"   ❌ Error querying Snowflake: {e}")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


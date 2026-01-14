"""Create Snowflake table for projects_simple."""

import snowflake.connector
import psycopg2
import json

# Get Snowflake connection details from database
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Creating Snowflake Table")
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
    if not row:
        print("   ❌ Snowflake connection not found!")
        exit(1)
    
    host, username, password, db, schema, additional_config = row
    
    # Parse additional_config
    if isinstance(additional_config, str):
        additional_config = json.loads(additional_config)
    elif additional_config is None:
        additional_config = {}
    
    account = host or additional_config.get('account', '')
    warehouse = additional_config.get('warehouse', '')
    role = additional_config.get('role', '')
    private_key = additional_config.get('private_key')
    
    # Format account
    account = account.replace("https://", "").replace("http://", "")
    account = account.replace(".snowflakecomputing.com", "")
    account = account.rstrip('/')
    
    print(f"   Account: {account}")
    print(f"   Username: {username}")
    print(f"   Database: {db}")
    print(f"   Schema: {schema or 'public'}")
    
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
        # Use private key authentication
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        
        # Parse private key
        private_key_pem = serialization.load_pem_private_key(
            private_key.encode('utf-8'),
            password=None,
            backend=default_backend()
        )
        
        # Get private key bytes
        private_key_bytes = private_key_pem.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        connect_params['private_key'] = private_key_bytes
        print("   Using private key authentication")
    else:
        connect_params['password'] = password
        print("   Using password authentication")
    
    if warehouse:
        connect_params['warehouse'] = warehouse
    if role:
        connect_params['role'] = role
    
    sf_conn = snowflake.connector.connect(**connect_params)
    sf_cursor = sf_conn.cursor()
    print("   ✅ Connected to Snowflake")
    
    # Create table
    print("\n3. Creating table: projects_simple")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS projects_simple (
        PROJECT_ID INTEGER,
        PROJECT_NAME VARCHAR(100),
        DEPARTMENT_ID INTEGER,
        EMPLOYEE_ID INTEGER,
        START_DATE DATE,
        END_DATE DATE,
        STATUS VARCHAR(20)
    )
    """
    
    try:
        sf_cursor.execute(create_table_sql)
        print("   ✅ Table created successfully")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("   ⚠️  Table already exists")
        else:
            print(f"   ❌ Error creating table: {e}")
            raise
    
    # Verify table exists
    print("\n4. Verifying table...")
    sf_cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.tables 
        WHERE table_schema = CURRENT_SCHEMA() 
        AND table_name = 'PROJECTS_SIMPLE'
    """)
    
    exists = sf_cursor.fetchone()[0] > 0
    if exists:
        print("   ✅ Table verified")
        
        # Get column info
        sf_cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = CURRENT_SCHEMA()
            AND table_name = 'PROJECTS_SIMPLE'
            ORDER BY ordinal_position
        """)
        
        columns = sf_cursor.fetchall()
        print(f"\n   Table has {len(columns)} columns:")
        for col_name, data_type, max_len in columns:
            type_str = f"{data_type}({max_len})" if max_len else data_type
            print(f"      - {col_name}: {type_str}")
    else:
        print("   ⚠️  Table not found after creation")
    
    sf_cursor.close()
    sf_conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Snowflake table created successfully!")
    print("=" * 70)
    print("\nNext step: Restart the sink connector to pick up the new table")
    
except ImportError:
    print("\n❌ Error: snowflake-connector-python not installed")
    print("\nInstall it with:")
    print("  pip install snowflake-connector-python")
    print("\nOr create the table manually in Snowflake using the SQL from check_source_table_schema.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nAlternative: Create the table manually in Snowflake:")
    print("CREATE TABLE IF NOT EXISTS seg.public.projects_simple (")
    print("    PROJECT_ID INTEGER,")
    print("    PROJECT_NAME VARCHAR(100),")
    print("    DEPARTMENT_ID INTEGER,")
    print("    EMPLOYEE_ID INTEGER,")
    print("    START_DATE DATE,")
    print("    END_DATE DATE,")
    print("    STATUS VARCHAR(20)")
    print(");")


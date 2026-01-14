"""Query the specific record in Snowflake to show how to access it."""

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

PROJECT_ID = 9000

print("=" * 70)
print(f"Querying Record in Snowflake (Project ID: {PROJECT_ID})")
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
    
    print("\n1. Querying record using RECORD_CONTENT:project_id...")
    sf_cursor.execute("""
        SELECT 
            RECORD_CONTENT:project_id::NUMBER as project_id,
            RECORD_CONTENT:project_name::STRING as project_name,
            RECORD_CONTENT:department_id::NUMBER as department_id,
            RECORD_CONTENT:employee_id::NUMBER as employee_id,
            RECORD_CONTENT:start_date::NUMBER as start_date_raw,
            RECORD_CONTENT:end_date::STRING as end_date,
            RECORD_CONTENT:status::STRING as status,
            RECORD_CONTENT,
            RECORD_METADATA
        FROM projects_simple 
        WHERE RECORD_CONTENT:project_id = %s
    """, (PROJECT_ID,))
    
    records = sf_cursor.fetchall()
    
    if records:
        print(f"   ✅ Found {len(records)} record(s):\n")
        for i, record in enumerate(records, 1):
            print(f"   Record {i}:")
            print(f"      Project ID: {record[0]}")
            print(f"      Project Name: {record[1]}")
            print(f"      Department ID: {record[2]}")
            print(f"      Employee ID: {record[3]}")
            print(f"      Start Date (raw): {record[4]}")
            print(f"      End Date: {record[5]}")
            print(f"      Status: {record[6]}")
            print(f"\n      Full RECORD_CONTENT:")
            print(f"      {json.dumps(json.loads(str(record[7])), indent=6)}")
            print(f"\n      RECORD_METADATA (Kafka info):")
            print(f"      {json.dumps(json.loads(str(record[8])), indent=6) if record[8] else 'None'}")
    else:
        print(f"   ❌ Record not found")
    
    print("\n" + "=" * 70)
    print("SQL Query to Use in Snowflake:")
    print("=" * 70)
    print(f"""
-- Query the record by project_id:
SELECT 
    RECORD_CONTENT:project_id::NUMBER as project_id,
    RECORD_CONTENT:project_name::STRING as project_name,
    RECORD_CONTENT:department_id::NUMBER as department_id,
    RECORD_CONTENT:employee_id::NUMBER as employee_id,
    RECORD_CONTENT:start_date::NUMBER as start_date,
    RECORD_CONTENT:end_date::STRING as end_date,
    RECORD_CONTENT:status::STRING as status
FROM projects_simple 
WHERE RECORD_CONTENT:project_id = {PROJECT_ID};

-- Or get all records:
SELECT * FROM projects_simple;
""")
    
    sf_cursor.close()
    sf_conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


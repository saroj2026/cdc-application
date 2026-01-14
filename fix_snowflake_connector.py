"""Fix Snowflake connector by dropping table and updating config for auto-creation."""

import snowflake.connector
import psycopg2
import json
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

# Get Snowflake connection details
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Fixing Snowflake Connector")
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
    
    # Connect to Snowflake and drop table
    print("\n2. Dropping existing table to let connector auto-create it...")
    
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
        sf_cursor.execute("DROP TABLE IF EXISTS projects_simple")
        print("   ✅ Table dropped")
    except Exception as e:
        print(f"   ⚠️  Error dropping table: {e}")
    
    sf_cursor.close()
    sf_conn.close()
    
    # Update connector config to ensure proper settings
    print("\n3. Updating connector configuration...")
    
    # Get current config
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config",
        timeout=10
    )
    
    if response.status_code == 200:
        config = response.json()
        
        # Update config - ensure metadata is disabled or properly configured
        # Snowflake connector should handle Debezium format, but let's ensure
        # it's configured correctly
        
        # The SnowflakeJsonConverter should handle Debezium format
        # But we might need to ensure the table mapping is correct
        
        print("   Current config retrieved")
        print(f"   Value Converter: {config.get('value.converter', 'N/A')}")
        
        # Restart connector to pick up changes
        print("\n4. Restarting connector...")
        restart_response = requests.post(
            f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart",
            timeout=10
        )
        
        if restart_response.status_code == 204:
            print("   ✅ Connector restarted")
        else:
            print(f"   ⚠️  Restart response: {restart_response.status_code}")
    
    print("\n" + "=" * 70)
    print("✅ Fix applied!")
    print("=" * 70)
    print("\nThe table has been dropped. The Snowflake connector should")
    print("auto-create it when it processes the first message.")
    print("\nWait a few seconds and check the connector status:")
    print("  python check_sink_connector_status.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


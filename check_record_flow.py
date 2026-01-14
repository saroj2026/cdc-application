"""Check why a specific record is not appearing in Snowflake."""

import psycopg2
import requests
import snowflake.connector
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
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "sink-ps_sn_p-snowflake-public"

print("=" * 70)
print(f"Checking Record Flow for Project ID: {PROJECT_ID}")
print("=" * 70)

try:
    # 1. Check PostgreSQL
    print("\n1. Checking PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT project_id, project_name, department_id, employee_id, start_date, end_date, status
        FROM projects_simple 
        WHERE project_id = %s
    """, (PROJECT_ID,))
    
    pg_record = cursor.fetchone()
    if pg_record:
        print(f"   ✅ Record found in PostgreSQL:")
        print(f"      Project ID: {pg_record[0]}")
        print(f"      Project Name: {pg_record[1]}")
        print(f"      Department ID: {pg_record[2]}")
        print(f"      Employee ID: {pg_record[3]}")
        print(f"      Start Date: {pg_record[4]}")
        print(f"      End Date: {pg_record[5]}")
        print(f"      Status: {pg_record[6]}")
    else:
        print(f"   ❌ Record NOT found in PostgreSQL")
        cursor.close()
        conn.close()
        exit(1)
    
    cursor.close()
    conn.close()
    
    # 2. Check connector status
    print("\n2. Checking Snowflake connector status...")
    response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status",
        timeout=10
    )
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status['connector']['state']
        task_state = status['tasks'][0]['state'] if status.get('tasks') else 'UNKNOWN'
        
        print(f"   Connector State: {connector_state}")
        print(f"   Task State: {task_state}")
        
        if task_state == 'FAILED':
            error_trace = status['tasks'][0].get('trace', '')
            print(f"   ❌ Task FAILED!")
            print(f"   Error: {error_trace[:500]}")
        elif connector_state == 'RUNNING' and task_state == 'RUNNING':
            print(f"   ✅ Connector is RUNNING")
        else:
            print(f"   ⚠️  Connector state: {connector_state}, Task state: {task_state}")
    else:
        print(f"   ❌ Error checking connector status: {response.status_code}")
    
    # 3. Check Snowflake
    print("\n3. Checking Snowflake...")
    
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
    
    # Check if record exists in Snowflake
    sf_cursor.execute("""
        SELECT RECORD_CONTENT, RECORD_METADATA
        FROM projects_simple 
        WHERE RECORD_CONTENT:project_id = %s
    """, (PROJECT_ID,))
    
    sf_records = sf_cursor.fetchall()
    
    if sf_records:
        print(f"   ✅ Record found in Snowflake ({len(sf_records)} row(s)):")
        for i, record in enumerate(sf_records, 1):
            record_content = record[0]
            print(f"\n   Row {i}:")
            print(f"      RECORD_CONTENT: {str(record_content)[:300]}...")
    else:
        print(f"   ❌ Record NOT found in Snowflake")
        print(f"   This means CDC hasn't replicated it yet or there's an issue")
        
        # Check total row count
        sf_cursor.execute("SELECT COUNT(*) FROM projects_simple")
        total_count = sf_cursor.fetchone()[0]
        print(f"\n   Total rows in Snowflake: {total_count}")
        
        # Check recent records
        print(f"\n   Checking recent records...")
        sf_cursor.execute("""
            SELECT RECORD_CONTENT:project_id, RECORD_CONTENT:project_name, RECORD_CONTENT:status
            FROM projects_simple 
            ORDER BY RECORD_METADATA:offset DESC
            LIMIT 5
        """)
        recent = sf_cursor.fetchall()
        if recent:
            print(f"   Recent records:")
            for rec in recent:
                print(f"      Project ID: {rec[0]}, Name: {rec[1]}, Status: {rec[2]}")
    
    sf_cursor.close()
    sf_conn.close()
    
    # 4. Recommendations
    print("\n" + "=" * 70)
    print("Diagnosis Summary")
    print("=" * 70)
    
    if pg_record and not sf_records:
        print("\n⚠️  Record exists in PostgreSQL but NOT in Snowflake")
        print("\nPossible reasons:")
        print("1. Connector is not processing messages (check task state)")
        print("2. Message is stuck in Kafka (check consumer lag)")
        print("3. Connector error (check logs)")
        print("4. Record was inserted before connector started")
        print("\nRecommendations:")
        print("- Check connector logs for errors")
        print("- Verify consumer group is active")
        print("- Try updating the record to trigger a new CDC event")
        print("- Check Kafka topic for the message")
    elif pg_record and sf_records:
        print("\n✅ Record found in both PostgreSQL and Snowflake - CDC is working!")
    elif not pg_record:
        print("\n❌ Record not found in PostgreSQL - check your insert statement")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


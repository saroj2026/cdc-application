"""Fix Sink connector transform chain to properly extract Debezium after field."""

import requests
import json
import time
import pyodbc

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR_NAME = "sink-pg_to_mssql_projects_simple-mssql-dbo"

MSSQL_CONFIG = {
    "server": "72.61.233.209",
    "port": 1433,
    "database": "cdctest",
    "username": "sa",
    "password": "Sql@12345",
    "trust_server_certificate": True
}

print("="*80)
print("Fixing Sink Connector Transform Chain")
print("="*80)

try:
    # Get current config
    print("\n1. Getting current configuration...")
    get_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}"
    response = requests.get(get_url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        config = data.get('config', {})
        print("   [OK] Got current config")
    else:
        print(f"   [ERROR] Failed to get config: {response.status_code}")
        exit(1)
    
    # Update config - try simpler approach: just extract 'after' from root
    # With schemas, Debezium format is: {schema: {...}, payload: {after: {...}}}
    # ExtractField$Value works on the value, which IS the payload when schemas are enabled
    # So 'after' should work directly
    
    print("\n2. Updating transform configuration...")
    print("   Trying: Extract 'after' field directly (Debezium with schemas)")
    
    updated_config = config.copy()
    updated_config["transforms"] = "extractAfter"
    updated_config["transforms.extractAfter.type"] = "org.apache.kafka.connect.transforms.ExtractField$Value"
    updated_config["transforms.extractAfter.field"] = "after"  # Back to 'after' - should work with schemas
    
    # Also ensure value converter is correct
    updated_config["value.converter"] = "org.apache.kafka.connect.json.JsonConverter"
    updated_config["value.converter.schemas.enable"] = "true"
    
    print(f"   Transforms: {updated_config['transforms']}")
    print(f"   Extract field: {updated_config['transforms.extractAfter.field']}")
    
    # Update connector
    print("\n3. Updating connector...")
    put_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/config"
    response = requests.put(
        put_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(updated_config),
        timeout=30
    )
    
    if response.status_code in [200, 201]:
        print("   [OK] Configuration updated")
    else:
        print(f"   [ERROR] Failed to update: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
    
    # Restart
    print("\n4. Restarting connector...")
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    
    if response.status_code == 204:
        print("   [OK] Restart command sent")
    else:
        print(f"   [WARN] Restart response: {response.status_code}")
    
    # Wait and check
    print("\n5. Waiting 15 seconds for processing...")
    time.sleep(15)
    
    print("\n6. Checking SQL Server for row 110...")
    mssql_conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={MSSQL_CONFIG['server']},{MSSQL_CONFIG['port']};"
        f"DATABASE={MSSQL_CONFIG['database']};"
        f"UID={MSSQL_CONFIG['username']};"
        f"PWD={MSSQL_CONFIG['password']};"
        f"TrustServerCertificate=yes;"
    )
    
    found = False
    for attempt in range(1, 4):
        try:
            mssql_conn = pyodbc.connect(mssql_conn_str, timeout=10)
            mssql_cur = mssql_conn.cursor()
            
            mssql_cur.execute("SELECT * FROM dbo.projects_simple WHERE project_id = ?", (110,))
            row = mssql_cur.fetchone()
            
            if row:
                columns = [column[0] for column in mssql_cur.description]
                row_dict = dict(zip(columns, row))
                print(f"   [OK] Row found in SQL Server!")
                print(f"   {row_dict}")
                found = True
                mssql_cur.close()
                mssql_conn.close()
                break
            else:
                print(f"   [WARN] Row not found (attempt {attempt}/3)...")
                mssql_cur.close()
                mssql_conn.close()
                time.sleep(5)
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
            time.sleep(5)
    
    # Summary
    print("\n" + "="*80)
    if found:
        print("[OK] SUCCESS: Row 110 is now in SQL Server!")
        print("CDC flow is working: PostgreSQL -> Debezium -> Kafka -> Sink -> SQL Server")
    else:
        print("[ERROR] Row still not in SQL Server")
        print("\nThe issue is likely:")
        print("  1. Message format in Kafka doesn't match what ExtractField expects")
        print("  2. The 'after' field structure is different")
        print("  3. There are errors in Sink connector logs (check server logs)")
        print("\nTo diagnose:")
        print("  - Check actual Kafka message format")
        print("  - Check Kafka Connect worker logs on 72.61.233.209")
        print("  - Look for transform or SQL insert errors")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


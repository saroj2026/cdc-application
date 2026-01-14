"""Fix publication and restart Debezium connector."""

import psycopg2
import requests
import json
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-pg_to_mssql_projects_simple-pg-public"
PUBLICATION_NAME = "pg_to_mssql_projects_simple_pub"

print("="*80)
print("Fixing Publication and Restarting Debezium")
print("="*80)

try:
    # Step 1: Check current publication
    print("\n1. Checking current publication...")
    conn = psycopg2.connect(
        host="72.61.233.209",
        port=5432,
        database="cdctest",
        user="cdc_user",
        password="cdc_pass"
    )
    cur = conn.cursor()
    
    cur.execute("""
        SELECT pubname, puballtables 
        FROM pg_publication 
        WHERE pubname = %s
    """, (PUBLICATION_NAME,))
    pub = cur.fetchone()
    
    if pub:
        print(f"   Publication exists: {pub[0]}, all_tables: {pub[1]}")
        
        # Check if table is in publication
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_publication_tables 
            WHERE pubname = %s AND tablename = 'projects_simple'
        """, (PUBLICATION_NAME,))
        count = cur.fetchone()[0]
        
        if count > 0:
            print(f"   [OK] Table 'projects_simple' is in publication")
        else:
            print(f"   [ERROR] Table 'projects_simple' is NOT in publication!")
            print("   Adding table to publication...")
            cur.execute(f"ALTER PUBLICATION {PUBLICATION_NAME} ADD TABLE public.projects_simple")
            conn.commit()
            print("   [OK] Table added to publication")
    else:
        print(f"   [ERROR] Publication '{PUBLICATION_NAME}' does not exist!")
        print("   Creating publication...")
        cur.execute(f"CREATE PUBLICATION {PUBLICATION_NAME} FOR TABLE public.projects_simple")
        conn.commit()
        print("   [OK] Publication created")
    
    cur.close()
    conn.close()
    
    # Step 2: Restart Debezium connector
    print("\n2. Restarting Debezium connector...")
    restart_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart"
    response = requests.post(restart_url, timeout=30)
    
    if response.status_code == 204:
        print("   [OK] Restart command sent")
    else:
        print(f"   [WARN] Restart response: {response.status_code}")
    
    # Step 3: Wait and verify
    print("\n3. Waiting for connector to restart...")
    time.sleep(5)
    
    status_url = f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status"
    response = requests.get(status_url, timeout=10)
    
    if response.status_code == 200:
        status = response.json()
        connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state', 'UNKNOWN') if tasks else 'UNKNOWN'
        
        print(f"   Connector: {connector_state}")
        print(f"   Task: {task_state}")
        
        if connector_state == 'RUNNING' and task_state == 'RUNNING':
            print("\n   [OK] Connector is RUNNING")
        else:
            print("\n   [ERROR] Connector is not fully operational")
    
    print("\n" + "="*80)
    print("Next Steps")
    print("="*80)
    print("1. Make a NEW change to the table:")
    print("   INSERT INTO public.projects_simple VALUES (110, 'Test After Fix', 200, 101, CURRENT_DATE, NULL, 'ACTIVE');")
    print("\n2. Wait 5-10 seconds")
    print("\n3. Check if row appears in SQL Server")
    print("\n4. Verify Kafka topic has messages")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()


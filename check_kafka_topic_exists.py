"""Check if Kafka topic exists and verify connector is working."""

import requests
import psycopg2
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_UI_URL = "http://72.61.233.209:8080"

# Database connection
DB_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("Kafka Topic Verification for ps_sn_p Pipeline")
print("=" * 70)

# Expected topic name
expected_topic = "ps_sn_p.public.projects_simple"

print(f"\n1. Expected Topic: {expected_topic}")

# Check connector status
print(f"\n2. Checking Debezium Connector Status...")
connector_name = "cdc-ps_sn_p-pg-public"

try:
    status_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/status",
        timeout=10
    )
    
    if status_response.status_code == 200:
        status = status_response.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {connector_state}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_state = task.get('state', 'N/A')
            print(f"   Task {task.get('id')}: {task_state}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                print(f"      Error: {trace[:300]}")
    
    # Get connector config
    config_response = requests.get(
        f"{KAFKA_CONNECT_URL}/connectors/{connector_name}/config",
        timeout=10
    )
    
    if config_response.status_code == 200:
        config = config_response.json()
        print(f"\n3. Connector Configuration:")
        print(f"   Topic Prefix: {config.get('topic.prefix')}")
        print(f"   Table Include: {config.get('table.include.list')}")
        print(f"   Publication: {config.get('publication.name')}")
        print(f"   Slot Name: {config.get('slot.name')}")
        print(f"   Snapshot Mode: {config.get('snapshot.mode')}")
        
except Exception as e:
    print(f"   Error: {e}")

# Check PostgreSQL publication and slot
print(f"\n4. Checking PostgreSQL Publication and Replication Slot...")
try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check publication
    cursor.execute("""
        SELECT pubname, puballtables, pubinsert, pubupdate, pubdelete, pubtruncate
        FROM pg_publication
        WHERE pubname = 'ps_sn_p_pub'
    """)
    publication = cursor.fetchone()
    
    if publication:
        print(f"   ✅ Publication 'ps_sn_p_pub' exists")
        print(f"      All Tables: {publication[1]}")
        
        # Check publication tables
        cursor.execute("""
            SELECT schemaname, tablename
            FROM pg_publication_tables
            WHERE pubname = 'ps_sn_p_pub'
        """)
        pub_tables = cursor.fetchall()
        print(f"      Tables in publication: {len(pub_tables)}")
        for table in pub_tables:
            print(f"         - {table[0]}.{table[1]}")
    else:
        print(f"   ❌ Publication 'ps_sn_p_pub' NOT found")
    
    # Check replication slot
    cursor.execute("""
        SELECT slot_name, slot_type, active, database, plugin
        FROM pg_replication_slots
        WHERE slot_name = 'ps_sn_p_slot'
    """)
    slot = cursor.fetchone()
    
    if slot:
        print(f"   ✅ Replication Slot 'ps_sn_p_slot' exists")
        print(f"      Active: {slot[2]}")
        print(f"      Plugin: {slot[4]}")
    else:
        print(f"   ❌ Replication Slot 'ps_sn_p_slot' NOT found")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   Error checking PostgreSQL: {e}")

# Recommendation
print(f"\n5. Recommendations:")
print(f"   - Topics are created when Debezium captures the first change event")
print(f"   - If snapshot.mode is 'never', topic won't be created until a change occurs")
print(f"   - Try inserting/updating a row in cdctest.public.projects_simple")
print(f"   - Or check Kafka broker directly for topic existence")

print("\n" + "=" * 70)
print(f"Kafka UI: {KAFKA_UI_URL}")
print("Check Topics page to see if topic exists there")
print("=" * 70)



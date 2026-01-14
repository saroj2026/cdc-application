"""Fix stuck CDC by recreating the replication slot."""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
PIPELINE_NAME = "pg_to_mssql_projects_simple"
DEBEZIUM_CONNECTOR = f"cdc-{PIPELINE_NAME}-pg-public"
SLOT_NAME = f"{PIPELINE_NAME}_slot"

PG_CONFIG = {
    "host": "72.61.233.209",
    "port": 5432,
    "database": "cdctest",
    "user": "cdc_user",
    "password": "cdc_pass"
}

print("=" * 70)
print("FIX STUCK CDC - Recreate Replication Slot")
print("=" * 70)

print("\n⚠️  WARNING: This will:")
print("   1. Delete the existing replication slot")
print("   2. Stop the Debezium connector")
print("   3. Recreate the slot (will be done automatically when connector restarts)")
print("   4. Restart the connector")
print("\nThis will cause a brief interruption in CDC.")
print("\nProceed? (This script will show what would happen)")

# Step 1: Check current state
print("\n1. CURRENT STATE:")
print("-" * 70)

try:
    conn = psycopg2.connect(**PG_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute('''
        SELECT 
            slot_name,
            confirmed_flush_lsn,
            pg_current_wal_lsn() AS current_lsn,
            pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn) AS lag_bytes,
            active
        FROM pg_replication_slots
        WHERE slot_name = %s
    ''', (SLOT_NAME,))
    
    slot = cursor.fetchone()
    if slot:
        lag_kb = slot['lag_bytes'] / 1024
        print(f"   Slot: {slot['slot_name']}")
        print(f"   Lag: {lag_kb:.2f} KB")
        print(f"   Active: {slot['active']}")
        print(f"   ⚠️  Slot exists and has lag")
    else:
        print(f"   ✅ Slot does not exist (will be created)")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 2: Check connector
print("\n2. DEBEZIUM CONNECTOR:")
print("-" * 70)
try:
    status = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/status").json()
    state = status.get('connector', {}).get('state')
    print(f"   State: {state}")
    if state == 'RUNNING':
        print(f"   ⚠️  Connector is RUNNING (will be stopped)")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("TO FIX MANUALLY:")
print("=" * 70)
print("\nOption 1: Recreate Slot (Recommended)")
print("1. Stop Debezium connector:")
print(f"   curl -X PUT {KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/pause")
print("\n2. Delete replication slot in PostgreSQL:")
print(f"   SELECT pg_drop_replication_slot('{SLOT_NAME}');")
print("\n3. Restart Debezium connector:")
print(f"   curl -X PUT {KAFKA_CONNECT_URL}/connectors/{DEBEZIUM_CONNECTOR}/resume")
print("\n4. Debezium will automatically recreate the slot")

print("\n" + "=" * 70)
print("Option 2: Restart Kafka Connect Service")
print("=" * 70)
print("SSH to server and restart:")
print("  ssh ssh@72.61.233.209")
print("  docker restart kafka-connect-cdc")
print("  # Or")
print("  docker-compose restart kafka-connect")

print("\n" + "=" * 70)
print("Option 3: Check Kafka Connect Logs")
print("=" * 70)
print("SSH to server and check logs:")
print("  ssh ssh@72.61.233.209")
print("  docker logs kafka-connect-cdc | tail -100")
print("  docker logs kafka-connect-cdc | grep -i error")

print("\n" + "=" * 70)



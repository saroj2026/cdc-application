#!/usr/bin/env python3
"""Verify complete CDC flow: Oracle -> Kafka -> Snowflake."""

import requests
from ingestion.connectors.snowflake import SnowflakeConnector
from ingestion.database.models_db import ConnectionModel
from ingestion.database.session import SessionLocal

KAFKA_UI_URL = "http://72.61.233.209:8080"
KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CORRECT_TOPIC = "oracle_sf_p.CDC_USER.TEST"

print("=" * 70)
print("COMPLETE CDC FLOW VERIFICATION")
print("=" * 70)

# 1. Check Kafka Topic
print("\n1. Kafka Topic Status:")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{CORRECT_TOPIC}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            message_count = offset_max - offset_min
            print(f"   Topic: {CORRECT_TOPIC}")
            print(f"   Messages: {message_count}")
            print(f"   Status: {'✓ HAS MESSAGES' if message_count > 0 else '⚠ EMPTY'}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Check Source Connector
print("\n2. Source Connector Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/status")
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state') if tasks else 'UNKNOWN'
        print(f"   State: {connector_state}")
        print(f"   Task state: {task_state}")
        print(f"   Status: {'✓ RUNNING' if connector_state == 'RUNNING' and task_state == 'RUNNING' else '⚠ NOT RUNNING'}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Check Sink Connector
print("\n3. Sink Connector Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-oracle_sf_p-snow-public/status")
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state')
        tasks = status.get('tasks', [])
        task_state = tasks[0].get('state') if tasks else 'UNKNOWN'
        config_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/sink-oracle_sf_p-snow-public/config")
        config = config_r.json()
        topics = config.get('topics', '')
        
        print(f"   State: {connector_state}")
        print(f"   Task state: {task_state}")
        print(f"   Topics: {topics}")
        print(f"   Status: {'✓ RUNNING' if connector_state == 'RUNNING' and task_state == 'RUNNING' else '⚠ NOT RUNNING'}")
        print(f"   Topic match: {'✓ MATCHES' if topics == CORRECT_TOPIC else '⚠ MISMATCH'}")
except Exception as e:
    print(f"   Error: {e}")

# 4. Check Snowflake
print("\n4. Snowflake Status:")
db = SessionLocal()
try:
    sf = db.query(ConnectionModel).filter_by(name='snowflake-s').first()
    config = {
        'host': sf.host,
        'port': sf.port,
        'database': sf.database,
        'user': sf.username,
        'password': sf.password,
        'account': sf.additional_config.get('account'),
        'private_key': sf.additional_config.get('private_key')
    }
    
    conn = SnowflakeConnector(config).connect()
    cur = conn.cursor()
    cur.execute('USE DATABASE SEG')
    cur.execute('USE SCHEMA PUBLIC')
    
    cur.execute('SELECT COUNT(*) FROM TEST')
    total_count = cur.fetchone()[0]
    
    cur.execute("""
        SELECT 
            RECORD_METADATA:operation::STRING as op,
            COUNT(*) as count
        FROM TEST
        GROUP BY RECORD_METADATA:operation::STRING
    """)
    op_counts = {row[0] or 'N/A': row[1] for row in cur.fetchall()}
    
    print(f"   Total records: {total_count}")
    print(f"   Operation counts: {op_counts}")
    
    # Check for recent CDC events
    has_cdc = any(op in op_counts for op in ['c', 'u', 'd']) if op_counts else False
    print(f"   CDC events: {'✓ PRESENT' if has_cdc else '⚠ Only snapshot (r) operations'}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"   Error: {e}")
finally:
    db.close()

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

all_ok = True
if message_count > 0:
    print("✓ Kafka topic has messages")
else:
    print("⚠ Kafka topic is empty")
    all_ok = False

if connector_state == 'RUNNING' and task_state == 'RUNNING':
    print("✓ Source connector is RUNNING")
else:
    print("⚠ Source connector is not RUNNING")
    all_ok = False

if topics == CORRECT_TOPIC:
    print(f"✓ Sink connector configured correctly ({CORRECT_TOPIC})")
else:
    print(f"⚠ Sink connector topic mismatch")
    all_ok = False

if total_count > 0:
    print(f"✓ Snowflake has data ({total_count} records)")
else:
    print("⚠ Snowflake is empty")
    all_ok = False

if has_cdc:
    print("✓ CDC events detected in Snowflake")
else:
    print("⚠ Only snapshot data (no CDC events yet)")

print("\n" + "=" * 70)
if all_ok:
    print("✓✓✓ CDC PIPELINE IS WORKING!")
    print("   Data is flowing from Oracle -> Kafka -> Snowflake")
else:
    print("⚠ Some components need attention (see details above)")
print("=" * 70)


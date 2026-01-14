#!/usr/bin/env python3
"""Verify operations happened in Oracle and check if messages are in Kafka."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import oracledb
from ingestion.database.session import get_db
from ingestion.database.models_db import ConnectionModel, PipelineModel

print("=" * 70)
print("VERIFYING ORACLE OPERATIONS AND KAFKA MESSAGES")
print("=" * 70)

test_id = 73032

db = next(get_db())
try:
    pipeline = db.query(PipelineModel).filter_by(name="oracle_sf_p").first()
    oracle_conn_model = db.query(ConnectionModel).filter_by(id=pipeline.source_connection_id).first()
    oracle_config = oracle_conn_model.additional_config or {}
    
    print("\n1. Checking Oracle for Test ID 73032...")
    print("-" * 70)
    
    oracle_host = oracle_conn_model.host
    oracle_port = oracle_conn_model.port or 1521
    oracle_service = oracle_config.get('service_name') or 'XE'
    oracle_user = oracle_conn_model.username
    oracle_password = oracle_conn_model.password
    
    oracle_dsn = f"{oracle_host}:{oracle_port}/{oracle_service}"
    oracle_conn = oracledb.connect(
        user=oracle_user,
        password=oracle_password,
        dsn=oracle_dsn
    )
    
    oracle_cursor = oracle_conn.cursor()
    
    # Check if the record exists (it was deleted, so it shouldn't exist)
    oracle_cursor.execute("SELECT COUNT(*) FROM cdc_user.test WHERE id = :id", {'id': test_id})
    count = oracle_cursor.fetchone()[0]
    
    if count > 0:
        print(f"   ⚠ Record with ID {test_id} still exists in Oracle (should have been deleted)")
    else:
        print(f"   ✅ Record with ID {test_id} does NOT exist (correct - it was deleted)")
    
    # Check recent operations in Oracle (check redo logs or transaction history if possible)
    # For now, let's check the max ID to see if our test ID was used
    oracle_cursor.execute("SELECT NVL(MAX(id), 0) FROM cdc_user.test")
    max_id = oracle_cursor.fetchone()[0]
    
    print(f"   Current max ID in Oracle: {max_id}")
    if max_id >= test_id:
        print(f"   ✅ Test ID {test_id} was within the range (operations likely happened)")
    else:
        print(f"   ⚠ Test ID {test_id} is higher than max ID - operations may not have happened")
    
    # Check total count
    oracle_cursor.execute("SELECT COUNT(*) FROM cdc_user.test")
    total = oracle_cursor.fetchone()[0]
    print(f"   Total records in Oracle: {total}")
    
    oracle_cursor.close()
    oracle_conn.close()
    
except Exception as e:
    print(f"   ❌ Error checking Oracle: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n2. Next Steps to Check Kafka...")
print("-" * 70)
print("   To verify messages are in Kafka topic:")
print("   ")
print("   Option 1: Use Kafka UI")
print("   - Open: http://72.61.233.209:8080")
print("   - Go to Topics → oracle_sf_p.CDC_USER.TEST")
print("   - Check message count and view recent messages")
print("   ")
print("   Option 2: SSH to server and check")
print("   - ssh root@72.61.233.209")
print("   - docker exec -it kafka kafka-console-consumer \\")
print("       --bootstrap-server localhost:9092 \\")
print("       --topic oracle_sf_p.CDC_USER.TEST \\")
print("       --from-beginning --max-messages 20")
print("   ")
print("   Option 3: Check consumer group offsets")
print("   - docker exec -it kafka kafka-consumer-groups \\")
print("       --bootstrap-server localhost:9092 \\")
print("       --group connect-sink-oracle_sf_p-snow-public \\")
print("       --describe")
print("   ")
print("   This will show:")
print("   - Current offset (messages consumed)")
print("   - Log end offset (total messages)")
print("   - LAG (unprocessed messages)")

print("\n3. Possible Issues...")
print("-" * 70)
print("   If messages are NOT in Kafka:")
print("   - Debezium source connector may not be capturing changes")
print("   - Check Debezium connector logs for errors")
print("   - Verify Oracle LogMiner is active")
print("   ")
print("   If messages ARE in Kafka but not in Snowflake:")
print("   - Sink connector may have errors processing messages")
print("   - Check sink connector logs")
print("   - Verify Snowflake connection and permissions")
print("   - Check for schema mismatches")

print("\n" + "=" * 70)


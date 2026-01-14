#!/usr/bin/env python3
"""Check both Oracle topics: schema change topic and table topic."""

import requests

KAFKA_UI_URL = "http://72.61.233.209:8080"
SCHEMA_TOPIC = "oracle_sf_p"  # Schema change topic
TABLE_TOPIC = "oracle_sf_p.CDC_USER.TEST"  # Table data topic

print("=" * 70)
print("CHECKING BOTH ORACLE TOPICS")
print("=" * 70)

# Check schema change topic
print("\n1. Schema Change Topic (oracle_sf_p):")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{SCHEMA_TOPIC}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            message_count = offset_max - offset_min
            
            print(f"   Topic: {SCHEMA_TOPIC}")
            print(f"   Messages: {message_count}")
            print(f"   Offset range: {offset_min} to {offset_max}")
            print(f"   Purpose: Schema changes (CREATE TABLE, ALTER TABLE, etc.)")
            
            if message_count > 0:
                print(f"   ✓ Has {message_count} message(s) - schema changes captured")
    else:
        print(f"   Error: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Check table data topic
print("\n2. Table Data Topic (oracle_sf_p.CDC_USER.TEST):")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{TABLE_TOPIC}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            message_count = offset_max - offset_min
            
            print(f"   Topic: {TABLE_TOPIC}")
            print(f"   Messages: {message_count}")
            print(f"   Offset range: {offset_min} to {offset_max}")
            print(f"   Purpose: Table data changes (INSERT, UPDATE, DELETE)")
            
            if message_count > 3:
                new_messages = message_count - 3
                print(f"\n   ✓✓✓ NEW MESSAGES DETECTED: {new_messages} new message(s)!")
                print(f"   CDC changes ARE being captured!")
            elif message_count == 3:
                print(f"\n   ⚠ Still has {message_count} messages (same as before)")
                print(f"   No new CDC changes captured yet")
            else:
                print(f"   Current: {message_count} messages")
    else:
        print(f"   Error: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("EXPLANATION:")
print("=" * 70)
print("  There are 2 topics:")
print(f"  1. {SCHEMA_TOPIC} - Schema changes (DDL)")
print(f"  2. {TABLE_TOPIC} - Table data changes (DML - INSERT/UPDATE/DELETE)")
print("")
print("  The sink connector consumes from the TABLE topic (oracle_sf_p.CDC_USER.TEST)")
print("  The schema topic contains DDL changes, not data changes")
print("=" * 70)


#!/usr/bin/env python3
"""Check if source connector is actually producing to the table topic."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
KAFKA_UI_URL = "http://72.61.233.209:8080"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"
EXPECTED_TOPIC = "oracle_sf_p.CDC_USER.TEST"

print("=" * 70)
print("CHECKING SOURCE CONNECTOR TOPIC USAGE")
print("=" * 70)

# Check connector config
print("\n1. Connector Configuration:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
    if r.status_code == 200:
        config = r.json()
        table_include = config.get('table.include.list', 'N/A')
        server_name = config.get('database.server.name', 'N/A')
        print(f"   table.include.list: {table_include}")
        print(f"   database.server.name: {server_name}")
        print(f"   Expected topic format: {server_name}.{{schema}}.{{table}}")
        print(f"   Expected topic: {EXPECTED_TOPIC}")
    else:
        print(f"   Error: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Check connector topics API (what topics is it using)
print("\n2. Topics API Response (what topics connector reports):")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/topics")
    if r.status_code == 200:
        topics_data = r.json()
        print(f"   Response: {json.dumps(topics_data, indent=2)}")
        connector_topics = topics_data.get(CONNECTOR_NAME, {}).get('topics', [])
        print(f"\n   Topics reported by connector: {connector_topics}")
        
        if EXPECTED_TOPIC in connector_topics:
            print(f"   ✓ Expected topic {EXPECTED_TOPIC} is in the list!")
        else:
            print(f"   ✗ Expected topic {EXPECTED_TOPIC} is NOT in the list!")
            print(f"   This means the connector is NOT producing to this topic!")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check actual Kafka topic
print("\n3. Actual Kafka Topic Status:")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{EXPECTED_TOPIC}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            message_count = offset_max - offset_min
            
            print(f"   Topic: {EXPECTED_TOPIC}")
            print(f"   Messages: {message_count}")
            print(f"   Offset range: {offset_min} to {offset_max}")
            
            if message_count > 0:
                print(f"   ✓ Topic has messages (but may be from snapshot only)")
            else:
                print(f"   ✗ Topic has no messages!")
    else:
        print(f"   Error: Topic might not exist? {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Check all topics that match the pattern
print("\n4. All Topics Matching Pattern (oracle_sf_p.*):")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics")
    if r.status_code == 200:
        all_topics = r.json()
        matching_topics = [t for t in all_topics if t.startswith('oracle_sf_p')]
        print(f"   Found {len(matching_topics)} matching topic(s):")
        for topic in sorted(matching_topics):
            print(f"     - {topic}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("=" * 70)
print("If the connector's topics API returns an empty list or doesn't include")
print("the expected topic, it means the connector is NOT producing messages")
print("to that topic. This could be because:")
print("  1. Table name mismatch (config vs actual)")
print("  2. Schema name mismatch (config uses lowercase, Oracle creates uppercase)")
print("  3. Connector is in snapshot mode and hasn't started CDC streaming yet")
print("  4. LogMiner not properly configured to stream changes")
print("=" * 70)


#!/usr/bin/env python3
"""Verify connector topics are properly assigned."""

import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SOURCE_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"

print("=" * 70)
print("VERIFYING CONNECTOR TOPICS")
print("=" * 70)

# Check source connector topics
print("\n1. Source Connector Topics:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/topics")
    if r.status_code == 200:
        topics_data = r.json()
        source_topics = topics_data.get(SOURCE_CONNECTOR, {}).get('topics', [])
        print(f"   Topics: {source_topics}")
        print(f"   Count: {len(source_topics)}")
        
        # Filter table topics (exclude schema change topic)
        table_topics = [t for t in source_topics if '.' in t and t != 'oracle_sf_p']
        print(f"   Table topics: {table_topics}")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check sink connector config
print("\n2. Sink Connector Configuration:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
    if r.status_code == 200:
        config = r.json()
        sink_topics = config.get('topics', '')
        print(f"   Topics: {sink_topics}")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check if topics match
print("\n3. Topic Match Check:")
try:
    r1 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/topics")
    r2 = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
    
    if r1.status_code == 200 and r2.status_code == 200:
        source_topics_data = r1.json()
        sink_config = r2.json()
        
        source_topics = source_topics_data.get(SOURCE_CONNECTOR, {}).get('topics', [])
        table_topics = [t for t in source_topics if '.' in t and t != 'oracle_sf_p']
        sink_topics_str = sink_config.get('topics', '')
        sink_topics_list = [t.strip() for t in sink_topics_str.split(',') if t.strip()]
        
        print(f"   Source table topics: {table_topics}")
        print(f"   Sink topics: {sink_topics_list}")
        
        if set(table_topics) == set(sink_topics_list):
            print("   ✓ Topics match!")
        else:
            print("   ⚠ Topics don't match!")
            missing_in_sink = set(table_topics) - set(sink_topics_list)
            missing_in_source = set(sink_topics_list) - set(table_topics)
            if missing_in_sink:
                print(f"      Missing in sink: {missing_in_sink}")
            if missing_in_source:
                print(f"      Missing in source: {missing_in_source}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("NOTE: Kafka UI may not display topics in the 'Topics' column")
print("      This is often a UI display limitation, not a connector issue")
print("      The topics are still being used by the connector")
print("=" * 70)


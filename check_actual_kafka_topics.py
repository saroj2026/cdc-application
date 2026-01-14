#!/usr/bin/env python3
"""Check actual Kafka topics that exist in Kafka."""

import requests

KAFKA_UI_URL = "http://72.61.233.209:8080"

print("=" * 70)
print("CHECKING ACTUAL KAFKA TOPICS")
print("=" * 70)

# Get all topics from Kafka UI API
print("\n1. Getting all topics from Kafka...")
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics")
    if r.status_code == 200:
        topics = r.json()
        oracle_topics = [t for t in topics if 'oracle_sf_p' in t]
        
        print(f"   Total topics: {len(topics)}")
        print(f"   Oracle-related topics: {len(oracle_topics)}")
        
        if oracle_topics:
            print("\n   Oracle topics found:")
            for topic in sorted(oracle_topics):
                print(f"     - {topic}")
        else:
            print("\n   ⚠ No Oracle topics found!")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check the uppercase topic (what Oracle creates)
print("\n2. Checking uppercase topic (oracle_sf_p.CDC_USER.TEST):")
expected_topic = "oracle_sf_p.CDC_USER.TEST"
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{expected_topic}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            offset_min = partition.get('offsetMin', 0)
            print(f"   ✓ Topic exists!")
            print(f"   Messages: {offset_max - offset_min}")
            print(f"   Offset range: {offset_min} to {offset_max}")
            
            if offset_max > 0:
                print(f"   ✓ Topic has messages!")
            else:
                print(f"   ⚠ Topic exists but has no messages")
        else:
            print(f"   Topic exists but has no partitions")
    else:
        print(f"   ⚠ Topic not found (status: {r.status_code})")
except Exception as e:
    print(f"   Error: {e}")

# Check the lowercase topic (what UI might be showing)
print("\n3. Checking lowercase topic (oracle_sf_p.cdc_user.test):")
lowercase_topic = "oracle_sf_p.cdc_user.test"
try:
    r = requests.get(f"{KAFKA_UI_URL}/api/clusters/local/topics/{lowercase_topic}")
    if r.status_code == 200:
        topic_info = r.json()
        partitions = topic_info.get('partitions', [])
        if partitions:
            partition = partitions[0]
            offset_max = partition.get('offsetMax', 0)
            print(f"   ⚠ Lowercase topic exists!")
            print(f"   Messages: {offset_max}")
            print(f"   This might be the wrong topic - Oracle creates UPPERCASE topics")
    else:
        print(f"   ✓ Lowercase topic doesn't exist (expected)")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("IMPORTANT:")
print("  Oracle Debezium creates topics with UPPERCASE schema/table names")
print("  The correct topic name is: oracle_sf_p.CDC_USER.TEST (UPPERCASE)")
print("  NOT: oracle_sf_p.cdc_user.test (lowercase)")
print("=" * 70)


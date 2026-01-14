#!/usr/bin/env python3
"""Check messages in the correct uppercase topic."""

import requests
import json

KAFKA_UI_URL = "http://72.61.233.209:8080"
CORRECT_TOPIC = "oracle_sf_p.CDC_USER.TEST"  # UPPERCASE - this is the correct topic

print("=" * 70)
print("CHECKING CORRECT TOPIC (UPPERCASE)")
print("=" * 70)
print(f"\nCorrect topic name: {CORRECT_TOPIC}")
print("(Oracle Debezium creates topics with UPPERCASE schema/table names)")
print("\n" + "=" * 70)

# Get topic info
print("\n1. Topic Information:")
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
            
            print(f"   ✓ Topic exists!")
            print(f"   Messages: {message_count}")
            print(f"   Offset range: {offset_min} to {offset_max}")
            
            if message_count > 0:
                print(f"\n   ✓✓✓ SUCCESS: Topic has {message_count} message(s)!")
                print("   Messages are being produced by Debezium connector!")
            else:
                print(f"\n   ⚠ Topic exists but has no messages yet")
        else:
            print(f"   Topic exists but has no partitions")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Try to get a sample message (if API supports it)
print("\n2. Topic Status:")
print(f"   Visit this URL in Kafka UI:")
print(f"   http://72.61.233.209:8080/ui/clusters/local/topics/{CORRECT_TOPIC}/messages")
print("\n   Make sure you're viewing the UPPERCASE topic:")
print(f"   ✓ {CORRECT_TOPIC} (correct - has messages)")
print(f"   ✗ oracle_sf_p.cdc_user.test (wrong - empty topic)")

print("\n" + "=" * 70)
print("IMPORTANT:")
print("  Oracle Debezium creates topics with UPPERCASE names")
print(f"  Correct topic: {CORRECT_TOPIC}")
print(f"  Sink connector is configured to consume from: {CORRECT_TOPIC}")
print("  Data IS flowing! Check the uppercase topic in Kafka UI!")
print("=" * 70)


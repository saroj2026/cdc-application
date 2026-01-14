#!/usr/bin/env python3
"""Check sink connector status and configuration."""

import requests

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SINK_CONNECTOR = "sink-oracle_sf_p-snow-public"

print("=" * 70)
print("SINK CONNECTOR STATUS")
print("=" * 70)

# Check config
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/config")
config = r.json()
print("\nConfiguration:")
print(f"  Topics: {config.get('topics')}")
print(f"  Tasks max: {config.get('tasks.max')}")

# Check status
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SINK_CONNECTOR}/status")
status = r.json()
print("\nStatus:")
print(f"  State: {status.get('connector', {}).get('state')}")
tasks = status.get('tasks', [])
print(f"  Tasks: {len(tasks)}")
for task in tasks:
    print(f"    Task {task.get('id')}: {task.get('state')}")
    if task.get('state') == 'FAILED':
        print(f"      Error: {task.get('trace', 'No trace')[:500]}")

# Check source topics
r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/cdc-oracle_sf_p-ora-cdc_user/topics")
topics_data = r.json()
source_topics = topics_data.get('cdc-oracle_sf_p-ora-cdc_user', {}).get('topics', [])
print("\nSource connector topics:")
for topic in source_topics:
    print(f"  - {topic}")

print("\n" + "=" * 70)
print("ISSUE DETECTED:")
print("=" * 70)
sink_topic = config.get('topics')
source_table_topic = 'oracle_sf_p.CDC_USER.TEST'
print(f"Sink is consuming from: {sink_topic}")
print(f"Source creates topic:    {source_table_topic}")
if sink_topic != source_table_topic:
    print("\n❌ TOPIC NAME MISMATCH!")
    print("   The sink connector is looking for a topic that doesn't exist!")
    print("   Oracle creates topics with UPPERCASE schema/table names")
    print("   But the sink is configured with lowercase topic name")
else:
    print("\n✓ Topic names match")


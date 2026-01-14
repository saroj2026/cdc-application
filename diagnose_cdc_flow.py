#!/usr/bin/env python3
"""Diagnose why CDC is not flowing to Snowflake."""

import requests
import subprocess
import json

print("=" * 70)
print("DIAGNOSING CDC FLOW: ORACLE → KAFKA → SNOWFLAKE")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
topic_name = "oracle_sf_p.CDC_USER.TEST"
source_connector = "cdc-oracle_sf_p-ora-cdc_user"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Checking Source Connector (Debezium)...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{source_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        print(f"   State: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'N/A')
            task_id = task.get('id', 'N/A')
            print(f"   Task {task_id}: {task_state}")
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"     Error: {trace[:500]}")
    else:
        print(f"   ❌ Connector not found: {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking Sink Connector (Snowflake)...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        tasks = status.get('tasks', [])
        print(f"   State: {connector_state}")
        for task in tasks:
            task_state = task.get('state', 'N/A')
            task_id = task.get('id', 'N/A')
            print(f"   Task {task_id}: {task_state}")
            if task_state == 'FAILED':
                trace = task.get('trace', '')
                if trace:
                    print(f"     Error: {trace[:800]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Checking Kafka Topic Message Count...")
print("-" * 70)

# Try to get message count from Kafka (if kafka-console-consumer is available via SSH)
# For now, we'll check via Kafka Connect API
try:
    # Get connector topics
    r = requests.get(f"{kafka_connect_url}/connectors/{source_connector}/topics", timeout=5)
    if r.status_code == 200:
        topics = r.json()
        print(f"   Topics reported by connector: {topics}")
    else:
        print(f"   ⚠ Could not get topics from connector API: {r.status_code}")
except Exception as e:
    print(f"   ⚠ Error getting topics: {e}")

print("\n4. Checking Sink Connector Configuration...")
print("-" * 70)

try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Topics configured: {config.get('topics', 'N/A')}")
        print(f"   Topic2Table map: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Transforms: {config.get('transforms', 'N/A')}")
        print(f"   Buffer count: {config.get('buffer.count.records', 'N/A')}")
        print(f"   Buffer flush time: {config.get('buffer.flush.time', 'N/A')}")
        
        # Check if topic matches
        configured_topics = config.get('topics', '')
        if topic_name not in configured_topics:
            print(f"   ⚠ WARNING: Topic '{topic_name}' not in configured topics!")
            print(f"   Configured: {configured_topics}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n5. Checking Consumer Group Offsets...")
print("-" * 70)

# Try to check consumer group offsets
# The consumer group name for Snowflake sink is typically: connect-{connector-name}
consumer_group = f"connect-{sink_connector}"

print(f"   Consumer group: {consumer_group}")
print(f"   (To check offsets, use: kafka-consumer-groups.sh --bootstrap-server kafka:29092 --group {consumer_group} --describe)")

print("\n6. Recommendations...")
print("-" * 70)

print("   If connectors are RUNNING but no data in Snowflake:")
print("   1. Check if Kafka topic has messages (use Kafka UI or kafka-console-consumer)")
print("   2. Check sink connector logs for errors")
print("   3. Verify topic name case matches (Oracle uses UPPERCASE: CDC_USER.TEST)")
print("   4. Check Snowflake buffer flush - may need to wait longer or trigger flush")
print("   5. Verify Snowflake table schema has RECORD_CONTENT and RECORD_METADATA columns")

print("\n" + "=" * 70)


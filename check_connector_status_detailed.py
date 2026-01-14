#!/usr/bin/env python3
"""Check detailed connector status and topics."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
SOURCE_CONNECTOR = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("DETAILED CONNECTOR STATUS CHECK")
print("=" * 70)

# Check connector status
print("\n1. Connector Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/status")
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state')
        print(f"   State: {connector_state}")
        
        tasks = status.get('tasks', [])
        print(f"   Tasks: {len(tasks)}")
        for task in tasks:
            task_id = task.get('id')
            task_state = task.get('state')
            worker_id = task.get('worker_id')
            print(f"     Task {task_id}: {task_state} (Worker: {worker_id})")
            
            if task_state == 'FAILED':
                trace = task.get('trace', 'No trace')
                print(f"       Error: {trace[:500]}")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check connector config
print("\n2. Connector Configuration:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/config")
    if r.status_code == 200:
        config = r.json()
        print(f"   Database server name: {config.get('database.server.name')}")
        print(f"   Table include list: {config.get('table.include.list')}")
        print(f"   Snapshot mode: {config.get('snapshot.mode')}")
        print(f"   Tasks max: {config.get('tasks.max')}")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check topics (this is what the UI shows)
print("\n3. Connector Topics (from API):")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{SOURCE_CONNECTOR}/topics")
    if r.status_code == 200:
        topics_data = r.json()
        topics = topics_data.get(SOURCE_CONNECTOR, {}).get('topics', [])
        print(f"   Topics: {topics}")
        print(f"   Count: {len(topics)}")
        
        if not topics:
            print("\n   ⚠ No topics reported by connector!")
            print("   This could mean:")
            print("     - Connector hasn't started producing messages yet")
            print("     - Connector is still initializing")
            print("     - Topics haven't been created yet")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("NOTE: Topics are created when the connector starts producing messages")
print("      For Oracle, this happens after snapshot/initialization")
print("=" * 70)


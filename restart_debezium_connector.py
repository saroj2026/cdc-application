#!/usr/bin/env python3
"""Restart Debezium Oracle connector to force it to start CDC streaming."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("RESTARTING DEBEZIUM ORACLE CONNECTOR")
print("=" * 70)

# Check current status
print("\n1. Current Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
    if r.status_code == 200:
        status = r.json()
        state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {state}")
    else:
        print(f"   Error: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# Restart connector
print("\n2. Restarting Connector:")
try:
    r = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
    if r.status_code == 204:
        print("   ✓ Connector restart initiated")
        print("   Waiting 10 seconds for connector to restart...")
        time.sleep(10)
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check status after restart
print("\n3. Status After Restart:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
    if r.status_code == 200:
        status = r.json()
        state = status.get('connector', {}).get('state', 'N/A')
        print(f"   Connector State: {state}")
        
        tasks = status.get('tasks', [])
        for i, task in enumerate(tasks):
            task_state = task.get('state', 'N/A')
            print(f"   Task {i} State: {task_state}")
            if task_state == 'FAILED':
                error = task.get('trace', 'No error details')
                print(f"   Error: {error[:300]}")
    else:
        print(f"   Error: {r.status_code}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("After restart, the connector should start capturing CDC changes.")
print("Wait a few seconds, then try INSERT/UPDATE/DELETE operations in Oracle")
print("and check if new messages appear in the Kafka topic.")
print("=" * 70)

#!/usr/bin/env python3
"""Check Debezium Oracle connector status and configuration."""

import requests
import json

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("CHECKING DEBEZIUM ORACLE CONNECTOR")
print("=" * 70)

# Check status
print("\n1. Connector Status:")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
    if r.status_code == 200:
        status = r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        connector_worker = status.get('connector', {}).get('worker_id', 'N/A')
        print(f"   State: {connector_state}")
        print(f"   Worker: {connector_worker}")
        
        tasks = status.get('tasks', [])
        print(f"\n   Tasks ({len(tasks)}):")
        for i, task in enumerate(tasks):
            task_state = task.get('state', 'N/A')
            task_worker = task.get('worker_id', 'N/A')
            task_id = task.get('id', i)
            print(f"     Task {task_id}: {task_state} on {task_worker}")
            if task_state == 'FAILED':
                error = task.get('trace', 'No error details')
                print(f"       Error: {error[:200]}...")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

# Check configuration
print("\n2. Connector Configuration (key settings):")
try:
    r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
    if r.status_code == 200:
        config = r.json()
        key_settings = [
            'snapshot.mode',
            'table.include.list',
            'database.connection.adapter',
            'log.mining.strategy',
            'database.user',
            'database.server.name',
            'database.dbname',
            'database.service.name'
        ]
        
        for key in key_settings:
            value = config.get(key, 'N/A')
            print(f"   {key}: {value}")
        
        # Check if snapshot mode is initial_only
        snapshot_mode = config.get('snapshot.mode', '')
        if snapshot_mode == 'initial_only':
            print(f"\n   ⚠ IMPORTANT: snapshot.mode is 'initial_only'")
            print(f"   This means:")
            print(f"     - Snapshot captured schema and initial data")
            print(f"     - CDC should continue capturing changes after snapshot")
            print(f"     - If no CDC changes are appearing, there might be an issue with:")
            print(f"       * LogMiner configuration")
            print(f"       * Oracle archive logs")
            print(f"       * User permissions (LOGMINING privilege)")
    else:
        print(f"   Error: {r.status_code} - {r.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)


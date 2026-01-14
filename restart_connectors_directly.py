#!/usr/bin/env python3
"""Restart connectors directly via Kafka Connect API."""

import requests
import time

print("=" * 70)
print("RESTARTING ORACLE-SNOWFLAKE CDC CONNECTORS")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
source_connector = "cdc-oracle_sf_p-ora-cdc_user"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Checking current connector status...")
print("-" * 70)

connectors = {
    "Source (Debezium)": source_connector,
    "Sink (Snowflake)": sink_connector
}

for name, connector_name in connectors.items():
    try:
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
        if r.status_code == 200:
            status = r.json()
            connector_state = status.get('connector', {}).get('state', 'N/A')
            tasks = status.get('tasks', [])
            print(f"\n   {name} ({connector_name}):")
            print(f"     State: {connector_state}")
            for task in tasks:
                task_id = task.get('id', 'N/A')
                task_state = task.get('state', 'N/A')
                print(f"     Task {task_id}: {task_state}")
        else:
            print(f"\n   {name} ({connector_name}): Not found ({r.status_code})")
    except Exception as e:
        print(f"\n   {name} ({connector_name}): Error - {e}")

print("\n2. Restarting connectors...")
print("-" * 70)

for name, connector_name in connectors.items():
    try:
        print(f"\n   Restarting {name}...")
        restart_r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
        
        if restart_r.status_code == 204:
            print(f"     ✅ Restart initiated for {connector_name}")
        else:
            print(f"     ⚠ Restart response: {restart_r.status_code} - {restart_r.text}")
    except Exception as e:
        print(f"     ❌ Error restarting {connector_name}: {e}")

print("\n   Waiting 25 seconds for connectors to initialize...")
time.sleep(25)

print("\n3. Checking connector status after restart...")
print("-" * 70)

all_running = True
for name, connector_name in connectors.items():
    try:
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
        if r.status_code == 200:
            status = r.json()
            connector_state = status.get('connector', {}).get('state', 'N/A')
            tasks = status.get('tasks', [])
            print(f"\n   {name} ({connector_name}):")
            print(f"     State: {connector_state}")
            
            for task in tasks:
                task_id = task.get('id', 'N/A')
                task_state = task.get('state', 'N/A')
                print(f"     Task {task_id}: {task_state}")
                
                if task_state == 'FAILED':
                    trace = task.get('trace', '')
                    if trace:
                        print(f"       ⚠ Error: {trace[:500]}")
                    all_running = False
                elif task_state != 'RUNNING':
                    all_running = False
        else:
            print(f"\n   {name} ({connector_name}): Not found ({r.status_code})")
            all_running = False
    except Exception as e:
        print(f"\n   {name} ({connector_name}): Error - {e}")
        all_running = False

print("\n" + "=" * 70)
if all_running:
    print("✅✅✅ ALL CONNECTORS ARE RUNNING!")
    print("CDC should now be flowing from Oracle → Kafka → Snowflake")
else:
    print("⚠ Some connectors may not be running. Check status above.")
print("=" * 70)

print("\nNEXT STEPS:")
print("  1. Wait 60-90 seconds for Snowflake buffer flush")
print("  2. Insert/update data in Oracle:")
print("     INSERT INTO cdc_user.test (id, name) VALUES (9999, 'CDC Test');")
print("     UPDATE cdc_user.test SET name = 'Updated' WHERE id = 9999;")
print("  3. Check Snowflake for CDC events")
print("  4. Run: python monitor_cdc_to_snowflake.py")
print("=" * 70)


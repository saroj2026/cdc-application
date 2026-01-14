#!/usr/bin/env python3
"""Resume connectors using PUT method (correct API)."""

import requests
import time

print("=" * 70)
print("RESUMING ORACLE-SNOWFLAKE CDC CONNECTORS (PUT METHOD)")
print("=" * 70)

kafka_connect_url = "http://72.61.233.209:8083"
source_connector = "cdc-oracle_sf_p-ora-cdc_user"
sink_connector = "sink-oracle_sf_p-snow-public"

print("\n1. Resuming connectors...")
print("-" * 70)

connectors = {
    "Source (Debezium)": source_connector,
    "Sink (Snowflake)": sink_connector
}

for name, connector_name in connectors.items():
    try:
        print(f"\n   Resuming {name} ({connector_name})...")
        # Use PUT method for resume (as per Kafka Connect API)
        resume_r = requests.put(f"{kafka_connect_url}/connectors/{connector_name}/resume", timeout=10)
        
        if resume_r.status_code in [200, 202, 204]:
            print(f"     ✅ Resume successful for {connector_name}")
        else:
            print(f"     ⚠ Resume response: {resume_r.status_code} - {resume_r.text}")
    except Exception as e:
        print(f"     ❌ Error resuming {connector_name}: {e}")

print("\n   Waiting 20 seconds for connectors to initialize...")
time.sleep(20)

print("\n2. Checking connector status...")
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
                elif task_state == 'RUNNING':
                    print(f"       ✅ Task is RUNNING!")
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
print("  2. Insert/update data in Oracle to test CDC")
print("  3. Check Snowflake for CDC events")
print("=" * 70)


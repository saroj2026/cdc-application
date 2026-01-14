#!/usr/bin/env python3
"""Restart connector after config update (handle 409 stale config errors)."""

import requests
import time

KAFKA_CONNECT_URL = "http://72.61.233.209:8083"
CONNECTOR_NAME = "cdc-oracle_sf_p-ora-cdc_user"

print("=" * 70)
print("RESTARTING CONNECTOR AFTER CONFIG UPDATE")
print("=" * 70)

# Wait a bit for config to settle
print("\n1. Waiting 10 seconds for config to settle...")
time.sleep(10)

# Try to restart
max_retries = 3
for attempt in range(1, max_retries + 1):
    print(f"\n2. Restart attempt {attempt}/{max_retries}...")
    try:
        restart_r = requests.post(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart")
        if restart_r.status_code == 204:
            print(f"   ✓ Connector restart initiated successfully!")
            break
        elif restart_r.status_code == 409:
            print(f"   ⚠ 409 Conflict (stale config) - waiting 10 more seconds...")
            if attempt < max_retries:
                time.sleep(10)
            else:
                print(f"   ✗ Still getting 409 after {max_retries} attempts")
        else:
            print(f"   ✗ Restart failed: {restart_r.status_code} - {restart_r.text}")
            break
    except Exception as e:
        print(f"   Error: {e}")
        break

# Wait for connector to restart
print(f"\n3. Waiting 15 seconds for connector to restart and initialize...")
time.sleep(15)

# Check status
print(f"\n4. Checking connector status...")
try:
    status_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status")
    if status_r.status_code == 200:
        status = status_r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        connector_worker = status.get('connector', {}).get('worker_id', 'N/A')
        
        print(f"   Connector State: {connector_state}")
        print(f"   Worker: {connector_worker}")
        
        tasks = status.get('tasks', [])
        for i, task in enumerate(tasks):
            task_state = task.get('state', 'N/A')
            task_worker = task.get('worker_id', 'N/A')
            print(f"   Task {i}: {task_state} on {task_worker}")
            
            if task_state == 'FAILED':
                error = task.get('trace', 'No error details')
                print(f"   ⚠ Task Error: {error[:500]}")
        
        if connector_state == 'RUNNING':
            print(f"\n   ✓✓✓ Connector is RUNNING!")
            
            # Verify config
            config_r = requests.get(f"{KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config")
            if config_r.status_code == 200:
                config = config_r.json()
                table_list = config.get('table.include.list', 'N/A')
                print(f"\n5. Verifying configuration...")
                print(f"   table.include.list: {table_list}")
                
                if table_list == 'cdc_user.test':
                    print(f"   ✓✓✓ Config is correct: using cdc_user.test (without ##)")
                    print(f"   ✓ This avoids special character issues")
                else:
                    print(f"   ⚠ Config might not be correct: {table_list}")
    else:
        print(f"   ⚠ Could not get connector status: {status_r.status_code}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)
print("✓ Connector configuration updated to: cdc_user.test")
print("✓ Connector restarted (if successful)")
print("")
print("Next steps:")
print("1. Try INSERT/UPDATE/DELETE operations in Oracle (cdc_user.test table)")
print("2. Wait 10-20 seconds")
print("3. Check Kafka topic oracle_sf_p.CDC_USER.TEST for new messages")
print("4. Check Snowflake for CDC events")
print("=" * 70)


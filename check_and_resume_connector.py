#!/usr/bin/env python3
"""Check connector status and resume if paused."""

import requests

kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("=" * 70)
print("CHECKING AND RESUMING SNOWFLAKE SINK CONNECTOR")
print("=" * 70)

try:
    # Get status
    status_r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
    if status_r.status_code == 200:
        status = status_r.json()
        connector_state = status.get('connector', {}).get('state', 'N/A')
        
        print(f"\n1. Current Status:")
        print(f"   Connector state: {connector_state}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_state = task.get('state', 'N/A')
            print(f"   Task {task.get('id', 'N/A')} state: {task_state}")
        
        # Resume if paused
        if connector_state == 'PAUSED':
            print(f"\n2. Resuming connector...")
            resume_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/resume", timeout=10)
            if resume_r.status_code == 204:
                print(f"   ✅ Connector resumed!")
                
                import time
                time.sleep(5)
                
                # Check status again
                status_r2 = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r2.status_code == 200:
                    status2 = status_r2.json()
                    new_state = status2.get('connector', {}).get('state', 'N/A')
                    print(f"   New state: {new_state}")
            else:
                print(f"   ❌ Resume failed: {resume_r.status_code} - {resume_r.text}")
        elif connector_state == 'RUNNING':
            print(f"\n   ✅ Connector is already RUNNING")
        else:
            print(f"\n   ⚠ Connector state is {connector_state}, may need restart")
            
            # Try restart
            print(f"\n2. Restarting connector...")
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{sink_connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print(f"   ✅ Connector restart initiated")
                
                import time
                time.sleep(10)
                
                # Check status again
                status_r3 = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/status", timeout=5)
                if status_r3.status_code == 200:
                    status3 = status_r3.json()
                    new_state = status3.get('connector', {}).get('state', 'N/A')
                    print(f"   New state: {new_state}")
            else:
                print(f"   ❌ Restart failed: {restart_r.status_code} - {restart_r.text}")
    else:
        print(f"   ❌ Error getting status: {status_r.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


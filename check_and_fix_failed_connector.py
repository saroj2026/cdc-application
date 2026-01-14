#!/usr/bin/env python3
"""Check why connector task failed and fix it."""

import paramiko
import requests
import json

print("=" * 70)
print("CHECKING FAILED CONNECTOR TASK")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Checking connector task status...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        print(f"   Connector state: {status.get('connector', {}).get('state', 'N/A')}")
        
        tasks = status.get('tasks', [])
        for task in tasks:
            task_id = task.get('id', 'N/A')
            task_state = task.get('state', 'N/A')
            worker_id = task.get('worker_id', 'N/A')
            print(f"   Task {task_id} state: {task_state} on {worker_id}")
            
            if task_state == 'FAILED':
                trace = task.get('trace', 'No trace available')
                print(f"\n   ⚠ Task Error Trace:")
                print(f"   {trace[:1000]}...")  # First 1000 chars
    
    print("\n2. Checking connector logs for errors...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
        
        log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -A 10 -B 5 "cdc-oracle_sf_p-ora-cdc_user.*FAILED\\|cdc-oracle_sf_p-ora-cdc_user.*ERROR\\|cdc-oracle_sf_p-ora-cdc_user.*Exception" | tail -30"""
        
        stdin, stdout, stderr = ssh.exec_command(log_cmd)
        output = stdout.read().decode()
        
        print("\nConnector error logs:")
        print("-" * 70)
        if output.strip():
            print(output)
        else:
            print("No specific errors found, checking all recent logs...")
            # Get all recent logs
            log_cmd2 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep "cdc-oracle_sf_p" | tail -20"""
            stdin, stdout, stderr = ssh.exec_command(log_cmd2)
            output = stdout.read().decode()
            print(output)
        print("-" * 70)
        
        ssh.close()
        
    except Exception as e:
        print(f"   Error checking logs: {e}")
    
    print("\n3. The issue: Changing to 'initial' mode tries to do full snapshot again")
    print("   Since we already have data, we should use 'never' or keep 'initial_only'")
    print("   But 'initial_only' doesn't enable streaming...")
    print("\n4. Solution: Change back to 'initial_only' but check if there's a way to enable streaming")
    print("   OR: Use 'never' mode if full load was already done")
    
    print("\n5. Actually, let's check the connector config to see what's best...")
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        print(f"   Full load was already done, so we should use 'never' mode")
        print("\n6. Changing to 'never' mode (CDC only, no snapshot)...")
        
        new_config = config.copy()
        new_config['snapshot.mode'] = 'never'
        
        update_r = requests.put(
            f"{kafka_connect_url}/connectors/{connector_name}/config",
            json=new_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if update_r.status_code == 200:
            print("   ✓ Config updated: snapshot.mode = 'never'")
            print("   This will start streaming immediately (no snapshot)")
            
            # Restart
            restart_r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
            if restart_r.status_code == 204:
                print("   ✓ Connector restarted")
                print("   Waiting 20 seconds...")
                import time
                time.sleep(20)
                
                # Check status
                status_r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
                if status_r.status_code == 200:
                    status = status_r.json()
                    print(f"\n   Connector state: {status.get('connector', {}).get('state', 'N/A')}")
                    tasks = status.get('tasks', [])
                    for task in tasks:
                        print(f"   Task {task.get('id', 'N/A')} state: {task.get('state', 'N/A')}")
        else:
            print(f"   ✗ Config update failed: {update_r.status_code}")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


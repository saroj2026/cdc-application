#!/usr/bin/env python3
"""Get detailed error from failed task and fix it."""

import paramiko
import requests
import json

print("=" * 70)
print("GETTING DETAILED ERROR AND FIXING")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Getting full task error trace...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/tasks/0/status", timeout=5)
    if r.status_code == 200:
        task_status = r.json()
        trace = task_status.get('trace', 'No trace')
        print("\nFull Error Trace:")
        print("-" * 70)
        print(trace)
        print("-" * 70)
        
        # Check if it's a LogMiner specific error
        if "LogMiner" in trace or "logminer" in trace.lower():
            print("\n⚠ LogMiner-related error detected")
        
        if "ORA-" in trace:
            print("\n⚠ Oracle error code detected in trace")
    
    print("\n2. Getting recent connector logs with full error details...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
        
        # Get full error logs
        log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -A 20 "cdc-oracle_sf_p-ora-cdc_user.*ERROR\\|LogMinerStreamingChangeEventSource.*Exception\\|An exception occurred" | tail -50"""
        
        stdin, stdout, stderr = ssh.exec_command(log_cmd)
        output = stdout.read().decode()
        
        print("\nDetailed Error Logs:")
        print("-" * 70)
        print(output)
        print("-" * 70)
        
        # The issue: 'initial' mode is trying to do snapshot again and failing
        # Oracle doesn't support 'never' mode
        # We need to go back to 'initial_only' but it's not enabling streaming
        
        print("\n3. Solution: Change back to 'initial_only' and check configuration...")
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
        if r.status_code == 200:
            config = r.json()
            
            # Change back to initial_only
            new_config = config.copy()
            new_config['snapshot.mode'] = 'initial_only'
            
            # Check if there's a streaming.enabled config or similar
            print(f"   Current config keys related to streaming:")
            for key in sorted(config.keys()):
                if 'stream' in key.lower() or 'mine' in key.lower() or 'cdc' in key.lower():
                    print(f"     {key}: {config[key]}")
            
            print("\n4. Updating back to 'initial_only'...")
            update_r = requests.put(
                f"{kafka_connect_url}/connectors/{connector_name}/config",
                json=new_config,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if update_r.status_code == 200:
                print("   ✓ Config reverted to 'initial_only'")
                
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
                            
                            if task.get('state') == 'RUNNING':
                                print("\n   ✓✓✓ Connector is RUNNING!")
                                print("   Note: 'initial_only' should enable streaming after snapshot completes")
                                print("   If streaming doesn't start, we may need to check Debezium version or configuration")
        
        ssh.close()
        
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


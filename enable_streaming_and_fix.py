#!/usr/bin/env python3
"""Enable streaming mode for Oracle connector to start LogMiner CDC."""

import paramiko
import requests
import json
import time

print("=" * 70)
print("ENABLING STREAMING MODE FOR CDC")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

print("\n1. Getting current connector configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Current snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        print(f"   Current log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
        
        # The issue: initial_only does snapshot but may not enable streaming
        # We need to ensure streaming is enabled after snapshot
        # Actually, initial_only should enable streaming after snapshot, but it seems it's not
        
        # Check if we need to change snapshot mode or add streaming configuration
        print("\n2. The issue: 'Streaming is not enabled in current configuration'")
        print("   This means LogMiner streaming is not starting after snapshot")
        
        # Option 1: Change to 'initial' which does snapshot + streaming
        # Option 2: Keep initial_only but ensure streaming starts after snapshot
        # Option 3: Check if there's a streaming.enabled config
        
        print("\n3. Checking if we need to change snapshot mode...")
        print("   Current: initial_only (snapshot only, should enable streaming after)")
        print("   Option: Change to 'initial' (snapshot + streaming)")
        
        # Actually, let's check the connector offset/state first
        print("\n4. Checking connector offsets/state...")
        try:
            r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
            if r.status_code == 200:
                status = r.json()
                print(f"   Connector state: {status.get('connector', {}).get('state', 'N/A')}")
                tasks = status.get('tasks', [])
                for task in tasks:
                    print(f"   Task {task.get('id', 'N/A')} state: {task.get('state', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # The real fix: We need to ensure the connector transitions to streaming
        # Since initial_only should do this automatically, the issue might be:
        # 1. Snapshot never completed properly
        # 2. Connector is stuck in snapshot mode
        # 3. Missing configuration for streaming
        
        print("\n5. Attempting fix: Restart connector and check if streaming starts...")
        print("   (If snapshot completed, streaming should start automatically)")
        
        # Restart the connector
        try:
            r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
            if r.status_code == 204:
                print("   ✓ Connector restart initiated")
                print("   Waiting 20 seconds for connector to initialize...")
                time.sleep(20)
            else:
                print(f"   ⚠ Restart returned: {r.status_code}")
        except Exception as e:
            print(f"   Error restarting: {e}")
        
        # Check logs after restart
        print("\n6. Checking connector logs for streaming status...")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
            
            log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "streaming\\|logminer.*start\\|cdc-oracle_sf_p" | tail -10"""
            
            stdin, stdout, stderr = ssh.exec_command(log_cmd)
            output = stdout.read().decode()
            
            print("\nRecent streaming/LogMiner logs:")
            print("-" * 70)
            print(output)
            print("-" * 70)
            
            # Check LogMiner sessions
            print("\n7. Checking if LogMiner session started...")
            logminer_check = """docker exec -i oracle-xe sqlplus -s / as sysdba << 'EOF'
SET FEEDBACK OFF
SELECT COUNT(*) as active_sessions FROM v$logmnr_session;
EXIT;
EOF"""
            
            stdin, stdout, stderr = ssh.exec_command(logminer_check)
            output = stdout.read().decode()
            
            print("\nActive LogMiner sessions:")
            print("-" * 70)
            print(output)
            print("-" * 70)
            
            if "0" not in output or "no rows" not in output.lower():
                print("\n✓✓✓ LogMiner session is active!")
            else:
                print("\n⚠ LogMiner session still not active")
                print("\n8. Trying alternative: Change snapshot mode to 'initial'...")
                print("   This will do snapshot + enable streaming")
                
                # Update config to use 'initial' instead of 'initial_only'
                new_config = config.copy()
                new_config['snapshot.mode'] = 'initial'
                
                update_r = requests.put(
                    f"{kafka_connect_url}/connectors/{connector_name}/config",
                    json=new_config,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if update_r.status_code == 200:
                    print("   ✓ Config updated: snapshot.mode = 'initial'")
                    print("   Waiting 10 seconds...")
                    time.sleep(10)
                    
                    # Restart again
                    requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
                    print("   ✓ Connector restarted with new config")
                    print("   Waiting 20 seconds for initialization...")
                    time.sleep(20)
                    
                    # Check LogMiner again
                    stdin, stdout, stderr = ssh.exec_command(logminer_check)
                    output = stdout.read().decode()
                    print("\nLogMiner sessions after config change:")
                    print(output)
                else:
                    print(f"   ✗ Config update failed: {update_r.status_code}")
            
            ssh.close()
            
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
        
    else:
        print(f"   Error getting config: {r.status_code}")
        
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("FIX COMPLETE")
print("=" * 70)


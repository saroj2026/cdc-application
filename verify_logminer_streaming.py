#!/usr/bin/env python3
"""Verify LogMiner is streaming and check connector logs."""

import paramiko
import requests
import time

print("=" * 70)
print("VERIFYING LOGMINER STREAMING STATUS")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

try:
    print("\n1. Checking connector status...")
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/status", timeout=5)
    if r.status_code == 200:
        status = r.json()
        print(f"   Connector state: {status.get('connector', {}).get('state', 'N/A')}")
        tasks = status.get('tasks', [])
        for task in tasks:
            print(f"   Task {task.get('id', 'N/A')} state: {task.get('state', 'N/A')}")
    
    print("\n2. Checking LogMiner sessions...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    logminer_check = """docker exec -i oracle-xe sqlplus -s / as sysdba << 'EOF'
SET FEEDBACK OFF
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN, PROCESSED_SCN
FROM v$logmnr_session;
EXIT;
EOF"""
    
    stdin, stdout, stderr = ssh.exec_command(logminer_check)
    output = stdout.read().decode()
    
    print("\nLogMiner Sessions:")
    print("-" * 70)
    print(output)
    print("-" * 70)
    
    if "SESSION_ID" in output and "no rows selected" not in output.lower():
        print("\n✓✓✓ LogMiner session is ACTIVE!")
    else:
        print("\n⚠ No active LogMiner sessions")
        print("   Checking connector logs for streaming status...")
        
        log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "streaming\\|logminer.*start\\|cdc-oracle_sf_p.*stream" | tail -15"""
        
        stdin, stdout, stderr = ssh.exec_command(log_cmd)
        output = stdout.read().decode()
        
        print("\nStreaming/LogMiner logs:")
        print("-" * 70)
        print(output if output.strip() else "No streaming logs found")
        print("-" * 70)
    
    print("\n3. Checking connector configuration...")
    r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
        print(f"   log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
        print(f"   log.mining.strategy: {config.get('log.mining.strategy', 'N/A')}")
        
        # The issue: initial_only might not be starting streaming
        # Let's check if we need to wait longer or if there's another issue
        if config.get('snapshot.mode') == 'initial_only':
            print("\n   ⚠ snapshot.mode is 'initial_only'")
            print("   This should enable streaming after snapshot, but it may take time")
            print("   OR streaming may not be starting automatically")
    
    ssh.close()
    
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


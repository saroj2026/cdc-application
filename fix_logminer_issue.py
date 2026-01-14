#!/usr/bin/env python3
"""Fix LogMiner issue by checking Debezium logs and restarting connector if needed."""

import paramiko
import requests
import json
import time

print("=" * 70)
print("FIXING LOGMINER ISSUE")
print("=" * 70)

hostname = "72.61.233.209"
username = "root"
password = "segmbp@1100"
kafka_connect_url = "http://72.61.233.209:8083"
connector_name = "cdc-oracle_sf_p-ora-cdc_user"

try:
    print("\n1. Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    print("   ✓ Connected")
    
    print("\n2. Checking Debezium connector logs for LogMiner errors...")
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "logminer\\|oracle.*error\\|failed.*logminer\\|cannot.*logminer" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    print("\nLogMiner-related errors:")
    print("-" * 70)
    if output.strip():
        print(output)
    else:
        print("No LogMiner errors found in recent logs")
    print("-" * 70)
    
    print("\n3. Checking full connector logs (last 100 lines)...")
    full_log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -A 5 -B 5 "cdc-oracle_sf_p-ora-cdc_user" | tail -50"""
    
    stdin, stdout, stderr = ssh.exec_command(full_log_cmd)
    output = stdout.read().decode()
    
    print("\nConnector-specific logs:")
    print("-" * 70)
    print(output[:2000] if len(output) > 2000 else output)
    print("-" * 70)
    
    print("\n4. Checking connector configuration...")
    try:
        r = requests.get(f"{kafka_connect_url}/connectors/{connector_name}/config", timeout=5)
        if r.status_code == 200:
            config = r.json()
            print(f"   table.include.list: {config.get('table.include.list', 'N/A')}")
            print(f"   log.mining.strategy: {config.get('log.mining.strategy', 'N/A')}")
            print(f"   log.mining.continuous.mine: {config.get('log.mining.continuous.mine', 'N/A')}")
            print(f"   snapshot.mode: {config.get('snapshot.mode', 'N/A')}")
    except Exception as e:
        print(f"   Error getting config: {e}")
    
    print("\n5. Restarting connector to force LogMiner session start...")
    try:
        r = requests.post(f"{kafka_connect_url}/connectors/{connector_name}/restart", timeout=10)
        if r.status_code == 204:
            print("   ✓ Connector restart initiated")
            print("   Waiting 15 seconds for restart...")
            time.sleep(15)
        else:
            print(f"   ⚠ Restart returned: {r.status_code}")
    except Exception as e:
        print(f"   Error restarting: {e}")
    
    print("\n6. Checking LogMiner sessions after restart...")
    time.sleep(5)
    logminer_check = """docker exec -i oracle-xe sqlplus -s / as sysdba << 'EOF'
SET FEEDBACK OFF
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN FROM v$logmnr_session;
EXIT;
EOF"""
    
    stdin, stdout, stderr = ssh.exec_command(logminer_check)
    output = stdout.read().decode()
    
    print("\nLogMiner Sessions (after restart):")
    print("-" * 70)
    print(output)
    print("-" * 70)
    
    if "SESSION_ID" in output and "no rows selected" not in output.lower():
        print("\n✓✓✓ LogMiner session is now active!")
    else:
        print("\n⚠ LogMiner session still not active")
        print("   This may indicate a configuration issue")
    
    ssh.close()
    print("\n✓ Diagnosis and fix attempt complete!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


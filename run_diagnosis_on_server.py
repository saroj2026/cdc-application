#!/usr/bin/env python3
"""Run diagnosis script on server via SSH."""

import paramiko
import sys

print("=" * 70)
print("CONNECTING TO SERVER AND RUNNING DIAGNOSIS")
print("=" * 70)

hostname = "72.61.233.209"
username = "root"
password = "segmbp@1100"

try:
    print(f"\n1. Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    print("   ✓ Connected successfully!")
    
    print("\n2. Checking Oracle LogMiner status...")
    oracle_cmd = """docker exec -i oracle-xe sqlplus -s / as sysdba << 'EOF'
SET PAGESIZE 1000
SET FEEDBACK OFF
PROMPT === LogMiner Sessions ===
SELECT SESSION_ID, SESSION_NAME, SESSION_STATE, START_SCN, END_SCN FROM v$logmnr_session;
PROMPT === Archive Log Count ===
SELECT COUNT(*) as total, MAX(sequence#) as latest_seq, MAX(next_change#) as latest_scn FROM v$archived_log WHERE status = 'A';
PROMPT === Current SCN ===
SELECT current_scn FROM v$database;
EXIT;
EOF"""
    
    stdin, stdout, stderr = ssh.exec_command(oracle_cmd)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    print("\nOracle LogMiner Status:")
    print("-" * 70)
    print(output)
    if errors:
        print("Errors:")
        print(errors)
    print("-" * 70)
    
    print("\n3. Checking Kafka Connect container logs...")
    kafka_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
if [ ! -z "$KAFKA_CONNECT" ]; then \
  echo "Container: $KAFKA_CONNECT"; \
  docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "oracle\\|logminer\\|error\\|exception" | tail -30; \
else \
  echo "Kafka Connect container not found"; \
fi"""
    
    stdin, stdout, stderr = ssh.exec_command(kafka_cmd)
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    print("\nKafka Connect Logs (Oracle/LogMiner related):")
    print("-" * 70)
    print(output)
    if errors:
        print("Errors:")
        print(errors)
    print("-" * 70)
    
    print("\n4. Checking connector status...")
    status_cmd = "curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status"
    stdin, stdout, stderr = ssh.exec_command(status_cmd)
    output = stdout.read().decode()
    
    print("\nConnector Status:")
    print("-" * 70)
    print(output)
    print("-" * 70)
    
    ssh.close()
    print("\n✓ Diagnosis complete!")
    
except ImportError:
    print("\n⚠ paramiko not installed. Installing...")
    print("Run: pip install paramiko")
    print("\nOr run the diagnosis manually on the server using fix_cdc_directly.sh")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease run diagnosis manually:")
    print("ssh root@72.61.233.209")
    print("Password: segmbp@1100")
    print("Then run: bash fix_cdc_directly.sh")
    sys.exit(1)

print("\n" + "=" * 70)


#!/usr/bin/env python3
"""Check sink connector logs to see if it's processing messages."""

import paramiko

print("=" * 70)
print("CHECKING SINK CONNECTOR LOGS")
print("=" * 70)

hostname = "72.61.233.209"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    print("\n1. Checking sink connector logs...")
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*error\\|sink-oracle_sf_p.*exception\\|snowflake.*error" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    print("\nSink Connector Error Logs:")
    print("-" * 70)
    print(output if output.strip() else "No errors found")
    print("-" * 70)
    
    print("\n2. Checking sink connector activity logs...")
    log_cmd2 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*snowflake\\|sink-oracle_sf_p.*buffer\\|sink-oracle_sf_p.*flush" | tail -15"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd2)
    output = stdout.read().decode()
    
    print("\nSink Connector Activity Logs:")
    print("-" * 70)
    print(output if output.strip() else "No recent activity logs")
    print("-" * 70)
    
    print("\n3. The sink connector may be processing snapshot messages first")
    print("   Then it will process CDC messages. This is normal behavior.")
    print("   Wait a bit longer and check Snowflake again.")
    
    ssh.close()
    
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


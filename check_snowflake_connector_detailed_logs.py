#!/usr/bin/env python3
"""Get detailed Snowflake connector logs including buffer and pipe activity."""

import paramiko

print("=" * 70)
print("CHECKING SNOWFLAKE CONNECTOR DETAILED LOGS")
print("=" * 70)

hostname = "72.61.233.209"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    print("\n1. Checking for Snowflake buffer/pipe activity...")
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "SF_KAFKA_CONNECTOR.*sink-oracle_sf_p\\|SNOWFLAKE_KAFKA_CONNECTOR.*oracle_sf_p\\|Buffer.*oracle_sf_p\\|PIPE.*oracle_sf_p" | tail -30"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Snowflake Buffer/Pipe Activity:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No buffer/pipe activity found")
    
    print("\n2. Checking for all Snowflake connector logs (not just errors)...")
    log_cmd2 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "SF_KAFKA_CONNECTOR" | tail -40"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd2)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   All Snowflake Connector Logs:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No Snowflake connector logs found")
    
    print("\n3. Checking for recent connector activity (last 50 lines of all logs)...")
    log_cmd3 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" --tail 200 2>&1 | grep -i "sink-oracle_sf_p" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd3)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Recent Sink Connector Activity (Last 20 lines):")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No recent activity found")
    
    ssh.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


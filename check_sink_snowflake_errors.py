#!/usr/bin/env python3
"""Check for Snowflake-specific errors in sink connector logs."""

import paramiko

print("=" * 70)
print("CHECKING SINK CONNECTOR FOR SNOWFLAKE ERRORS")
print("=" * 70)

hostname = "72.61.233.209"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    print("\n1. Checking for Snowflake errors...")
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*snowflake.*error\\|sink-oracle_sf_p.*exception\\|sink-oracle_sf_p.*failed" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Snowflake Errors Found:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ✅ No Snowflake errors found")
    
    print("\n2. Checking for buffer flush activity...")
    log_cmd2 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*flush\\|sink-oracle_sf_p.*buffer.*flush\\|sink-oracle_sf_p.*pipe" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd2)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Buffer Flush Activity:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No recent buffer flush activity found")
    
    print("\n3. Checking for Snowflake connection/insert activity...")
    log_cmd3 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*insert\\|sink-oracle_sf_p.*snowflake.*connect\\|sink-oracle_sf_p.*table.*test" | tail -15"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd3)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Snowflake Insert/Connection Activity:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No recent insert/connection activity found")
    
    print("\n4. Getting ALL recent sink connector logs (last 30 lines)...")
    log_cmd4 = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep "sink-oracle_sf_p" | tail -30"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd4)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   All Recent Sink Connector Logs:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No recent logs found")
    
    ssh.close()
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("The sink connector has consumed all 23 messages (LAG: 0)")
print("But CDC events haven't appeared in Snowflake yet.")
print("\nPossible reasons:")
print("1. Buffer is waiting to flush (flush time: 60 seconds)")
print("2. Messages are being processed but not yet written")
print("3. There might be a silent error in Snowflake writes")
print("4. The sink connector might be processing snapshot messages first")
print("=" * 70)


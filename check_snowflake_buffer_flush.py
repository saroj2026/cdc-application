#!/usr/bin/env python3
"""Check if Snowflake sink connector is flushing buffers."""

import paramiko
import requests

print("=" * 70)
print("CHECKING SNOWFLAKE SINK BUFFER FLUSH STATUS")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Sink Connector Configuration (Buffer Settings)")
print("-" * 70)
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Buffer count records: {config.get('buffer.count.records', 'N/A')}")
        print(f"   Buffer flush time (seconds): {config.get('buffer.flush.time', 'N/A')}")
        print(f"   Buffer size bytes: {config.get('buffer.size.bytes', 'N/A')}")
        print(f"\n   ⚠ Messages are buffered until:")
        print(f"     - {config.get('buffer.count.records', 'N/A')} records accumulated, OR")
        print(f"     - {config.get('buffer.flush.time', 'N/A')} seconds elapsed")
        print(f"   Since we have 23 messages, buffer may be waiting for flush time or more records")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking Sink Connector Logs for Buffer Flush Activity")
print("-" * 70)
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    # Check for buffer flush, pipe, stage, or Snowflake write activity
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*flush\\|sink-oracle_sf_p.*pipe\\|sink-oracle_sf_p.*stage\\|sink-oracle_sf_p.*snowflake.*write\\|sink-oracle_sf_p.*buffer" | tail -20"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("   Recent Buffer/Flush Activity:")
        for line in output.strip().split('\n'):
            if len(line) > 0:
                print(f"     {line[:200]}")
    else:
        print("   ⚠ No recent buffer flush activity found")
        print("   This might mean:")
        print("     - Buffer hasn't reached flush threshold yet")
        print("     - Buffer flush time hasn't elapsed")
        print("     - There might be an issue with Snowflake writes")
    
    print("\n3. Checking for Errors in Sink Connector Logs")
    print("-" * 70)
    
    error_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*error\\|sink-oracle_sf_p.*exception\\|sink-oracle_sf_p.*failed" | tail -15"""
    
    stdin, stdout, stderr = ssh.exec_command(error_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("   ⚠ Errors Found:")
        for line in output.strip().split('\n'):
            if len(line) > 0:
                print(f"     {line[:200]}")
    else:
        print("   ✅ No errors found in recent logs")
    
    print("\n4. Checking Latest Sink Connector Logs (Last 30 lines)")
    print("-" * 70)
    
    latest_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep "sink-oracle_sf_p" | tail -30"""
    
    stdin, stdout, stderr = ssh.exec_command(latest_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("   Latest Activity:")
        lines = output.strip().split('\n')
        for line in lines[-10:]:  # Last 10 lines
            if len(line) > 0:
                print(f"     {line[:200]}")
    
    ssh.close()
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("ANALYSIS & RECOMMENDATIONS")
print("=" * 70)
print("Current Status:")
print("  ✅ Sink connector has consumed all 23 messages from Kafka (LAG: 0)")
print("  ⚠ Messages are buffered but not yet in Snowflake")
print("\nPossible Reasons:")
print("  1. Buffer flush time (60 seconds) hasn't elapsed yet")
print("  2. Buffer count threshold (3000 records) not reached (we have 23)")
print("  3. Messages are in buffer waiting for next flush cycle")
print("\nRecommendations:")
print("  1. Wait for buffer flush time (60 seconds) to elapse")
print("  2. Or manually trigger flush by restarting sink connector")
print("  3. Or reduce buffer.flush.time to flush more frequently")
print("=" * 70)


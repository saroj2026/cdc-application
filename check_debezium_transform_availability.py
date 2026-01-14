#!/usr/bin/env python3
"""Check if Debezium transform is available and if there are transform errors."""

import paramiko
import requests

print("=" * 70)
print("CHECKING DEBEZIUM TRANSFORM AVAILABILITY")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"

print("\n1. Checking sink connector configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Transforms: {config.get('transforms', 'N/A')}")
        print(f"   Transform type: {config.get('transforms.unwrap.type', 'N/A')}")
        print(f"   Value converter: {config.get('value.converter', 'N/A')}")
        print(f"   Schemas enable: {config.get('value.converter.schemas.enable', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

print("\n2. Checking for transform-related errors in logs...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "transform\\|ExtractNewRecordState\\|unwrap.*error\\|sink-oracle_sf_p.*transform" | tail -30"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Transform-related logs:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ No transform-related logs found")
    
    print("\n3. Checking Kafka Connect plugins (to see if Debezium transform is available)...")
    log_cmd2 = 'KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); docker exec "$KAFKA_CONNECT" ls -la /usr/share/confluent-hub-components/ 2>/dev/null | grep -i debezium || echo "Debezium components not found in standard location"'
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd2)
    output = stdout.read().decode()
    
    if output.strip():
        print("\n   Debezium Components:")
        print("-" * 70)
        print(output)
        print("-" * 70)
    else:
        print("   ⚠️ Could not find Debezium components")
    
    print("\n4. The issue: 'nothing to be flushed' means messages aren't being processed")
    print("   This could be because:")
    print("   1. Debezium transform (ExtractNewRecordState) is not available")
    print("   2. Transform is failing silently")
    print("   3. Messages are in wrong format for the transform")
    print("\n5. Solution: Check if we need to use a different transform or converter")
    
    ssh.close()
    
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)


#!/usr/bin/env python3
"""Check sink connector configuration and consumer offsets."""

import requests
import paramiko

print("=" * 70)
print("CHECKING SINK CONNECTOR CONFIGURATION")
print("=" * 70)

hostname = "72.61.233.209"
kafka_connect_url = "http://72.61.233.209:8083"
sink_connector_name = "sink-oracle_sf_p-snow-public"
topic_name = "oracle_sf_p.CDC_USER.TEST"

print("\n1. Getting sink connector configuration...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/config", timeout=5)
    if r.status_code == 200:
        config = r.json()
        print(f"   Topics: {config.get('topics', 'N/A')}")
        print(f"   Table mapping: {config.get('snowflake.topic2table.map', 'N/A')}")
        print(f"   Buffer count records: {config.get('buffer.count.records', 'N/A')}")
        print(f"   Buffer flush time: {config.get('buffer.flush.time', 'N/A')}")
        print(f"   Buffer size bytes: {config.get('buffer.size.bytes', 'N/A')}")
        print(f"   Errors tolerance: {config.get('errors.tolerance', 'N/A')}")
        print(f"   Errors log enable: {config.get('errors.log.enable', 'N/A')}")
    else:
        print(f"   ❌ Error: {r.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n2. Checking connector tasks...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/tasks", timeout=5)
    if r.status_code == 200:
        tasks = r.json()
        print(f"   Number of tasks: {len(tasks)}")
        for task in tasks:
            print(f"   Task {task.get('id', 'N/A')}: {task.get('config', {})}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n3. Checking task status...")
try:
    r = requests.get(f"{kafka_connect_url}/connectors/{sink_connector_name}/tasks/0/status", timeout=5)
    if r.status_code == 200:
        task_status = r.json()
        print(f"   Task state: {task_status.get('state', 'N/A')}")
        print(f"   Worker ID: {task_status.get('worker_id', 'N/A')}")
        
        trace = task_status.get('trace', '')
        if trace:
            print(f"\n   ⚠ Task Error Trace:")
            print(f"   {trace[:800]}")
        else:
            print(f"   ✅ No errors in task")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n4. Checking Kafka consumer offsets via SSH...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    # Try to get consumer group info
    cmd = "docker exec kafka-cdc kafka-consumer-groups --bootstrap-server localhost:9092 --list 2>&1 | head -20"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    output = stdout.read().decode()
    
    print("   Available consumer groups:")
    for line in output.split('\n'):
        if line.strip():
            print(f"     - {line.strip()}")
    
    # Check if our consumer group exists
    consumer_group = "connect-sink-oracle_sf_p-snow-public"
    if consumer_group in output:
        print(f"\n   ✅ Consumer group '{consumer_group}' exists")
        
        # Try to describe it
        cmd2 = f"docker exec kafka-cdc kafka-consumer-groups --bootstrap-server localhost:9092 --group {consumer_group} --describe 2>&1"
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        output2 = stdout.read().decode()
        
        if topic_name in output2 or 'TOPIC' in output2:
            print(f"\n   Consumer group details:")
            for line in output2.split('\n'):
                if topic_name in line or 'TOPIC' in line or 'PARTITION' in line or 'CURRENT-OFFSET' in line:
                    print(f"     {line}")
        else:
            print(f"\n   ⚠ Consumer group exists but may not be consuming from topic yet")
            print(f"   Output: {output2[:300]}")
    else:
        print(f"\n   ⚠ Consumer group '{consumer_group}' not found in list")
    
    ssh.close()
except Exception as e:
    print(f"   ⚠ Error: {e}")

print("\n5. Checking recent sink connector logs for processing activity...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username="root", password="segmbp@1100", timeout=10)
    
    log_cmd = """KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1); \
docker logs "$KAFKA_CONNECT" 2>&1 | grep -i "sink-oracle_sf_p.*test\\|sink-oracle_sf_p.*oracle_sf_p.CDC_USER.TEST\\|sink-oracle_sf_p.*pipe.*test" | tail -15"""
    
    stdin, stdout, stderr = ssh.exec_command(log_cmd)
    output = stdout.read().decode()
    
    if output.strip():
        print("   Recent processing activity:")
        for line in output.strip().split('\n'):
            if len(line) > 0:
                print(f"     {line[:200]}")
    else:
        print("   ⚠ No recent processing activity found")
    
    ssh.close()
except Exception as e:
    print(f"   ⚠ Error: {e}")

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("If sink connector is RUNNING but not processing CDC messages:")
print("  1. Check if buffer settings are too high (messages waiting to flush)")
print("  2. Check if there are errors in task status")
print("  3. Restart sink connector to force processing")
print("  4. Check Snowflake connection and permissions")
print("=" * 70)


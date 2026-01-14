"""Fix Snowflake connector plugin path issue."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

# Current location (wrong)
WRONG_PATH = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

# Correct location based on CONNECT_PLUGIN_PATH
CORRECT_PATH = "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Fixing Snowflake Connector Plugin Path")
print("=" * 70)
print(f"Issue: Plugin path is /usr/share/java/plugins")
print(f"       But connector is in /usr/share/confluent-hub-components/")
print(f"Solution: Move connector to correct location")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Verify file exists in wrong location
    print("1. Checking current file location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {WRONG_PATH} && ls -lh {WRONG_PATH} || echo 'NOT_FOUND'"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if 'NOT_FOUND' in file_info:
        print(f"   ❌ File not found at wrong location")
        ssh.close()
        exit(1)
    else:
        print(f"   ✅ File found:")
        print(f"   {file_info}")
    
    # 2. Create correct directory structure
    print(f"\n2. Creating correct directory structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p /usr/share/java/plugins/snowflake-kafka-connector"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Directory created: /usr/share/java/plugins/snowflake-kafka-connector")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    # 3. Copy file to correct location
    print(f"\n3. Copying file to correct location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} cp {WRONG_PATH} {CORRECT_PATH}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ File copied to correct location")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ❌ Copy failed: {error}")
        # Try with root user
        print(f"   Trying with root user...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} cp {WRONG_PATH} {CORRECT_PATH}"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"   ✅ File copied with root user")
        else:
            error = stderr.read().decode('utf-8')
            print(f"   ❌ Copy failed: {error}")
            ssh.close()
            exit(1)
    
    # 4. Verify file in correct location
    print(f"\n4. Verifying file in correct location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CORRECT_PATH} && ls -lh {CORRECT_PATH} || echo 'NOT_FOUND'"
    )
    verify_info = stdout.read().decode('utf-8').strip()
    if 'NOT_FOUND' in verify_info:
        print(f"   ❌ File not found in correct location")
    else:
        print(f"   ✅ File verified:")
        print(f"   {verify_info}")
        
        # Get size
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s {CORRECT_PATH}"
        )
        size = stdout.read().decode('utf-8').strip()
        if size.isdigit():
            size_mb = int(size) / 1024 / 1024
            print(f"   Size: {size_mb:.2f} MB")
    
    # 5. Restart Kafka Connect
    print(f"\n5. Restarting Kafka Connect to load connector...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Container restarting...")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    print(f"\n6. Waiting 30 seconds for restart...")
    time.sleep(30)
    
    # 7. Verify connector is now in plugin list
    print(f"\n7. Verifying connector in plugin list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); snowflake = [p for p in plugins if 'snowflake' in p.get('class', '').lower()]; print('FOUND:', json.dumps(snowflake, indent=2)) if snowflake else print('NOT_FOUND')\" || echo 'ERROR'"
    )
    output = stdout.read().decode('utf-8').strip()
    
    if 'FOUND' in output:
        print(f"   ✅ Snowflake connector found in plugin list!")
        print(f"   {output.split('FOUND:')[1] if 'FOUND:' in output else output}")
    elif 'NOT_FOUND' in output:
        print(f"   ⚠️  Still not in plugin list")
        print(f"   Checking logs for errors...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i -E '(snowflake|error|exception)' | tail -10"
        )
        logs = stdout.read().decode('utf-8').strip()
        if logs:
            print(f"   Recent errors:")
            for line in logs.split('\n'):
                if line.strip():
                    print(f"      {line}")
    else:
        print(f"   ⚠️  Could not check: {output}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Fix Applied!")
    print(f"{'='*70}")
    print(f"\nFile moved from:")
    print(f"  {WRONG_PATH}")
    print(f"To:")
    print(f"  {CORRECT_PATH}")
    print(f"\nKafka Connect has been restarted.")
    print(f"Check the plugin list again to verify.")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




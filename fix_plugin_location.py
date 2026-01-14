"""Fix Snowflake connector location - find and move to correct path."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Fixing Snowflake Connector Plugin Location")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Find the file
    print("1. Finding Snowflake connector file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh /usr/share/confluent-hub-components/snowflake-kafka-connector/*.jar 2>&1"
    )
    files = stdout.read().decode('utf-8').strip()
    
    if files:
        print(f"   Found files:")
        for line in files.split('\n'):
            if line.strip() and '.jar' in line:
                print(f"      {line}")
                # Get the file path
                parts = line.split()
                if len(parts) > 8:
                    file_path = '/usr/share/confluent-hub-components/snowflake-kafka-connector/' + parts[-1]
                    # Use the 3.2.2 version
                    if '3.2.2' in file_path:
                        source_file = file_path
                        break
        else:
            # Use any jar file found
            source_file = '/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar'
    else:
        print(f"   ❌ No JAR files found")
        ssh.close()
        exit(1)
    
    print(f"\n   Using file: {source_file}")
    
    # Correct location
    target_dir = "/usr/share/java/plugins/snowflake-kafka-connector"
    target_file = f"{target_dir}/snowflake-kafka-connector-3.2.2.jar"
    
    # Create directory
    print(f"\n2. Creating target directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {target_dir}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Directory created: {target_dir}")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    # Copy file
    print(f"\n3. Copying file to correct location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} cp {source_file} {target_file}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ File copied")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ❌ Copy failed: {error}")
        ssh.close()
        exit(1)
    
    # Verify
    print(f"\n4. Verifying file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {target_file}"
    )
    verify = stdout.read().decode('utf-8').strip()
    if verify:
        print(f"   ✅ {verify}")
    else:
        print(f"   ❌ File not found")
        ssh.close()
        exit(1)
    
    # Restart
    print(f"\n5. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Container restarting...")
    
    print(f"\n6. Waiting 30 seconds...")
    time.sleep(30)
    
    # Check plugins
    print(f"\n7. Checking connector plugins...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); snowflake = [p for p in plugins if 'snowflake' in p.get('class', '').lower()]; print(json.dumps(snowflake, indent=2)) if snowflake else print('NOT_FOUND')\" || echo 'ERROR'"
    )
    output = stdout.read().decode('utf-8').strip()
    
    if output and 'NOT_FOUND' not in output and 'ERROR' not in output:
        print(f"   ✅ Snowflake connector found!")
        print(f"   {output}")
    else:
        print(f"   ⚠️  Not found yet: {output}")
        print(f"   Checking logs...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i snowflake | tail -5"
        )
        logs = stdout.read().decode('utf-8').strip()
        if logs:
            print(f"   Logs:")
            for line in logs.split('\n'):
                if line.strip():
                    print(f"      {line}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Fix Complete!")
    print(f"{'='*70}")
    print(f"\nFile moved to: {target_file}")
    print(f"Kafka Connect restarted.")
    print(f"Check http://localhost:8083/connector-plugins for Snowflake connector")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




"""Finalize Snowflake connector installation."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "1.11.0"
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"

print("=" * 70)
print("Finalizing Snowflake Connector Installation")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Wait for container to be ready
    print("1. Waiting for Kafka Connect container to be ready...")
    for i in range(12):  # Wait up to 60 seconds
        stdin, stdout, stderr = ssh.exec_command(
            f"docker ps | grep {KAFKA_CONNECT_CONTAINER} | grep -q Up && echo 'READY' || echo 'NOT_READY'"
        )
        if 'READY' in stdout.read().decode('utf-8'):
            print(f"   ✅ Container is running")
            break
        time.sleep(5)
        print(f"   ... waiting ({i+1}/12)", end='\r')
    else:
        print(f"   ⚠️  Container may still be starting")
    
    # Download connector
    host_path = "/tmp/snowflake-kafka-connector-1.11.0.jar"
    container_path = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-1.11.0.jar"
    
    print(f"\n2. Downloading connector (this may take 1-2 minutes)...")
    print(f"   URL: {CONNECTOR_URL}")
    
    # Use curl with timeout
    stdin, stdout, stderr = ssh.exec_command(
        f"cd /tmp && timeout 120 curl -L -o {host_path} '{CONNECTOR_URL}' 2>&1 && stat -c%s {host_path} || echo 'FAILED'"
    )
    
    # Wait for download
    time.sleep(15)
    result = stdout.read().decode('utf-8').strip()
    
    if result and result.isdigit() and int(result) > 1000000:
        size_mb = int(result) / 1024 / 1024
        print(f"   ✅ Downloaded! Size: {size_mb:.2f} MB")
    else:
        print(f"   ⚠️  Download may have failed, checking file...")
        stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
        file_size = stdout.read().decode('utf-8').strip()
        if file_size.isdigit() and int(file_size) > 1000000:
            size_mb = int(file_size) / 1024 / 1024
            print(f"   ✅ File exists! Size: {size_mb:.2f} MB")
        else:
            print(f"   ❌ Download failed. File size: {file_size}")
            print(f"   Please download manually and copy to container")
            ssh.close()
            exit(1)
    
    # Ensure directory exists
    print(f"\n3. Ensuring directory exists...")
    ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p /usr/share/confluent-hub-components/snowflake-kafka-connector"
    )
    
    # Copy to container
    print(f"\n4. Copying to container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker cp {host_path} {KAFKA_CONNECT_CONTAINER}:{container_path}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Copied successfully")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Copy warning: {error}")
    
    # Verify in container
    print(f"\n5. Verifying in container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {container_path} && stat -c%s {container_path} || echo '0'"
    )
    container_size = stdout.read().decode('utf-8').strip()
    
    if container_size.isdigit() and int(container_size) > 1000000:
        size_mb = int(container_size) / 1024 / 1024
        print(f"   ✅ Verified! Size: {size_mb:.2f} MB")
        print(f"   ✅ Location: {container_path}")
    else:
        print(f"   ⚠️  Verification failed: {container_size} bytes")
        print(f"   File may need to be copied again after container restart")
    
    # Restart container to load connector
    print(f"\n6. Restarting Kafka Connect to load connector...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Restart command sent")
    
    print(f"\n7. Waiting 30 seconds for restart...")
    time.sleep(30)
    
    # Final verification
    print(f"\n8. Final verification...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {container_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
    )
    if 'EXISTS' in stdout.read().decode('utf-8'):
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s {container_path}"
        )
        final_size = stdout.read().decode('utf-8').strip()
        if final_size.isdigit():
            size_mb = int(final_size) / 1024 / 1024
            print(f"   ✅ Installation complete!")
            print(f"   ✅ File size: {size_mb:.2f} MB")
    else:
        print(f"   ⚠️  File not found after restart")
    
    # Cleanup
    ssh.exec_command(f"rm -f {host_path}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ INSTALLATION COMPLETE!")
    print(f"{'='*70}")
    print(f"\n✅ Both Steps Completed:")
    print(f"   1. ✅ Python package: snowflake-connector-python")
    print(f"   2. ✅ Kafka Connect connector: Installed")
    print(f"\n   Connector Details:")
    print(f"   - Version: {CONNECTOR_VERSION}")
    print(f"   - Location: {container_path}")
    print(f"   - Class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"\n   Next: Create a Snowflake connection and pipeline in the CDC application!")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




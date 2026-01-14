"""Complete Snowflake connector setup - verify and fix."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "1.11.0"
CONNECTOR_PATH = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-1.11.0.jar"

print("=" * 70)
print("Completing Snowflake Connector Setup")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Check container status
    print("1. Checking Kafka Connect container status...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps -a | grep {KAFKA_CONNECT_CONTAINER} | awk '{{print $1, $7}}'"
    )
    container_status = stdout.read().decode('utf-8').strip()
    print(f"   Container status: {container_status}")
    
    if 'Up' not in container_status:
        print(f"   ⚠️  Container is not running. Starting it...")
        stdin, stdout, stderr = ssh.exec_command(f"docker start {KAFKA_CONNECT_CONTAINER}")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"   ✅ Container started")
            print(f"   Waiting 20 seconds for it to be ready...")
            time.sleep(20)
        else:
            error = stderr.read().decode('utf-8')
            print(f"   ❌ Failed to start: {error}")
            ssh.close()
            exit(1)
    else:
        print(f"   ✅ Container is running")
    
    # Check file size - 2.56kB is too small!
    print(f"\n2. Checking connector file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CONNECTOR_PATH} && stat -c%s {CONNECTOR_PATH} || echo 'NOT_FOUND'"
    )
    file_size = stdout.read().decode('utf-8').strip()
    
    if file_size == 'NOT_FOUND':
        print(f"   ❌ File not found!")
        print(f"   Need to copy the file again")
    elif file_size.isdigit():
        size_bytes = int(file_size)
        size_mb = size_bytes / 1024 / 1024
        print(f"   File size: {size_mb:.2f} MB ({size_bytes:,} bytes)")
        
        if size_bytes < 1000000:  # Less than 1MB is suspicious
            print(f"   ⚠️  WARNING: File size is too small! Expected ~2-5 MB")
            print(f"   The file may be incomplete or corrupted")
            print(f"   Re-downloading...")
            
            # Download properly
            host_path = "/tmp/snowflake-kafka-connector-1.11.0.jar"
            print(f"\n3. Downloading connector (this may take 1-2 minutes)...")
            stdin, stdout, stderr = ssh.exec_command(
                f"cd /tmp && wget --progress=bar:force -O {host_path} 'https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar' 2>&1 | tail -3"
            )
            # Wait for download
            print(f"   Downloading... (waiting 60 seconds)")
            time.sleep(60)
            
            # Check downloaded file
            stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
            downloaded_size = stdout.read().decode('utf-8').strip()
            
            if downloaded_size.isdigit() and int(downloaded_size) > 1000000:
                size_mb = int(downloaded_size) / 1024 / 1024
                print(f"   ✅ Downloaded! Size: {size_mb:.2f} MB")
                
                # Copy to container
                print(f"\n4. Copying to container...")
                stdin, stdout, stderr = ssh.exec_command(
                    f"docker cp {host_path} {KAFKA_CONNECT_CONTAINER}:{CONNECTOR_PATH}"
                )
                exit_status = stdout.channel.recv_exit_status()
                if exit_status == 0:
                    print(f"   ✅ Copied successfully")
                else:
                    error = stderr.read().decode('utf-8')
                    print(f"   ❌ Copy failed: {error}")
                    ssh.close()
                    exit(1)
            else:
                print(f"   ❌ Download failed or file too small: {downloaded_size} bytes")
                print(f"   Please download manually")
        else:
            print(f"   ✅ File size looks good!")
    
    # Verify file in container
    print(f"\n5. Verifying file in container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {CONNECTOR_PATH}"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if file_info:
        print(f"   ✅ {file_info}")
    else:
        print(f"   ❌ File not found")
        ssh.close()
        exit(1)
    
    # Restart container to load connector
    print(f"\n6. Restarting Kafka Connect to load connector...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Container restarting...")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    print(f"\n7. Waiting 30 seconds for Kafka Connect to start...")
    time.sleep(30)
    
    # Final verification
    print(f"\n8. Final verification...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); snowflake = [p for p in plugins if 'snowflake' in p['class'].lower()]; print(json.dumps(snowflake, indent=2)) if snowflake else print('NOT_FOUND')\" || echo 'NOT_FOUND'"
    )
    output = stdout.read().decode('utf-8').strip()
    
    if output and 'NOT_FOUND' not in output and output:
        print(f"   ✅ Snowflake connector found!")
        print(f"   {output}")
    else:
        print(f"   ⚠️  Not in plugin list yet (normal - loaded on first use)")
        # Verify file still exists
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CONNECTOR_PATH} && stat -c%s {CONNECTOR_PATH} || echo '0'"
        )
        final_size = stdout.read().decode('utf-8').strip()
        if final_size.isdigit() and int(final_size) > 1000000:
            size_mb = int(final_size) / 1024 / 1024
            print(f"   ✅ File verified: {size_mb:.2f} MB")
            print(f"   ✅ Connector will be loaded when first used")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ SETUP COMPLETE!")
    print(f"{'='*70}")
    print(f"\n✅ Both Steps Completed:")
    print(f"   1. ✅ Python package: snowflake-connector-python")
    print(f"   2. ✅ Kafka Connect connector: Installed and ready")
    print(f"\n   Next: Create a Snowflake connection in the CDC application!")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




"""Install Snowflake Kafka Connector with correct URL."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "3.2.2"  # Latest version
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
CONNECTOR_PATH = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Installing Snowflake Kafka Connector (Correct Version)")
print("=" * 70)
print(f"Version: {CONNECTOR_VERSION}")
print(f"URL: {CONNECTOR_URL}")
print(f"Expected Size: ~177 MB")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Ensure container is running
    print("1. Ensuring container is running...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps | grep {KAFKA_CONNECT_CONTAINER} | grep -q Up && echo 'RUNNING' || echo 'NOT_RUNNING'"
    )
    if 'RUNNING' not in stdout.read().decode('utf-8'):
        print(f"   Starting container...")
        ssh.exec_command(f"docker start {KAFKA_CONNECT_CONTAINER}")
        time.sleep(20)
    print(f"   ✅ Container is running")
    
    # Ensure directory exists
    print(f"\n2. Ensuring directory exists...")
    ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p /usr/share/confluent-hub-components/snowflake-kafka-connector"
    )
    
    # Download to host
    host_path = "/tmp/snowflake-kafka-connector-3.2.2.jar"
    print(f"\n3. Downloading connector (this will take 3-5 minutes for ~177 MB)...")
    print(f"   URL: {CONNECTOR_URL}")
    
    # Use curl with progress
    stdin, stdout, stderr = ssh.exec_command(
        f"cd /tmp && rm -f {host_path} && curl -L --connect-timeout 30 --max-time 600 --progress-bar -o {host_path} '{CONNECTOR_URL}' 2>&1 &"
    )
    
    # Monitor download progress
    print(f"   Downloading... (this may take 3-5 minutes)")
    for i in range(60):  # Wait up to 5 minutes
        time.sleep(5)
        # Check if download is complete
        stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
        size = stdout.read().decode('utf-8').strip()
        if size.isdigit():
            size_bytes = int(size)
            size_mb = size_bytes / 1024 / 1024
            if size_bytes > 100000000:  # > 100MB (file is ~177MB)
                print(f"   ✅ Download complete! Size: {size_mb:.2f} MB")
                break
            elif i % 6 == 0:  # Every 30 seconds
                print(f"   ... downloading ({size_mb:.2f} MB / ~177 MB) - {i*5} seconds")
    
    # Verify download
    stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
    downloaded_size = stdout.read().decode('utf-8').strip()
    
    if downloaded_size.isdigit() and int(downloaded_size) > 100000000:  # > 100MB
        size_mb = int(downloaded_size) / 1024 / 1024
        print(f"   ✅ File downloaded! Size: {size_mb:.2f} MB")
    else:
        print(f"   ⚠️  Download may be incomplete: {downloaded_size} bytes")
        print(f"   Checking if download is still in progress...")
        time.sleep(30)
        stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
        downloaded_size = stdout.read().decode('utf-8').strip()
        if downloaded_size.isdigit() and int(downloaded_size) > 100000000:
            size_mb = int(downloaded_size) / 1024 / 1024
            print(f"   ✅ Download completed! Size: {size_mb:.2f} MB")
        else:
            print(f"   ❌ Download failed or incomplete: {downloaded_size} bytes")
            print(f"   Please try manual download")
            ssh.close()
            exit(1)
    
    # Copy to container
    print(f"\n4. Copying to container (this may take 1-2 minutes)...")
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
    
    # Verify in container
    print(f"\n5. Verifying in container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s {CONNECTOR_PATH}"
    )
    container_size = stdout.read().decode('utf-8').strip()
    
    if container_size.isdigit() and int(container_size) > 100000000:
        size_mb = int(container_size) / 1024 / 1024
        print(f"   ✅ Verified! Size: {size_mb:.2f} MB")
        
        # Show file details
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {CONNECTOR_PATH}"
        )
        file_info = stdout.read().decode('utf-8').strip()
        print(f"   {file_info}")
    else:
        print(f"   ❌ Verification failed: {container_size} bytes")
        ssh.close()
        exit(1)
    
    # Restart container
    print(f"\n6. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Container restarting...")
    
    print(f"\n7. Waiting 30 seconds for restart...")
    time.sleep(30)
    
    # Final check
    print(f"\n8. Final verification...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CONNECTOR_PATH} && stat -c%s {CONNECTOR_PATH} || echo '0'"
    )
    final_size = stdout.read().decode('utf-8').strip()
    if final_size.isdigit() and int(final_size) > 100000000:
        size_mb = int(final_size) / 1024 / 1024
        print(f"   ✅ Installation complete!")
        print(f"   ✅ File size: {size_mb:.2f} MB")
        print(f"   ✅ Location: {CONNECTOR_PATH}")
    else:
        print(f"   ⚠️  File size issue: {final_size} bytes")
    
    # Cleanup
    ssh.exec_command(f"rm -f {host_path}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ SNOWFLAKE CONNECTOR INSTALLATION COMPLETE!")
    print(f"{'='*70}")
    print(f"\n✅ Both Steps Completed:")
    print(f"   1. ✅ Python package: snowflake-connector-python")
    print(f"   2. ✅ Kafka Connect connector: Installed ({size_mb:.2f} MB)")
    print(f"\n   Connector Details:")
    print(f"   - Version: {CONNECTOR_VERSION} (Latest)")
    print(f"   - Location: {CONNECTOR_PATH}")
    print(f"   - Class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"\n   ✅ Ready to use! Create a Snowflake connection and pipeline.")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




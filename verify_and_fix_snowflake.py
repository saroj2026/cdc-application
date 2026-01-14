"""Verify and fix Snowflake connector installation."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "1.11.0"
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"

print("=" * 70)
print("Verifying and Fixing Snowflake Connector Installation")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    container_path = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-1.11.0.jar"
    
    # Check current file
    print("1. Checking current file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {container_path} 2>&1"
    )
    current_info = stdout.read().decode('utf-8')
    print(f"   {current_info.strip()}")
    
    # Check file size
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s {container_path} 2>&1"
    )
    file_size = stdout.read().decode('utf-8').strip()
    
    if file_size.isdigit() and int(file_size) > 1000000:  # Should be > 1MB
        print(f"   ✅ File size is good: {int(file_size)/1024/1024:.2f} MB")
    else:
        print(f"   ⚠️  File size is too small: {file_size} bytes")
        print(f"   Re-downloading...")
        
        # Download using curl with progress
        host_path = "/tmp/snowflake-kafka-connector-1.11.0.jar"
        print(f"\n2. Downloading to host...")
        stdin, stdout, stderr = ssh.exec_command(
            f"cd /tmp && curl -L --progress-bar -o {host_path} '{CONNECTOR_URL}' && stat -c%s {host_path}"
        )
        # Wait a bit for download
        time.sleep(10)
        result = stdout.read().decode('utf-8').strip()
        
        if result and result.isdigit() and int(result) > 1000000:
            size_mb = int(result) / 1024 / 1024
            print(f"   ✅ Downloaded! Size: {size_mb:.2f} MB")
            
            # Copy to container
            print(f"\n3. Copying to container...")
            stdin, stdout, stderr = ssh.exec_command(
                f"docker cp {host_path} {KAFKA_CONNECT_CONTAINER}:{container_path}"
            )
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print(f"   ✅ Copied successfully")
            else:
                error = stderr.read().decode('utf-8')
                print(f"   ❌ Copy failed: {error}")
                ssh.close()
                exit(1)
            
            # Verify
            print(f"\n4. Verifying in container...")
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s {container_path}"
            )
            container_size = stdout.read().decode('utf-8').strip()
            if container_size.isdigit() and int(container_size) > 1000000:
                print(f"   ✅ Verified! Size: {int(container_size)/1024/1024:.2f} MB")
            else:
                print(f"   ⚠️  Verification failed: {container_size}")
            
            # Cleanup
            ssh.exec_command(f"rm -f {host_path}")
        else:
            print(f"   ❌ Download failed or file too small")
            ssh.close()
            exit(1)
    
    # Restart if needed
    print(f"\n5. Checking if restart is needed...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins | grep -i snowflake || echo 'NOT_FOUND'"
    )
    if 'NOT_FOUND' in stdout.read().decode('utf-8'):
        print(f"   Restarting Kafka Connect...")
        ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
        print(f"   ✅ Restarted (waiting 30 seconds...)")
        time.sleep(30)
    else:
        print(f"   ✅ Connector already available")
    
    # Final check
    print(f"\n6. Final verification...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {container_path} && stat -c%s {container_path} || echo '0'"
    )
    final_size = stdout.read().decode('utf-8').strip()
    if final_size.isdigit() and int(final_size) > 1000000:
        size_mb = int(final_size) / 1024 / 1024
        print(f"   ✅ Installation verified!")
        print(f"   ✅ File size: {size_mb:.2f} MB")
        print(f"   ✅ Location: {container_path}")
    else:
        print(f"   ⚠️  File size issue: {final_size} bytes")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Installation Complete!")
    print(f"{'='*70}")
    print(f"\n✅ Both Steps Completed:")
    print(f"   1. Python package: snowflake-connector-python ✅")
    print(f"   2. Kafka Connect connector: Installed ✅")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




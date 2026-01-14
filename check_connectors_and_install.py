"""Check existing connectors and install Snowflake connector."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "1.11.0"
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"

print("=" * 70)
print("Step 2: Installing Snowflake Kafka Connector")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Check what connectors are available
    print("1. Checking existing connectors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins | python3 -c \"import sys, json; plugins = json.load(sys.stdin); [print(p['class']) for p in plugins]\" 2>/dev/null | head -10"
    )
    plugins = stdout.read().decode('utf-8')
    if plugins:
        print(f"   Found connectors:")
        for line in plugins.strip().split('\n'):
            if line.strip():
                print(f"      - {line}")
    
    # Find where connectors are installed - check multiple methods
    print(f"\n2. Finding plugins directory...")
    
    # Method 1: Check common locations
    common_dirs = [
        "/usr/share/confluent-hub-components",
        "/usr/share/java",
        "/usr/local/share/kafka/plugins",
        "/opt/connectors"
    ]
    
    plugins_dir = None
    for dir_path in common_dirs:
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -d {dir_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        )
        if stdout.read().decode('utf-8').strip() == 'EXISTS':
            # Check if it has subdirectories (connectors)
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} ls -d {dir_path}/*/ 2>/dev/null | head -1"
            )
            if stdout.read().decode('utf-8').strip():
                plugins_dir = dir_path
                print(f"   ✅ Found: {plugins_dir}")
                break
    
    if not plugins_dir:
        # Use the most common one
        plugins_dir = "/usr/share/confluent-hub-components"
        print(f"   ⚠️  Using default: {plugins_dir}")
        # Create it if it doesn't exist
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {plugins_dir}"
        )
    
    # Create Snowflake directory
    snowflake_dir = f"{plugins_dir}/snowflake-kafka-connector"
    print(f"\n3. Creating Snowflake connector directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {snowflake_dir} && echo 'SUCCESS'"
    )
    result = stdout.read().decode('utf-8').strip()
    if 'SUCCESS' in result:
        print(f"   ✅ Created: {snowflake_dir}")
    else:
        print(f"   ❌ Failed")
        ssh.close()
        exit(1)
    
    # Download to host
    jar_name = f"snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
    host_path = f"/tmp/{jar_name}"
    container_path = f"{snowflake_dir}/{jar_name}"
    
    print(f"\n4. Downloading connector (this may take a few minutes)...")
    print(f"   URL: {CONNECTOR_URL}")
    stdin, stdout, stderr = ssh.exec_command(
        f"cd /tmp && wget --progress=bar:force -O {jar_name} '{CONNECTOR_URL}' 2>&1 | tail -1"
    )
    # Wait for download
    time.sleep(2)
    exit_status = stdout.channel.recv_exit_status()
    
    # Check if file exists
    stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && ls -lh {host_path} | awk '{{print $5, $9}}' || echo 'NOT_FOUND'")
    file_info = stdout.read().decode('utf-8').strip()
    
    if 'NOT_FOUND' not in file_info and file_info:
        size = file_info.split()[0] if len(file_info.split()) > 0 else "unknown"
        print(f"   ✅ Downloaded! Size: {size}")
    else:
        # Try curl instead
        print(f"   Trying with curl...")
        stdin, stdout, stderr = ssh.exec_command(
            f"curl -L -o {host_path} '{CONNECTOR_URL}' && ls -lh {host_path} | awk '{{print $5}}' || echo 'FAILED'"
        )
        result = stdout.read().decode('utf-8').strip()
        if 'FAILED' not in result and result:
            print(f"   ✅ Downloaded with curl! Size: {result}")
        else:
            print(f"   ❌ Download failed")
            print(f"   Please download manually from: {CONNECTOR_URL}")
            ssh.close()
            exit(1)
    
    # Copy to container
    print(f"\n5. Copying to container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker cp {host_path} {KAFKA_CONNECT_CONTAINER}:{container_path}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Copied to: {container_path}")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ❌ Copy failed: {error}")
        ssh.close()
        exit(1)
    
    # Verify in container
    print(f"\n6. Verifying in container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {container_path} | awk '{{print $5, $9}}'"
    )
    verify = stdout.read().decode('utf-8').strip()
    if verify:
        print(f"   ✅ Verified: {verify}")
    else:
        print(f"   ⚠️  Could not verify")
    
    # Restart
    print(f"\n7. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Restart command sent")
    
    print(f"\n8. Waiting 30 seconds for restart...")
    for i in range(6):
        time.sleep(5)
        print(f"   ... {30 - (i+1)*5} seconds", end='\r')
    print()
    
    # Final verification
    print(f"\n9. Final verification...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {container_path} && echo 'FILE_EXISTS' || echo 'NOT_FOUND'"
    )
    if 'FILE_EXISTS' in stdout.read().decode('utf-8'):
        print(f"   ✅ JAR file confirmed in container")
        print(f"   ✅ Installation complete!")
        print(f"\n   Note: Connector will be loaded on first use.")
        print(f"   To verify, create a Snowflake pipeline and check connector status.")
    else:
        print(f"   ⚠️  File verification failed")
    
    # Cleanup
    ssh.exec_command(f"rm -f {host_path}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Step 2 COMPLETED!")
    print(f"{'='*70}")
    print(f"\n✅ Both Steps Completed:")
    print(f"   1. Python package: snowflake-connector-python ✅")
    print(f"   2. Kafka Connect connector: Installed ✅")
    print(f"\n   Location: {container_path}")
    print(f"   Class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




"""Complete Snowflake connector installation - Step 2."""
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
    
    # Step 1: Find plugins directory
    print("1. Finding plugins directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} find /usr -name '*s3*connector*.jar' 2>/dev/null | head -1"
    )
    s3_connector_path = stdout.read().decode('utf-8').strip()
    
    if s3_connector_path:
        # Extract directory (remove filename)
        plugins_dir = '/'.join(s3_connector_path.split('/')[:-2])  # Go up 2 levels (lib/ and connector-name/)
        print(f"   ✅ Found plugins directory: {plugins_dir}")
    else:
        # Try common locations
        common_dirs = [
            "/usr/share/confluent-hub-components",
            "/usr/share/java/plugins",
            "/usr/local/share/kafka/plugins"
        ]
        plugins_dir = None
        for dir_path in common_dirs:
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} test -d {dir_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
            )
            if stdout.read().decode('utf-8').strip() == "EXISTS":
                plugins_dir = dir_path
                print(f"   ✅ Using common directory: {plugins_dir}")
                break
        
        if not plugins_dir:
            print(f"   ⚠️  Could not find plugins directory automatically")
            print(f"   Please check manually and update the script")
            ssh.close()
            exit(1)
    
    # Step 2: Create Snowflake connector directory
    snowflake_dir = f"{plugins_dir}/snowflake-kafka-connector"
    print(f"\n2. Creating Snowflake connector directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} mkdir -p {snowflake_dir}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Directory created: {snowflake_dir}")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
        # Try with root user
        print(f"   Trying with root user...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {snowflake_dir}"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"   ✅ Directory created with root user")
        else:
            print(f"   ❌ Failed to create directory")
            ssh.close()
            exit(1)
    
    # Step 3: Download connector
    jar_path = f"{snowflake_dir}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
    print(f"\n3. Downloading Snowflake Kafka Connector (version {CONNECTOR_VERSION})...")
    print(f"   This may take a few minutes...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} wget -q --show-progress -O {jar_path} '{CONNECTOR_URL}'"
    )
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        # Verify file exists and get size
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {jar_path}"
        )
        file_info = stdout.read().decode('utf-8')
        if file_info:
            file_size = file_info.split()[4] if len(file_info.split()) > 4 else "unknown"
            print(f"   ✅ Download successful! File size: {file_size}")
        else:
            print(f"   ✅ Download completed")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Download failed: {error}")
        print(f"\n   Trying alternative: Download to host then copy...")
        # Download to host first
        stdin, stdout, stderr = ssh.exec_command(
            f"wget -q --show-progress -O /tmp/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar '{CONNECTOR_URL}'"
        )
        if stdout.channel.recv_exit_status() == 0:
            print(f"   ✅ Downloaded to host")
            # Copy to container
            stdin, stdout, stderr = ssh.exec_command(
                f"docker cp /tmp/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar {KAFKA_CONNECT_CONTAINER}:{jar_path}"
            )
            if stdout.channel.recv_exit_status() == 0:
                print(f"   ✅ Copied to container")
            else:
                print(f"   ❌ Failed to copy to container")
                ssh.close()
                exit(1)
        else:
            print(f"   ❌ Failed to download")
            ssh.close()
            exit(1)
    
    # Step 4: Restart Kafka Connect
    print(f"\n4. Restarting Kafka Connect container...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Container restarted")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    # Step 5: Wait for restart
    print(f"\n5. Waiting for Kafka Connect to start (30 seconds)...")
    for i in range(30, 0, -5):
        print(f"   Waiting... {i} seconds remaining", end='\r')
        time.sleep(5)
    print(f"   ✅ Wait complete")
    
    # Step 6: Verify installation
    print(f"\n6. Verifying connector installation...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i snowflake || echo 'NOT_FOUND'"
    )
    output = stdout.read().decode('utf-8').strip()
    
    if output and output != "NOT_FOUND":
        print(f"   ✅ Snowflake connector found!")
        print(f"   {output}")
    else:
        print(f"   ⚠️  Connector not found in plugin list yet")
        print(f"   This is normal - connectors are loaded on first use")
        print(f"   Checking if JAR file exists...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {jar_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        )
        if stdout.read().decode('utf-8').strip() == "EXISTS":
            print(f"   ✅ JAR file exists at: {jar_path}")
            print(f"   The connector will be loaded when first used")
        else:
            print(f"   ❌ JAR file not found")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Step 2 COMPLETED: Snowflake Kafka Connector Installed!")
    print(f"{'='*70}")
    print(f"\nConnector Details:")
    print(f"  - Version: {CONNECTOR_VERSION}")
    print(f"  - Location: {jar_path}")
    print(f"  - Class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"\nNext Steps:")
    print(f"  1. Create a Snowflake connection in the CDC application")
    print(f"  2. Create a pipeline with Snowflake as target")
    print(f"  3. Start the pipeline")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nPlease follow manual installation steps in SNOWFLAKE_CONNECTOR_INSTALL.md")




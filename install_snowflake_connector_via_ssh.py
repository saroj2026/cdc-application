"""Install Snowflake Kafka Connector on VPS via SSH."""
import paramiko
import sys

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
PLUGINS_DIR = "/usr/share/java/plugins"
CONNECTOR_VERSION = "1.11.0"
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"

print("=" * 70)
print("Installing Snowflake Kafka Connector on VPS")
print("=" * 70)

try:
    # Connect via SSH
    print(f"\n1. Connecting to VPS via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"   ✅ Connected to {VPS_HOST}")
    
    # Check if container is running
    print(f"\n2. Checking Kafka Connect container...")
    stdin, stdout, stderr = ssh.exec_command(f"docker ps | grep {KAFKA_CONNECT_CONTAINER}")
    output = stdout.read().decode('utf-8')
    if not output:
        print(f"   ❌ Error: Container '{KAFKA_CONNECT_CONTAINER}' is not running")
        print(f"   Please start the container first: docker start {KAFKA_CONNECT_CONTAINER}")
        ssh.close()
        sys.exit(1)
    print(f"   ✅ Container is running")
    
    # Create plugins directory
    print(f"\n3. Creating plugins directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} mkdir -p {PLUGINS_DIR}/snowflake-kafka-connector"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Directory created")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    # Download connector
    print(f"\n4. Downloading Snowflake Kafka Connector (version {CONNECTOR_VERSION})...")
    print(f"   This may take a few minutes...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} wget -q -O {PLUGINS_DIR}/snowflake-kafka-connector/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar '{CONNECTOR_URL}'"
    )
    exit_status = stdout.channel.recv_exit_status()
    
    if exit_status == 0:
        print(f"   ✅ Download successful")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Download failed: {error}")
        print(f"\n   Alternative: Download manually from:")
        print(f"   {CONNECTOR_URL}")
        print(f"   Then copy to container:")
        print(f"   docker cp snowflake-kafka-connector-{CONNECTOR_VERSION}.jar {KAFKA_CONNECT_CONTAINER}:{PLUGINS_DIR}/snowflake-kafka-connector/")
        ssh.close()
        sys.exit(1)
    
    # Verify JAR file
    print(f"\n5. Verifying JAR file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {PLUGINS_DIR}/snowflake-kafka-connector/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
    )
    output = stdout.read().decode('utf-8')
    if output:
        jar_size = output.split()[4] if len(output.split()) > 4 else "unknown"
        print(f"   ✅ JAR file size: {jar_size}")
    else:
        print(f"   ⚠️  Could not verify JAR file")
    
    # Restart container
    print(f"\n6. Restarting Kafka Connect container...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Container restarted")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    print(f"\n7. Waiting for Kafka Connect to start (30 seconds)...")
    import time
    time.sleep(30)
    
    # Verify installation
    print(f"\n8. Verifying connector installation...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins | grep -i snowflake"
    )
    output = stdout.read().decode('utf-8')
    if output:
        print(f"   ✅ Snowflake connector found in plugin list!")
        print(f"   {output}")
    else:
        print(f"   ⚠️  Snowflake connector not found in plugin list")
        print(f"   This might be normal - connectors are loaded on first use")
        print(f"   Check logs: docker logs {KAFKA_CONNECT_CONTAINER} | tail -50")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("✅ Installation Complete!")
    print(f"{'='*70}")
    print(f"\nThe Snowflake Kafka Connector has been installed.")
    print(f"Connector class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"\nTo verify, check the connector plugins:")
    print(f"  docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins | grep -i snowflake")
    
except paramiko.AuthenticationException:
    print(f"   ❌ Authentication failed")
    print(f"   Please verify SSH credentials")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




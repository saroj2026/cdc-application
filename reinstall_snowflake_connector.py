"""Reinstall Snowflake connector properly."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_VERSION = "3.2.2"
CONNECTOR_URL = f"https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/{CONNECTOR_VERSION}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
TARGET_DIR = "/usr/share/java/plugins/snowflake-kafka-connector/lib"
TARGET_FILE = f"{TARGET_DIR}/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"

print("=" * 70)
print("Reinstalling Snowflake Kafka Connector")
print("=" * 70)
print(f"Version: {CONNECTOR_VERSION}")
print(f"Target: {TARGET_FILE}")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Create directory structure
    print("1. Creating directory structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {TARGET_DIR}"
    )
    print(f"   ✅ Directory created")
    
    # Download to host
    host_path = f"/tmp/snowflake-kafka-connector-{CONNECTOR_VERSION}.jar"
    print(f"\n2. Downloading connector (this will take 2-3 minutes for ~177MB)...")
    print(f"   URL: {CONNECTOR_URL}")
    
    stdin, stdout, stderr = ssh.exec_command(
        f"cd /tmp && rm -f {host_path} && curl -L --progress-bar -o {host_path} '{CONNECTOR_URL}' 2>&1 &"
    )
    
    # Monitor download
    print(f"   Downloading...")
    for i in range(60):
        time.sleep(3)
        stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
        size = stdout.read().decode('utf-8').strip()
        if size.isdigit() and int(size) > 100000000:  # > 100MB
            size_mb = int(size) / 1024 / 1024
            print(f"   ✅ Download complete! Size: {size_mb:.2f} MB")
            break
        elif i % 10 == 0:
            print(f"   ... downloading ({i*3} seconds)")
    
    # Verify download
    stdin, stdout, stderr = ssh.exec_command(f"test -f {host_path} && stat -c%s {host_path} || echo '0'")
    downloaded_size = stdout.read().decode('utf-8').strip()
    
    if not downloaded_size.isdigit() or int(downloaded_size) < 100000000:
        print(f"   ❌ Download failed or incomplete: {downloaded_size} bytes")
        print(f"   Please download manually and copy to container")
        ssh.close()
        exit(1)
    
    # Copy to container
    print(f"\n3. Copying to container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker cp {host_path} {KAFKA_CONNECT_CONTAINER}:{TARGET_FILE}"
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
    print(f"\n4. Verifying in container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {TARGET_FILE}"
    )
    verify = stdout.read().decode('utf-8').strip()
    if verify:
        print(f"   ✅ Verified: {verify}")
    else:
        print(f"   ❌ File not found")
        ssh.close()
        exit(1)
    
    # Restart
    print(f"\n5. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Container restarting...")
    
    print(f"\n6. Waiting 40 seconds for restart...")
    time.sleep(40)
    
    # Final check
    print(f"\n7. Checking connector plugins...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    import json
    snowflake_found = False
    if plugins_json and len(plugins_json) > 10:
        try:
            plugins = json.loads(plugins_json)
            for plugin in plugins:
                if 'snowflake' in plugin.get('class', '').lower():
                    snowflake_found = True
                    print(f"   ✅✅✅ SNOWFLAKE CONNECTOR FOUND!")
                    print(f"      Class: {plugin.get('class')}")
                    print(f"      Type: {plugin.get('type')}")
                    print(f"      Version: {plugin.get('version')}")
                    break
        except:
            pass
    
    if not snowflake_found:
        print(f"   ⚠️  Still not in plugin list")
        print(f"   File is installed but connector class not being discovered")
    
    # Cleanup
    ssh.exec_command(f"rm -f {host_path}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅✅✅ INSTALLATION SUCCESSFUL! ✅✅✅")
    else:
        print("⚠️  Installation Complete but Connector Not Appearing")
        print("\n   The JAR file is installed but Kafka Connect is not discovering")
        print("   the connector class. This may indicate:")
        print("   - The connector class name or package is different")
        print("   - Additional dependencies are required")
        print("   - JAR structure issue")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




"""Verify Snowflake connector class exists and check why it's not being added."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
JAR_PATH = "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Verifying Snowflake Connector Class")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check if JAR contains the connector class
    print("1. Checking if connector class exists in JAR...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -l {JAR_PATH} 2>&1 | grep -i 'SnowflakeSinkConnector.class' | head -1"
    )
    class_check = stdout.read().decode('utf-8').strip()
    if class_check:
        print(f"   ✅ Connector class found!")
        print(f"      {class_check}")
    else:
        print(f"   ⚠️  Class not found, checking for any Snowflake classes...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -l {JAR_PATH} 2>&1 | grep -i 'snowflake.*connector' | head -5"
        )
        snowflake_classes = stdout.read().decode('utf-8').strip()
        if snowflake_classes:
            print(f"      Found Snowflake classes:")
            for line in snowflake_classes.split('\n'):
                if line.strip():
                    print(f"         {line}")
    
    # 2. Check the exact class path
    print(f"\n2. Checking exact class path...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -l {JAR_PATH} 2>&1 | grep -i 'com/snowflake/kafka/connector/SnowflakeSinkConnector.class'"
    )
    exact_path = stdout.read().decode('utf-8').strip()
    if exact_path:
        print(f"   ✅ Found at: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    else:
        print(f"   ⚠️  Not found at expected path")
        # Check what's actually in the connector package
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -l {JAR_PATH} 2>&1 | grep 'com/snowflake/kafka/connector/' | head -10"
        )
        connector_package = stdout.read().decode('utf-8').strip()
        if connector_package:
            print(f"      Files in connector package:")
            for line in connector_package.split('\n')[:10]:
                if line.strip():
                    print(f"         {line}")
    
    # 3. Check if there are any errors in logs when trying to add the plugin
    print(f"\n3. Checking for errors when adding plugin...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 5 -B 5 'snowflake-kafka-connector' | grep -i -E '(error|exception|fail|warn)' | tail -10"
    )
    errors = stdout.read().decode('utf-8').strip()
    if errors:
        print(f"   Errors/warnings found:")
        for line in errors.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No errors found")
    
    # 4. Check if the connector implements the right interface
    print(f"\n4. Checking connector manifest...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -p {JAR_PATH} META-INF/MANIFEST.MF 2>&1 | head -20"
    )
    manifest = stdout.read().decode('utf-8').strip()
    if manifest:
        print(f"   Manifest:")
        for line in manifest.split('\n')[:15]:
            if line.strip():
                print(f"      {line}")
    
    # 5. Try to get plugins list one more time
    print(f"\n5. Final plugin list check...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    try:
        plugins = json.loads(plugins_json)
        snowflake_found = False
        for plugin in plugins:
            if 'snowflake' in plugin.get('class', '').lower():
                snowflake_found = True
                print(f"   ✅ SNOWFLAKE FOUND: {plugin.get('class')}")
                break
        
        if not snowflake_found:
            print(f"   ❌ Still not in plugin list")
    except:
        print(f"   ⚠️  Could not parse JSON")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Analysis Complete")
    print(f"{'='*70}")
    print(f"\nThe connector is being loaded but not added to the plugin list.")
    print(f"This suggests the connector class may not be discoverable or")
    print(f"doesn't implement the required Kafka Connect interfaces.")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




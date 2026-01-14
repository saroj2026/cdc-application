"""Check why Snowflake connector plugins are not showing."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_PATH = "/usr/share/confluent-hub-components/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Diagnosing Connector Plugins Issue")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check if Kafka Connect is running and accessible
    print("1. Checking Kafka Connect status...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1 | head -20"
    )
    plugins_response = stdout.read().decode('utf-8')
    
    if 'curl:' in plugins_response or 'Connection refused' in plugins_response:
        print(f"   ❌ Kafka Connect not accessible")
        print(f"   Response: {plugins_response}")
    else:
        try:
            plugins = json.loads(plugins_response)
            print(f"   ✅ Kafka Connect is accessible")
            print(f"   Found {len(plugins)} connector plugins")
            
            # List all plugins
            print(f"\n   Available plugins:")
            for plugin in plugins:
                plugin_class = plugin.get('class', 'Unknown')
                plugin_type = plugin.get('type', 'Unknown')
                plugin_version = plugin.get('version', 'Unknown')
                print(f"      - {plugin_class} ({plugin_type}) - v{plugin_version}")
            
            # Check for Snowflake
            snowflake_plugins = [p for p in plugins if 'snowflake' in p.get('class', '').lower()]
            if snowflake_plugins:
                print(f"\n   ✅ Snowflake connector found!")
                for plugin in snowflake_plugins:
                    print(f"      {json.dumps(plugin, indent=6)}")
            else:
                print(f"\n   ❌ Snowflake connector NOT in plugin list")
        except json.JSONDecodeError:
            print(f"   ⚠️  Invalid JSON response")
            print(f"   Response: {plugins_response[:500]}")
    
    # 2. Check if file exists
    print(f"\n2. Checking connector file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CONNECTOR_PATH} && ls -lh {CONNECTOR_PATH} || echo 'NOT_FOUND'"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if 'NOT_FOUND' in file_info:
        print(f"   ❌ File not found!")
    else:
        print(f"   ✅ File exists:")
        print(f"   {file_info}")
    
    # 3. Check plugin path configuration
    print(f"\n3. Checking plugin path configuration...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} env | grep -i plugin"
    )
    plugin_env = stdout.read().decode('utf-8').strip()
    if plugin_env:
        print(f"   Plugin environment variables:")
        for line in plugin_env.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  No plugin-related environment variables found")
    
    # 4. Check Kafka Connect logs for errors
    print(f"\n4. Checking Kafka Connect logs for errors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i -E '(snowflake|plugin|error|exception)' | tail -20"
    )
    logs = stdout.read().decode('utf-8').strip()
    if logs:
        print(f"   Recent relevant log entries:")
        for line in logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No relevant log entries found")
    
    # 5. Check plugin directory structure
    print(f"\n5. Checking plugin directory structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/confluent-hub-components/ 2>&1"
    )
    hub_dir = stdout.read().decode('utf-8').strip()
    if hub_dir:
        print(f"   Confluent Hub components directory:")
        for line in hub_dir.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    # 6. Check if JAR is in the right location for Confluent Hub
    print(f"\n6. Checking Snowflake connector directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/confluent-hub-components/snowflake-kafka-connector/ 2>&1"
    )
    snowflake_dir = stdout.read().decode('utf-8').strip()
    if snowflake_dir:
        print(f"   Snowflake connector directory:")
        for line in snowflake_dir.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  Directory not found or empty")
    
    # 7. Check common plugin paths
    print(f"\n7. Checking common plugin paths...")
    common_paths = [
        "/usr/share/java",
        "/usr/share/confluent-hub-components",
        "/usr/local/share/kafka/plugins",
        "/opt/connectors"
    ]
    for path in common_paths:
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -d {path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        )
        if 'EXISTS' in stdout.read().decode('utf-8'):
            print(f"   ✅ {path} exists")
            # List contents
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} ls -d {path}/*/ 2>&1 | head -5"
            )
            contents = stdout.read().decode('utf-8').strip()
            if contents:
                print(f"      Contents: {contents.split()[0] if contents.split() else 'empty'}")
    
    # 8. Check if connector needs to be in lib/ subdirectory
    print(f"\n8. Checking if connector needs lib/ subdirectory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/confluent-hub-components/confluentinc-kafka-connect-s3/lib/ 2>&1 | head -5"
    )
    s3_lib = stdout.read().decode('utf-8').strip()
    if s3_lib:
        print(f"   S3 connector structure (for reference):")
        for line in s3_lib.split('\n')[:5]:
            if line.strip():
                print(f"      {line}")
        print(f"   ⚠️  Snowflake connector might need to be in lib/ subdirectory")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Diagnosis Complete")
    print(f"{'='*70}")
    print(f"\nPossible Issues:")
    print(f"1. Connector JAR might need to be in a 'lib/' subdirectory")
    print(f"2. Kafka Connect might need a restart after file placement")
    print(f"3. Plugin path might not include the directory")
    print(f"4. Connector might need dependencies")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




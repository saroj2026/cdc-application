"""Final verification of Snowflake connector plugin."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"
CONNECTOR_PATH = "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Final Verification of Snowflake Connector Plugin")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Verify file exists
    print("1. Verifying file location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {CONNECTOR_PATH} && ls -lh {CONNECTOR_PATH} || echo 'NOT_FOUND'"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if 'NOT_FOUND' in file_info:
        print(f"   ❌ File not found")
    else:
        print(f"   ✅ File exists:")
        print(f"   {file_info}")
    
    # 2. Check all plugins
    print(f"\n2. Checking all connector plugins...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_response = stdout.read().decode('utf-8')
    
    try:
        plugins = json.loads(plugins_response)
        print(f"   Found {len(plugins)} plugins")
        
        # Check for Snowflake
        snowflake_plugins = [p for p in plugins if 'snowflake' in p.get('class', '').lower()]
        if snowflake_plugins:
            print(f"\n   ✅ Snowflake connector FOUND!")
            for plugin in snowflake_plugins:
                print(f"      Class: {plugin.get('class')}")
                print(f"      Type: {plugin.get('type')}")
                print(f"      Version: {plugin.get('version')}")
        else:
            print(f"\n   ❌ Snowflake connector NOT found")
            print(f"   Available plugins:")
            for plugin in plugins:
                print(f"      - {plugin.get('class')} ({plugin.get('type')})")
    except json.JSONDecodeError:
        print(f"   ⚠️  Invalid JSON: {plugins_response[:200]}")
    
    # 3. Check Kafka Connect logs for Snowflake
    print(f"\n3. Checking Kafka Connect logs for Snowflake...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i snowflake | tail -10"
    )
    logs = stdout.read().decode('utf-8').strip()
    if logs:
        print(f"   Log entries:")
        for line in logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No Snowflake-related log entries")
    
    # 4. Check for class loading errors
    print(f"\n4. Checking for class loading errors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i -E '(classnotfound|noclassdef|exception|error.*snowflake)' | tail -10"
    )
    errors = stdout.read().decode('utf-8').strip()
    if errors:
        print(f"   Errors found:")
        for line in errors.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No class loading errors found")
    
    # 5. Check plugin path configuration
    print(f"\n5. Checking plugin path configuration...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} env | grep -i plugin"
    )
    plugin_env = stdout.read().decode('utf-8').strip()
    if plugin_env:
        print(f"   Plugin environment:")
        for line in plugin_env.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    # 6. Check if JAR is readable and valid
    print(f"\n6. Checking JAR file validity...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} file {CONNECTOR_PATH} 2>&1"
    )
    file_type = stdout.read().decode('utf-8').strip()
    print(f"   File type: {file_type}")
    
    # 7. Check if connector needs dependencies
    print(f"\n7. Note: Snowflake connector may need dependencies")
    print(f"   The connector JAR is large (108MB) and may include dependencies")
    print(f"   If it still doesn't load, check for missing dependencies")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Verification Complete")
    print(f"{'='*70}")
    print(f"\nSummary:")
    print(f"  - File location: {CONNECTOR_PATH}")
    print(f"  - Plugin path: /usr/share/java/plugins")
    print(f"  - Status: {'✅ Found' if snowflake_plugins else '❌ Not found'}")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




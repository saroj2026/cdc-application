"""Verify Snowflake connector after moving to lib/ subdirectory."""
import paramiko
import json
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Verifying Snowflake Connector After lib/ Move")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Wait a bit more for container to be ready
    print("1. Waiting for Kafka Connect to be ready...")
    for i in range(10):
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1 && echo 'READY' || echo 'NOT_READY'"
        )
        if 'READY' in stdout.read().decode('utf-8'):
            print(f"   ✅ Container is ready")
            break
        time.sleep(3)
        print(f"   ... waiting ({i+1}/10)", end='\r')
    else:
        print(f"   ⚠️  Container may still be starting")
    
    # Check file location
    print(f"\n2. Verifying file location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh /usr/share/java/plugins/snowflake-kafka-connector/lib/ 2>&1"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if file_info:
        print(f"   ✅ File in lib/ subdirectory:")
        for line in file_info.split('\n'):
            if line.strip() and '.jar' in line:
                print(f"      {line}")
    
    # Check plugins
    print(f"\n3. Checking connector plugins list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    try:
        plugins = json.loads(plugins_json)
        print(f"   Found {len(plugins)} plugins total")
        
        snowflake_found = False
        snowflake_plugin = None
        for plugin in plugins:
            plugin_class = plugin.get('class', '')
            if 'snowflake' in plugin_class.lower():
                snowflake_found = True
                snowflake_plugin = plugin
                break
        
        if snowflake_found:
            print(f"\n   ✅✅✅ SNOWFLAKE CONNECTOR FOUND! ✅✅✅")
            print(f"      Class: {snowflake_plugin.get('class')}")
            print(f"      Type: {snowflake_plugin.get('type')}")
            print(f"      Version: {snowflake_plugin.get('version')}")
        else:
            print(f"\n   ❌ Snowflake connector still not found")
            print(f"   Available plugins:")
            for plugin in plugins:
                print(f"      - {plugin.get('class')} ({plugin.get('type')})")
    except json.JSONDecodeError:
        print(f"   ⚠️  Could not parse JSON")
        print(f"   Response: {plugins_json[:300]}")
        snowflake_found = False
    
    # Check loading logs
    print(f"\n4. Checking plugin loading logs...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i 'snowflake' | tail -5"
    )
    logs = stdout.read().decode('utf-8').strip()
    if logs:
        print(f"   Recent Snowflake logs:")
        for line in logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅✅✅ SUCCESS! Snowflake Connector is Now Available! ✅✅✅")
    else:
        print("⚠️  Connector still not appearing")
        print("   File is in lib/ subdirectory")
        print("   May need to check for class loading errors")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




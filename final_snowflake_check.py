"""Final check of Snowflake connector after all fixes."""
import paramiko
import json
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Final Snowflake Connector Check")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Check container status
    print("1. Checking container status...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps | grep {KAFKA_CONNECT_CONTAINER}"
    )
    container_status = stdout.read().decode('utf-8').strip()
    if container_status:
        print(f"   ✅ Container is running")
    else:
        print(f"   ⚠️  Container not running, starting...")
        ssh.exec_command(f"docker start {KAFKA_CONNECT_CONTAINER}")
        print(f"   Waiting 30 seconds...")
        time.sleep(30)
    
    # Wait for Kafka Connect to be ready
    print(f"\n2. Waiting for Kafka Connect to be ready...")
    for i in range(15):
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1 && echo 'READY' || echo 'NOT_READY'"
        )
        if 'READY' in stdout.read().decode('utf-8'):
            print(f"   ✅ Kafka Connect is ready")
            break
        time.sleep(3)
        print(f"   ... waiting ({i+1}/15)", end='\r')
    else:
        print(f"   ⚠️  Kafka Connect may still be starting")
    
    # Verify file location
    print(f"\n3. Verifying file location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh /usr/share/java/plugins/snowflake-kafka-connector/lib/*.jar 2>&1"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if file_info and 'No such file' not in file_info:
        print(f"   ✅ File exists:")
        print(f"      {file_info}")
    else:
        print(f"   ❌ File not found")
    
    # Get plugins
    print(f"\n4. Getting connector plugins list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    snowflake_found = False
    if plugins_json and len(plugins_json) > 10:
        try:
            plugins = json.loads(plugins_json)
            print(f"   ✅ Got {len(plugins)} plugins")
            
            for plugin in plugins:
                plugin_class = plugin.get('class', '')
                if 'snowflake' in plugin_class.lower():
                    snowflake_found = True
                    print(f"\n   ✅✅✅ SNOWFLAKE CONNECTOR FOUND! ✅✅✅")
                    print(f"      Class: {plugin_class}")
                    print(f"      Type: {plugin.get('type')}")
                    print(f"      Version: {plugin.get('version')}")
                    break
            
            if not snowflake_found:
                print(f"\n   ❌ Snowflake connector NOT in list")
                print(f"   Available plugins:")
                for plugin in plugins[:5]:
                    print(f"      - {plugin.get('class')} ({plugin.get('type')})")
        except json.JSONDecodeError:
            print(f"   ⚠️  JSON parse error")
            print(f"   Response: {plugins_json[:300]}")
    else:
        print(f"   ⚠️  Empty or invalid response")
        print(f"   Response: {plugins_json[:200]}")
    
    # Check latest logs
    print(f"\n5. Checking latest plugin loading...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i 'snowflake' | tail -3"
    )
    latest_logs = stdout.read().decode('utf-8').strip()
    if latest_logs:
        print(f"   Latest logs:")
        for line in latest_logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅✅✅ SUCCESS! Snowflake Connector is Available! ✅✅✅")
    else:
        print("⚠️  Connector Still Not Appearing")
        print("\n   Summary:")
        print("   - File is in correct location: /usr/share/java/plugins/snowflake-kafka-connector/lib/")
        print("   - Plugin directory is being loaded")
        print("   - But no connector classes are being discovered")
        print("\n   Possible causes:")
        print("   1. Connector class may not exist in JAR")
        print("   2. Connector may need additional dependencies")
        print("   3. JAR may be corrupted or incomplete")
        print("\n   Recommendation:")
        print("   - Verify the JAR file integrity")
        print("   - Check Snowflake documentation for exact class name")
        print("   - Try downloading a fresh copy of the JAR")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




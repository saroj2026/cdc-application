"""Check why Snowflake connector loads but doesn't appear in plugin list."""
import paramiko

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Checking Snowflake Connector Loading")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check logs around the time Snowflake was loaded
    print("1. Checking logs when Snowflake connector was loaded...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 20 'Loading plugin from.*snowflake' | tail -30"
    )
    loading_logs = stdout.read().decode('utf-8').strip()
    if loading_logs:
        print(f"   Logs around Snowflake loading:")
        for line in loading_logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No specific loading logs found")
    
    # 2. Check for errors after loading
    print(f"\n2. Checking for errors after Snowflake loading...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i -E '(snowflake.*error|snowflake.*exception|snowflake.*fail|classnotfound.*snowflake)' | tail -10"
    )
    errors = stdout.read().decode('utf-8').strip()
    if errors:
        print(f"   Errors found:")
        for line in errors.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No errors found")
    
    # 3. Check if we can extract the connector class from JAR
    print(f"\n3. Checking connector class in JAR...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} unzip -l /usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar 2>&1 | grep -i 'SnowflakeSinkConnector.class' | head -1"
    )
    class_check = stdout.read().decode('utf-8').strip()
    if class_check:
        print(f"   ✅ Connector class found in JAR")
        print(f"      {class_check}")
    else:
        print(f"   ⚠️  Could not verify class in JAR")
    
    # 4. Try to restart and see if it appears
    print(f"\n4. Restarting Kafka Connect to reload plugins...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Container restarting...")
    
    import time
    print(f"   Waiting 40 seconds for full restart...")
    time.sleep(40)
    
    # 5. Check plugins again
    print(f"\n5. Checking plugin list after restart...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    import json
    try:
        plugins = json.loads(plugins_json)
        print(f"   Found {len(plugins)} plugins")
        
        snowflake_found = False
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
            print(f"\n   ❌ Still not found")
            print(f"   Available plugins:")
            for plugin in plugins:
                print(f"      - {plugin.get('class')} ({plugin.get('type')})")
    except:
        print(f"   ⚠️  Could not parse: {plugins_json[:200]}")
    
    # 6. Check latest loading logs
    print(f"\n6. Checking latest plugin loading logs...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i 'loading plugin' | tail -5"
    )
    latest_logs = stdout.read().decode('utf-8').strip()
    if latest_logs:
        print(f"   Latest loading:")
        for line in latest_logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅ SUCCESS! Snowflake connector is now available!")
    else:
        print("⚠️  Connector still not appearing")
        print("   The connector may need dependencies or have a class loading issue")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




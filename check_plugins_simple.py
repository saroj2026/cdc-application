"""Simple check of connector plugins."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Checking Connector Plugins")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    
    # Check plugins
    print("\n1. Getting connector plugins list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    try:
        plugins = json.loads(plugins_json)
        print(f"   ✅ Found {len(plugins)} plugins\n")
        
        # Check for Snowflake
        snowflake_found = False
        for plugin in plugins:
            plugin_class = plugin.get('class', '')
            if 'snowflake' in plugin_class.lower():
                snowflake_found = True
                print(f"   ✅ SNOWFLAKE CONNECTOR FOUND!")
                print(f"      Class: {plugin_class}")
                print(f"      Type: {plugin.get('type')}")
                print(f"      Version: {plugin.get('version')}")
                break
        
        if not snowflake_found:
            print(f"   ❌ Snowflake connector NOT found")
            print(f"\n   Available plugins:")
            for plugin in plugins:
                print(f"      - {plugin.get('class')} ({plugin.get('type')})")
        
        # Check file
        print(f"\n2. Checking file location...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh /usr/share/java/plugins/snowflake-kafka-connector/ 2>&1"
        )
        file_list = stdout.read().decode('utf-8')
        if file_list:
            print(f"   {file_list}")
        else:
            print(f"   ⚠️  Directory not found or empty")
        
    except json.JSONDecodeError:
        print(f"   ❌ Invalid JSON response")
        print(f"   Response: {plugins_json[:200]}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅ SUCCESS: Snowflake connector is available!")
    else:
        print("⚠️  Snowflake connector not in plugin list")
        print("   Check file location and restart Kafka Connect")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




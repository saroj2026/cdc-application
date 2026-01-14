"""Try putting Snowflake connector in root of plugin directory."""
import paramiko
import json
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

SOURCE = "/usr/share/java/plugins/snowflake-kafka-connector/lib/snowflake-kafka-connector-3.2.2.jar"
TARGET = "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"

print("=" * 70)
print("Trying Root Location (Not lib/ subdirectory)")
print("=" * 70)
print("Other connectors (S3, JDBC) are in root, not lib/")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Check if source exists
    print("1. Checking source file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {SOURCE} && ls -lh {SOURCE} || echo 'NOT_FOUND'"
    )
    source_info = stdout.read().decode('utf-8').strip()
    if 'NOT_FOUND' in source_info:
        print(f"   ❌ Source file not found")
        ssh.close()
        exit(1)
    else:
        print(f"   ✅ Source file exists")
        print(f"      {source_info}")
    
    # Copy to root
    print(f"\n2. Copying to root of plugin directory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} cp {SOURCE} {TARGET}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Copied to root location")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ❌ Copy failed: {error}")
        ssh.close()
        exit(1)
    
    # Verify both locations
    print(f"\n3. Verifying both locations...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {TARGET} {SOURCE} 2>&1"
    )
    both_files = stdout.read().decode('utf-8').strip()
    if both_files:
        print(f"   Files:")
        for line in both_files.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    # Restart
    print(f"\n4. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Restarting...")
    
    print(f"\n5. Waiting 40 seconds...")
    time.sleep(40)
    
    # Check plugins
    print(f"\n6. Checking connector plugins...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    snowflake_found = False
    if plugins_json and len(plugins_json) > 10:
        try:
            plugins = json.loads(plugins_json)
            print(f"   Found {len(plugins)} plugins")
            
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
        except json.JSONDecodeError:
            print(f"   ⚠️  JSON parse error")
    
    # Check logs
    print(f"\n7. Checking loading logs...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 5 'Loading plugin from.*snowflake' | tail -10"
    )
    logs = stdout.read().decode('utf-8').strip()
    if logs:
        print(f"   Recent logs:")
        for line in logs.split('\n'):
            if 'Added plugin' in line and 'snowflake' in line.lower():
                print(f"      ✅ {line}")
            elif line.strip():
                print(f"      {line}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅✅✅ SUCCESS! Snowflake Connector is Now Available! ✅✅✅")
    else:
        print("⚠️  Connector Still Not Appearing")
        print("\n   The connector JAR is being loaded but no connector classes")
        print("   are being discovered. This is unusual and may indicate:")
        print("   1. The JAR doesn't contain the expected connector class")
        print("   2. The connector requires additional setup or dependencies")
        print("   3. There's a compatibility issue with this Kafka Connect version")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




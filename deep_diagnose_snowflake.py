"""Deep diagnosis of Snowflake connector issue."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Deep Diagnosis of Snowflake Connector")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check endpoint directly
    print("1. Testing connector-plugins endpoint...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -v http://localhost:8083/connector-plugins 2>&1 | head -30"
    )
    curl_output = stdout.read().decode('utf-8')
    print(f"   Curl output:")
    for line in curl_output.split('\n')[:25]:
        if line.strip():
            print(f"      {line}")
    
    # 2. Get plugins with better error handling
    print(f"\n2. Getting plugins list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins"
    )
    plugins_raw = stdout.read().decode('utf-8')
    
    if plugins_raw:
        print(f"   Response length: {len(plugins_raw)} characters")
        print(f"   First 200 chars: {plugins_raw[:200]}")
        
        try:
            plugins = json.loads(plugins_raw)
            print(f"   ✅ Valid JSON, found {len(plugins)} plugins")
            
            snowflake_found = False
            for plugin in plugins:
                plugin_class = plugin.get('class', '')
                if 'snowflake' in plugin_class.lower():
                    snowflake_found = True
                    print(f"\n   ✅✅✅ SNOWFLAKE FOUND!")
                    print(f"      {json.dumps(plugin, indent=6)}")
                    break
            
            if not snowflake_found:
                print(f"\n   ❌ Snowflake not in list")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
    else:
        print(f"   ❌ No response from endpoint")
    
    # 3. Check for class loading errors in detail
    print(f"\n3. Checking for class loading errors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 10 -B 5 'snowflake-kafka-connector' | grep -i -E '(error|exception|fail|warn|classnotfound|noclassdef)' | tail -20"
    )
    errors = stdout.read().decode('utf-8').strip()
    if errors:
        print(f"   Errors/warnings found:")
        for line in errors.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No errors found in logs")
    
    # 4. Check what happens when plugin is loaded
    print(f"\n4. Checking plugin loading sequence...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 30 'Loading plugin from.*snowflake' | tail -40"
    )
    loading_sequence = stdout.read().decode('utf-8').strip()
    if loading_sequence:
        print(f"   Loading sequence:")
        for line in loading_sequence.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    # 5. Compare with working connector (S3)
    print(f"\n5. Comparing with S3 connector (working)...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 10 'Loading plugin from.*s3' | grep -i 'added plugin' | head -2"
    )
    s3_added = stdout.read().decode('utf-8').strip()
    if s3_added:
        print(f"   S3 connector (working):")
        for line in s3_added.split('\n'):
            if line.strip():
                print(f"      {line}")
    
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -A 10 'Loading plugin from.*snowflake' | grep -i 'added plugin'"
    )
    snowflake_added = stdout.read().decode('utf-8').strip()
    if snowflake_added:
        print(f"   Snowflake connector:")
        for line in snowflake_added.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ❌ No 'Added plugin' message for Snowflake")
    
    # 6. Check JAR file structure
    print(f"\n6. Checking JAR file...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh /usr/share/java/plugins/snowflake-kafka-connector/lib/*.jar"
    )
    jar_info = stdout.read().decode('utf-8').strip()
    if jar_info:
        print(f"   JAR file:")
        print(f"      {jar_info}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Diagnosis Complete")
    print(f"{'='*70}")
    if snowflake_found:
        print("✅ Snowflake connector is available!")
    else:
        print("⚠️  Connector still not appearing")
        print("   The JAR is being loaded but no connector classes are being discovered")
        print("   This may indicate:")
        print("   - Connector class not in expected location")
        print("   - Missing dependencies")
        print("   - JAR structure issue")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




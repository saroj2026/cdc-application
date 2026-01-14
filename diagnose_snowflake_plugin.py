"""Diagnose why Snowflake connector isn't showing in plugin list."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Diagnosing Snowflake Connector Plugin Issue")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check how other connectors are structured
    print("1. Checking structure of other connectors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/java/plugins/ 2>&1 | head -20"
    )
    plugins_dir = stdout.read().decode('utf-8')
    print(f"   Plugins directory structure:")
    for line in plugins_dir.split('\n')[:15]:
        if line.strip():
            print(f"      {line}")
    
    # 2. Check if connectors need lib/ subdirectory
    print(f"\n2. Checking if connectors use lib/ subdirectory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -d /usr/share/java/plugins/*/lib/ 2>&1 | head -5"
    )
    lib_dirs = stdout.read().decode('utf-8').strip()
    if lib_dirs:
        print(f"   Found lib/ subdirectories:")
        for line in lib_dirs.split('\n'):
            if line.strip():
                print(f"      {line}")
                # Check what's in one of them
                stdin2, stdout2, stderr2 = ssh.exec_command(
                    f"docker exec {KAFKA_CONNECT_CONTAINER} ls {line}*.jar 2>&1 | head -3"
                )
                jars = stdout2.read().decode('utf-8').strip()
                if jars:
                    print(f"         JARs: {jars.split()[0] if jars.split() else 'none'}")
    else:
        print(f"   No lib/ subdirectories found")
    
    # 3. Check current Snowflake structure
    print(f"\n3. Current Snowflake connector structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/java/plugins/snowflake-kafka-connector/ 2>&1"
    )
    snowflake_structure = stdout.read().decode('utf-8')
    print(f"   {snowflake_structure}")
    
    # 4. Check if we need to move to lib/ subdirectory
    print(f"\n4. Checking if JAR should be in lib/ subdirectory...")
    # Check one working connector structure
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -d /usr/share/java/plugins/*/ 2>&1 | grep -v snowflake | head -1"
    )
    example_connector = stdout.read().decode('utf-8').strip()
    if example_connector:
        print(f"   Example connector: {example_connector}")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la {example_connector} 2>&1"
        )
        example_structure = stdout.read().decode('utf-8')
        print(f"   Structure:")
        for line in example_structure.split('\n')[:10]:
            if line.strip():
                print(f"      {line}")
    
    # 5. Get all plugins to see what's available
    print(f"\n5. Getting current plugin list...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    try:
        plugins = json.loads(plugins_json)
        print(f"   Found {len(plugins)} plugins")
        
        # Check for Snowflake
        snowflake_found = False
        for plugin in plugins:
            if 'snowflake' in plugin.get('class', '').lower():
                snowflake_found = True
                print(f"   ✅ SNOWFLAKE FOUND: {plugin.get('class')}")
                break
        
        if not snowflake_found:
            print(f"   ❌ Snowflake NOT in list")
    except:
        print(f"   ⚠️  Could not parse JSON")
    
    # 6. Check recent logs for plugin loading
    print(f"\n6. Checking recent plugin loading logs...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i 'loading plugin' | tail -10"
    )
    loading_logs = stdout.read().decode('utf-8').strip()
    if loading_logs:
        print(f"   Recent plugin loading:")
        for line in loading_logs.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No recent loading logs")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Diagnosis Complete")
    print(f"{'='*70}")
    print(f"\nRecommendation:")
    print(f"Based on the structure, the connector might need to be in a lib/ subdirectory")
    print(f"or the connector directory structure might need to match other connectors.")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




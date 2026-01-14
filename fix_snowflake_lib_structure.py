"""Fix Snowflake connector structure - move to lib/ subdirectory."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Fixing Snowflake Connector Structure")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check current file location
    print("1. Checking current file location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/java/plugins/snowflake-kafka-connector/ 2>&1"
    )
    current_files = stdout.read().decode('utf-8').strip()
    print(f"   Current directory contents:")
    for line in current_files.split('\n'):
        if line.strip():
            print(f"      {line}")
    
    # Find the JAR file
    jar_file = None
    for line in current_files.split('\n'):
        if '.jar' in line and 'snowflake' in line.lower():
            parts = line.split()
            if len(parts) > 8:
                jar_file = parts[-1]
                break
    
    if not jar_file:
        # Try listing with ls
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls /usr/share/java/plugins/snowflake-kafka-connector/ 2>&1"
        )
        files = stdout.read().decode('utf-8').strip()
        for line in files.split('\n'):
            if '.jar' in line:
                jar_file = line.strip()
                break
    
    if jar_file:
        print(f"\n   Found JAR: {jar_file}")
    else:
        print(f"\n   ⚠️  Could not find JAR file name")
        # Use the known filename
        jar_file = "snowflake-kafka-connector-3.2.2.jar"
        print(f"   Using default: {jar_file}")
    
    source_path = f"/usr/share/java/plugins/snowflake-kafka-connector/{jar_file}"
    lib_dir = "/usr/share/java/plugins/snowflake-kafka-connector/lib"
    target_path = f"{lib_dir}/{jar_file}"
    
    # 2. Create lib directory
    print(f"\n2. Creating lib/ subdirectory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {lib_dir}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Directory created: {lib_dir}")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    # 3. Move file to lib/
    print(f"\n3. Moving JAR to lib/ subdirectory...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mv {source_path} {target_path}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ File moved successfully")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ❌ Move failed: {error}")
        # Try with full path
        print(f"   Trying with full path...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} sh -c 'mv /usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar {target_path}'"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"   ✅ File moved with sh -c")
        else:
            error = stderr.read().decode('utf-8')
            print(f"   ❌ Still failed: {error}")
            ssh.close()
            exit(1)
    
    # 4. Verify file in new location
    print(f"\n4. Verifying file in new location...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {target_path} 2>&1"
    )
    verify = stdout.read().decode('utf-8').strip()
    if verify and 'No such file' not in verify:
        print(f"   ✅ File verified:")
        print(f"   {verify}")
    else:
        print(f"   ❌ File not found in new location")
        ssh.close()
        exit(1)
    
    # 5. Check directory structure
    print(f"\n5. Checking final directory structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/java/plugins/snowflake-kafka-connector/ 2>&1"
    )
    final_structure = stdout.read().decode('utf-8').strip()
    print(f"   Final structure:")
    for line in final_structure.split('\n'):
        if line.strip():
            print(f"      {line}")
    
    # 6. Restart Kafka Connect
    print(f"\n6. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"   ✅ Container restarting...")
    else:
        error = stderr.read().decode('utf-8')
        print(f"   ⚠️  Warning: {error}")
    
    print(f"\n7. Waiting 40 seconds for restart...")
    time.sleep(40)
    
    # 7. Check plugins
    print(f"\n8. Checking connector plugins...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    import json
    try:
        plugins = json.loads(plugins_json)
        snowflake_found = False
        for plugin in plugins:
            if 'snowflake' in plugin.get('class', '').lower():
                snowflake_found = True
                print(f"\n   ✅✅✅ SNOWFLAKE CONNECTOR FOUND! ✅✅✅")
                print(f"      Class: {plugin.get('class')}")
                print(f"      Type: {plugin.get('type')}")
                print(f"      Version: {plugin.get('version')}")
                break
        
        if not snowflake_found:
            print(f"\n   ❌ Still not found")
            print(f"   Found {len(plugins)} plugins total")
    except:
        print(f"   ⚠️  Could not parse JSON: {plugins_json[:200]}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅ SUCCESS! Snowflake connector is now available!")
    else:
        print("⚠️  Connector still not appearing")
        print("   File moved to lib/ subdirectory")
        print("   May need to check logs for class loading issues")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




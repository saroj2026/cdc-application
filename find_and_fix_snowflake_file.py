"""Find Snowflake file and fix structure."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Finding and Fixing Snowflake Connector File")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Find the file
    print("1. Searching for Snowflake connector JAR...")
    search_paths = [
        "/usr/share/java/plugins/snowflake-kafka-connector/",
        "/usr/share/java/plugins/snowflake-kafka-connector/lib/",
        "/usr/share/confluent-hub-components/snowflake-kafka-connector/",
    ]
    
    jar_path = None
    for path in search_paths:
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls {path}*.jar 2>&1"
        )
        files = stdout.read().decode('utf-8').strip()
        if files and 'No such file' not in files and '.jar' in files:
            jar_path = files.split('\n')[0].strip()
            print(f"   ✅ Found: {jar_path}")
            break
    
    if not jar_path:
        print(f"   ❌ JAR file not found in any expected location")
        print(f"   Need to re-download and install")
        ssh.close()
        exit(1)
    
    # Determine target location
    target_dir = "/usr/share/java/plugins/snowflake-kafka-connector/lib"
    target_path = f"{target_dir}/snowflake-kafka-connector-3.2.2.jar"
    
    # If file is already in target, verify it
    if jar_path == target_path or target_path in jar_path:
        print(f"\n2. File is already in correct location")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {target_path}"
        )
        file_info = stdout.read().decode('utf-8').strip()
        if file_info:
            print(f"   ✅ {file_info}")
    else:
        # Move to correct location
        print(f"\n2. Moving file to correct location...")
        print(f"   From: {jar_path}")
        print(f"   To: {target_path}")
        
        # Create directory
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} mkdir -p {target_dir}"
        )
        
        # Move file
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec -u root {KAFKA_CONNECT_CONTAINER} cp {jar_path} {target_path}"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print(f"   ✅ File copied to target location")
        else:
            error = stderr.read().decode('utf-8')
            print(f"   ❌ Copy failed: {error}")
            ssh.close()
            exit(1)
    
    # Verify final structure
    print(f"\n3. Verifying final structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/java/plugins/snowflake-kafka-connector/"
    )
    structure = stdout.read().decode('utf-8').strip()
    print(f"   Directory structure:")
    for line in structure.split('\n'):
        if line.strip():
            print(f"      {line}")
    
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {target_path}"
    )
    final_file = stdout.read().decode('utf-8').strip()
    if final_file:
        print(f"\n   ✅ Final file:")
        print(f"      {final_file}")
    
    # Restart
    print(f"\n4. Restarting Kafka Connect...")
    stdin, stdout, stderr = ssh.exec_command(f"docker restart {KAFKA_CONNECT_CONTAINER}")
    print(f"   ✅ Restarting...")
    
    print(f"\n5. Waiting 40 seconds for restart...")
    time.sleep(40)
    
    # Final check
    print(f"\n6. Final plugin check...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
    )
    plugins_json = stdout.read().decode('utf-8')
    
    import json
    snowflake_found = False
    if plugins_json and len(plugins_json) > 10:
        try:
            plugins = json.loads(plugins_json)
            for plugin in plugins:
                if 'snowflake' in plugin.get('class', '').lower():
                    snowflake_found = True
                    print(f"   ✅✅✅ SNOWFLAKE FOUND: {plugin.get('class')}")
                    break
        except:
            pass
    
    if not snowflake_found:
        print(f"   ❌ Still not found")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if snowflake_found:
        print("✅ SUCCESS!")
    else:
        print("⚠️  Connector still not appearing")
        print("   The JAR is in the correct location but classes aren't being discovered")
    print(f"{'='*70}\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




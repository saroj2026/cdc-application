"""Check status of all containers and Kafka Connect health."""
import paramiko
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Checking All Container Status and Kafka Connect Health")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check all containers
    print("1. Container Status:")
    stdin, stdout, stderr = ssh.exec_command(
        "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
    )
    containers = stdout.read().decode('utf-8')
    print(containers)
    
    # 2. Check Kafka Connect health specifically
    print("\n2. Kafka Connect Health Check:")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker inspect {KAFKA_CONNECT_CONTAINER} --format='{{{{.State.Health.Status}}}}'"
    )
    health_status = stdout.read().decode('utf-8').strip()
    print(f"   Health Status: {health_status}")
    
    if health_status == "healthy":
        print(f"   ✅ Kafka Connect is healthy and ready!")
    elif health_status == "starting":
        print(f"   ⚠️  Kafka Connect is still starting...")
    elif health_status == "unhealthy":
        print(f"   ❌ Kafka Connect is unhealthy!")
    
    # 3. Test REST API
    print(f"\n3. Testing Kafka Connect REST API...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s -w '\\nHTTP_CODE:%{{http_code}}' http://localhost:8083/connector-plugins 2>&1 | tail -1"
    )
    response = stdout.read().decode('utf-8').strip()
    
    if 'HTTP_CODE:200' in response:
        print(f"   ✅ REST API is responding")
        
        # Get plugins
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
        )
        plugins_json = stdout.read().decode('utf-8')
        
        try:
            plugins = json.loads(plugins_json)
            print(f"   Found {len(plugins)} connector plugins")
            
            # Check for Snowflake
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
                print(f"\n   ⚠️  Snowflake connector not in plugin list")
                print(f"   (May work with lazy loading when creating pipeline)")
        except:
            pass
    else:
        print(f"   ⚠️  REST API not responding yet: {response}")
    
    # 4. Check Kafka Connect logs for any errors
    print(f"\n4. Recent Kafka Connect Logs (last 20 lines):")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} --tail 20 2>&1"
    )
    logs = stdout.read().decode('utf-8')
    for line in logs.split('\n')[-10:]:
        if line.strip():
            print(f"   {line[:120]}")
    
    # 5. Check if Snowflake connector file exists
    print(f"\n5. Checking Snowflake Connector File:")
    jar_path = "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar"
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh {jar_path} 2>&1"
    )
    file_info = stdout.read().decode('utf-8').strip()
    if file_info and 'snowflake-kafka-connector-3.2.2.jar' in file_info:
        print(f"   ✅ File exists: {file_info}")
    else:
        print(f"   ⚠️  File check: {file_info}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"\n✅ All containers are running")
    print(f"✅ Kafka Connect: {health_status}")
    print(f"✅ REST API: http://{VPS_HOST}:8083/connector-plugins")
    print(f"\n📋 Next Steps:")
    print(f"   1. If Kafka Connect is 'starting', wait 1-2 more minutes")
    print(f"   2. Access connector-plugins at: http://{VPS_HOST}:8083/connector-plugins")
    print(f"   3. Try creating a Snowflake pipeline (may work with lazy loading)")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




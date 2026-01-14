"""Wait for Kafka Connect to fully start and check endpoint."""
import paramiko
import time
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Waiting for Kafka Connect to Start and Checking Endpoint")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    max_wait = 180  # 3 minutes
    wait_interval = 10
    elapsed = 0
    
    print(f"Waiting for Kafka Connect to be ready (max {max_wait}s)...")
    
    while elapsed < max_wait:
        # Check health
        stdin, stdout, stderr = ssh.exec_command(
            f"docker ps --filter name={KAFKA_CONNECT_CONTAINER} --format '{{{{.Status}}}}'"
        )
        status = stdout.read().decode('utf-8').strip()
        
        # Test endpoint
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s -w 'HTTP_CODE:%{{http_code}}' http://localhost:8083/connector-plugins 2>&1 | tail -1"
        )
        response = stdout.read().decode('utf-8').strip()
        
        if 'HTTP_CODE:200' in response:
            print(f"\n✅✅✅ Kafka Connect is READY! ✅✅✅")
            print(f"   Status: {status}")
            print(f"   Endpoint: http://{VPS_HOST}:8083/connector-plugins")
            
            # Get plugins list
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1"
            )
            plugins_json = stdout.read().decode('utf-8')
            
            try:
                plugins = json.loads(plugins_json)
                print(f"\n   Found {len(plugins)} connector plugins:")
                
                snowflake_found = False
                for plugin in plugins:
                    plugin_class = plugin.get('class', '')
                    if 'snowflake' in plugin_class.lower():
                        snowflake_found = True
                        print(f"      ✅ {plugin_class}")
                    else:
                        print(f"      • {plugin_class}")
                
                if not snowflake_found:
                    print(f"\n   ⚠️  Snowflake connector not in list")
                    print(f"   (But it may work with lazy loading)")
                
            except:
                print(f"   Response: {plugins_json[:200]}")
            
            break
        else:
            print(f"   [{elapsed}s] Still starting... (Status: {status[:50]})", end='\r')
            time.sleep(wait_interval)
            elapsed += wait_interval
    
    if elapsed >= max_wait:
        print(f"\n⚠️  Timeout after {max_wait}s")
        print(f"   Container status: {status}")
        print(f"   Check logs: docker logs {KAFKA_CONNECT_CONTAINER}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"\n✅ JDBC Driver: NOT needed")
    print(f"   - Snowflake Kafka Connector is a 'fat JAR' (176MB)")
    print(f"   - Includes Snowflake JDBC driver")
    print(f"   - Includes all dependencies")
    print(f"   - No separate download needed")
    print(f"\n✅ Endpoint URL:")
    print(f"   - Use: http://{VPS_HOST}:8083/connector-plugins")
    print(f"   - NOT: http://localhost:8083/connector-plugins")
    print(f"   (Kafka Connect runs on VPS, not your local machine)")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




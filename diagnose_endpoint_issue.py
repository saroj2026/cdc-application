"""Diagnose why Kafka Connect endpoint is not responding."""
import paramiko
import time

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Diagnosing Kafka Connect Endpoint Issue")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # 1. Check container health
    print("1. Checking container health status...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps --filter name={KAFKA_CONNECT_CONTAINER} --format '{{{{.Status}}}}'"
    )
    status = stdout.read().decode('utf-8').strip()
    print(f"   Status: {status}")
    
    if 'health: starting' in status:
        print(f"   ⚠️  Container is still starting (health: starting)")
        print(f"   Wait a few minutes for it to fully start")
    elif 'health: healthy' in status:
        print(f"   ✅ Container is healthy")
    elif 'health: unhealthy' in status:
        print(f"   ❌ Container is unhealthy")
    
    # 2. Check if Kafka Connect is listening
    print(f"\n2. Checking if Kafka Connect is listening on port 8083...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} netstat -tlnp 2>/dev/null | grep 8083 || docker exec {KAFKA_CONNECT_CONTAINER} ss -tlnp 2>/dev/null | grep 8083 || echo 'netstat/ss not available'"
    )
    listening = stdout.read().decode('utf-8').strip()
    if '8083' in listening:
        print(f"   ✅ Kafka Connect is listening on port 8083")
        print(f"   {listening}")
    else:
        print(f"   ⚠️  Cannot verify if listening (netstat/ss not available)")
    
    # 3. Check recent logs for errors
    print(f"\n3. Checking recent logs for errors...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} --tail 50 2>&1 | grep -i -E '(error|exception|failed|fatal)' | tail -10"
    )
    errors = stdout.read().decode('utf-8').strip()
    if errors:
        print(f"   ⚠️  Found errors in logs:")
        for line in errors.split('\n'):
            if line.strip():
                print(f"      {line[:150]}")
    else:
        print(f"   ✅ No recent errors found")
    
    # 4. Check if Kafka Connect REST API is ready
    print(f"\n4. Testing REST API endpoint...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s -w '\\nHTTP_CODE:%{{http_code}}' http://localhost:8083/ 2>&1 | tail -5"
    )
    api_test = stdout.read().decode('utf-8').strip()
    if 'HTTP_CODE:200' in api_test or 'HTTP_CODE:404' in api_test:
        print(f"   ✅ REST API is responding")
        print(f"   {api_test[:200]}")
    elif 'Connection refused' in api_test or 'Failed to connect' in api_test:
        print(f"   ❌ REST API is NOT responding")
        print(f"   Kafka Connect may still be starting")
    else:
        print(f"   Response: {api_test[:200]}")
    
    # 5. Check connector-plugins endpoint specifically
    print(f"\n5. Testing connector-plugins endpoint...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s -w '\\nHTTP_CODE:%{{http_code}}' http://localhost:8083/connector-plugins 2>&1 | tail -10"
    )
    plugins_test = stdout.read().decode('utf-8').strip()
    if 'HTTP_CODE:200' in plugins_test:
        print(f"   ✅ Endpoint is working!")
        # Count plugins
        if '[' in plugins_test:
            import json
            try:
                json_part = plugins_test.split('HTTP_CODE')[0].strip()
                plugins = json.loads(json_part)
                print(f"   Found {len(plugins)} plugins")
                snowflake_found = any('snowflake' in str(p).lower() for p in plugins)
                if snowflake_found:
                    print(f"   ✅ Snowflake connector found!")
                else:
                    print(f"   ⚠️  Snowflake connector not in list")
            except:
                pass
    elif 'HTTP_CODE:404' in plugins_test:
        print(f"   ⚠️  Endpoint returned 404 (not found)")
    elif 'Connection refused' in plugins_test:
        print(f"   ❌ Connection refused - Kafka Connect not ready")
    else:
        print(f"   Response: {plugins_test[:300]}")
    
    # 6. Check startup logs
    print(f"\n6. Checking startup progress...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker logs {KAFKA_CONNECT_CONTAINER} 2>&1 | grep -i -E '(started|ready|listening|server started)' | tail -5"
    )
    startup = stdout.read().decode('utf-8').strip()
    if startup:
        print(f"   Startup messages:")
        for line in startup.split('\n'):
            if line.strip():
                print(f"      {line[:150]}")
    else:
        print(f"   ⚠️  No startup messages found")
    
    # 7. Wait and retry if needed
    if 'health: starting' in status:
        print(f"\n7. Container is still starting. Waiting 30 seconds and retrying...")
        time.sleep(30)
        
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1 | head -3"
        )
        retry_test = stdout.read().decode('utf-8').strip()
        if retry_test and '[' in retry_test:
            print(f"   ✅ Endpoint is now working after wait!")
        else:
            print(f"   ⚠️  Still not ready: {retry_test[:100]}")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Diagnosis Complete")
    print(f"{'='*70}")
    print(f"\n📋 Answers:")
    print(f"\n1. JDBC Driver Needed?")
    print(f"   ❌ NO - Snowflake Kafka Connector is a 'fat JAR'")
    print(f"   ✅ Includes Snowflake JDBC driver")
    print(f"   ✅ Includes all dependencies")
    print(f"   ✅ No separate download needed")
    print(f"\n2. Why is http://localhost:8083 not reachable?")
    print(f"   ❌ Kafka Connect is on VPS (72.61.233.209), not localhost")
    print(f"   ✅ Use: http://72.61.233.209:8083/connector-plugins")
    print(f"   ⚠️  If still not reachable:")
    print(f"      - Container may still be starting (wait 2-3 minutes)")
    print(f"      - Check firewall rules on VPS")
    print(f"      - Verify port 8083 is exposed in docker run command")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




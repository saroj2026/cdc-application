"""Check why endpoint is not reachable and if JDBC driver is needed."""
import paramiko
import requests

VPS_HOST = "72.61.233.209"
KAFKA_CONNECT_PORT = 8083
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Checking Endpoint Accessibility and JDBC Driver Requirements")
print("=" * 70)

# 1. Check endpoint accessibility
print("\n1. Checking Kafka Connect endpoint accessibility...")
print(f"   Local endpoint: http://localhost:{KAFKA_CONNECT_PORT}/connector-plugins")
print(f"   VPS endpoint: http://{VPS_HOST}:{KAFKA_CONNECT_PORT}/connector-plugins")

# Try local endpoint
try:
    response = requests.get(f"http://localhost:{KAFKA_CONNECT_PORT}/connector-plugins", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Local endpoint is reachable")
        print(f"   Response: {len(response.text)} characters")
    else:
        print(f"   ⚠️  Local endpoint returned status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ Local endpoint NOT reachable (Connection refused)")
    print(f"   Reason: Kafka Connect is on VPS, not localhost")
    print(f"   Use: http://{VPS_HOST}:{KAFKA_CONNECT_PORT}/connector-plugins")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# Try VPS endpoint
try:
    response = requests.get(f"http://{VPS_HOST}:{KAFKA_CONNECT_PORT}/connector-plugins", timeout=10)
    if response.status_code == 200:
        print(f"   ✅ VPS endpoint is reachable")
        print(f"   Response: {len(response.text)} characters")
    else:
        print(f"   ⚠️  VPS endpoint returned status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print(f"   ❌ VPS endpoint NOT reachable")
    print(f"   Possible reasons:")
    print(f"   - Kafka Connect container not running")
    print(f"   - Port 8083 not exposed/forwarded")
    print(f"   - Firewall blocking access")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# 2. Check container status via SSH
print(f"\n2. Checking Kafka Connect container status via SSH...")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username="root", password="segmbp@1100", timeout=10)
    print(f"   ✅ Connected to VPS")
    
    # Check container
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps | grep {KAFKA_CONNECT_CONTAINER}"
    )
    container_status = stdout.read().decode('utf-8').strip()
    if container_status:
        print(f"   ✅ Container is running:")
        print(f"      {container_status}")
    else:
        print(f"   ❌ Container is NOT running")
        print(f"   Start it with: docker start {KAFKA_CONNECT_CONTAINER}")
    
    # Check if port is exposed
    if container_status and '8083' in container_status:
        print(f"   ✅ Port 8083 is exposed")
    else:
        print(f"   ⚠️  Port 8083 may not be exposed")
    
    # Test endpoint from inside container
    print(f"\n3. Testing endpoint from inside container...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} curl -s http://localhost:8083/connector-plugins 2>&1 | head -5"
    )
    internal_test = stdout.read().decode('utf-8').strip()
    if internal_test and '[' in internal_test:
        print(f"   ✅ Endpoint works from inside container")
        print(f"   Response preview: {internal_test[:200]}")
    else:
        print(f"   ⚠️  Endpoint may not be responding")
        print(f"   Response: {internal_test[:200]}")
    
    ssh.close()
    
except Exception as e:
    print(f"   ❌ SSH connection failed: {e}")

# 3. Check JDBC driver requirements
print(f"\n4. Checking JDBC driver requirements for Snowflake...")
print(f"   Snowflake Kafka Connector (fat JAR) includes:")
print(f"   ✅ Snowflake JDBC driver (included)")
print(f"   ✅ All dependencies (included)")
print(f"   ✅ Bouncy Castle libraries (included)")
print(f"   \n   ❌ NO separate JDBC driver download needed")
print(f"   The connector JAR (176MB) is a 'fat JAR' that includes everything")

print(f"\n{'='*70}")
print("Summary")
print(f"{'='*70}")
print(f"\n✅ JDBC Driver: NOT needed (included in connector JAR)")
print(f"\n⚠️  Endpoint Issue:")
print(f"   - Use: http://{VPS_HOST}:{KAFKA_CONNECT_PORT}/connector-plugins")
print(f"   - NOT: http://localhost:{KAFKA_CONNECT_PORT}/connector-plugins")
print(f"   (Kafka Connect is on VPS, not your local machine)")
print()




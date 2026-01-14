"""Verify Snowflake connector class in JAR and check documentation."""
import paramiko

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Verifying Snowflake Connector Class in JAR")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Find JAR
    print("1. Finding Snowflake connector JAR...")
    jar_paths = [
        "/usr/share/java/plugins/snowflake-kafka-connector/lib/snowflake-kafka-connector-3.2.2.jar",
        "/usr/share/java/plugins/snowflake-kafka-connector/snowflake-kafka-connector-3.2.2.jar",
    ]
    
    jar_path = None
    for path in jar_paths:
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -f {path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        )
        if 'EXISTS' in stdout.read().decode('utf-8'):
            jar_path = path
            print(f"   ✅ Found: {jar_path}")
            break
    
    if not jar_path:
        print(f"   ❌ JAR not found")
        ssh.close()
        exit(1)
    
    # Check for connector class using jar command or unzip
    print(f"\n2. Checking for connector class in JAR...")
    print(f"   Expected class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    
    # Try with jar command
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} sh -c 'jar tf {jar_path} 2>&1 | grep -i \"SnowflakeSinkConnector.class\"'"
    )
    class_found = stdout.read().decode('utf-8').strip()
    
    if class_found:
        print(f"   ✅ Connector class found!")
        for line in class_found.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  Not found with jar command, trying alternative...")
        
        # Try listing all Snowflake classes
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} sh -c 'jar tf {jar_path} 2>&1 | grep -i \"snowflake.*connector\" | head -10'"
        )
        snowflake_classes = stdout.read().decode('utf-8').strip()
        if snowflake_classes:
            print(f"   Found Snowflake connector classes:")
            for line in snowflake_classes.split('\n'):
                if line.strip():
                    print(f"      {line}")
        else:
            print(f"   ❌ No Snowflake connector classes found")
    
    # Check package structure
    print(f"\n3. Checking package structure...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} sh -c 'jar tf {jar_path} 2>&1 | grep \"com/snowflake/kafka/connector/\" | head -20'"
    )
    package_structure = stdout.read().decode('utf-8').strip()
    if package_structure:
        print(f"   Package structure:")
        for line in package_structure.split('\n')[:15]:
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  Could not list package structure")
    
    # Check META-INF/services
    print(f"\n4. Checking META-INF/services (for service loader)...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} sh -c 'jar tf {jar_path} 2>&1 | grep \"META-INF/services\"'"
    )
    service_files = stdout.read().decode('utf-8').strip()
    if service_files:
        print(f"   Service files found:")
        for line in service_files.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  No META-INF/services files found")
    
    # Check manifest
    print(f"\n5. Checking MANIFEST.MF...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} sh -c 'jar xf {jar_path} META-INF/MANIFEST.MF && cat META-INF/MANIFEST.MF 2>&1 | head -30'"
    )
    manifest = stdout.read().decode('utf-8').strip()
    if manifest and 'Manifest-Version' in manifest:
        print(f"   Manifest:")
        for line in manifest.split('\n')[:20]:
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   ⚠️  Could not read manifest")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Documentation Findings:")
    print(f"{'='*70}")
    print(f"\n✅ Connector Class Name: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"✅ This is the correct class name according to Snowflake documentation")
    print(f"\nKey Requirements:")
    print(f"1. JAR file must be in Kafka Connect plugins directory")
    print(f"2. Kafka Connect must be restarted after installation")
    print(f"3. Connector class: com.snowflake.kafka.connector.SnowflakeSinkConnector")
    print(f"4. Compatible with Kafka Connect API 3.9.0+")
    print(f"\nIf the class exists in the JAR but still doesn't appear,")
    print(f"it may be a compatibility issue or the connector may need")
    print(f"to be loaded on first use (when creating a pipeline).")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




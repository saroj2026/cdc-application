"""Find the correct plugins directory in Kafka Connect container."""
import paramiko

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Finding Kafka Connect Plugins Directory")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Check common plugins directories
    common_dirs = [
        "/usr/share/java/plugins",
        "/usr/share/confluent-hub-components",
        "/usr/share/confluent-hub-components/confluentinc-kafka-connect-s3/lib",
        "/usr/share/java/kafka-connect-s3",
        "/usr/local/share/kafka/plugins",
        "/opt/connectors",
        "/kafka/connect/plugins"
    ]
    
    print("1. Checking common plugins directories...")
    for dir_path in common_dirs:
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} test -d {dir_path} && echo 'EXISTS' || echo 'NOT_FOUND'"
        )
        result = stdout.read().decode('utf-8').strip()
        if result == "EXISTS":
            print(f"   ✅ Found: {dir_path}")
            
            # List contents
            stdin, stdout, stderr = ssh.exec_command(
                f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la {dir_path} | head -20"
            )
            contents = stdout.read().decode('utf-8')
            if contents:
                print(f"   Contents:")
                for line in contents.split('\n')[:10]:
                    if line.strip():
                        print(f"      {line}")
        else:
            print(f"   ❌ Not found: {dir_path}")
    
    # Check environment variables
    print(f"\n2. Checking Kafka Connect environment variables...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} env | grep -i plugin"
    )
    env_output = stdout.read().decode('utf-8')
    if env_output:
        print(f"   Environment variables:")
        for line in env_output.split('\n'):
            if line.strip():
                print(f"      {line}")
    else:
        print(f"   No plugin-related environment variables found")
    
    # Check where existing connectors are
    print(f"\n3. Checking where existing connectors are installed...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} find /usr -name '*s3*connector*.jar' 2>/dev/null | head -5"
    )
    existing_connectors = stdout.read().decode('utf-8')
    if existing_connectors:
        print(f"   Found existing connectors:")
        for path in existing_connectors.split('\n'):
            if path.strip():
                print(f"      {path}")
                # Get directory
                dir_path = '/'.join(path.split('/')[:-1])
                print(f"      → Directory: {dir_path}")
    else:
        print(f"   No existing connectors found in /usr")
    
    # Check confluent hub components
    print(f"\n4. Checking Confluent Hub components...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} find /usr/share/confluent-hub-components -name '*.jar' 2>/dev/null | head -5"
    )
    hub_components = stdout.read().decode('utf-8')
    if hub_components:
        print(f"   Found Confluent Hub components:")
        for path in hub_components.split('\n'):
            if path.strip():
                print(f"      {path}")
                dir_path = '/'.join(path.split('/')[:-1])
                print(f"      → Directory: {dir_path}")
                break  # Just show first one
    
    ssh.close()
    
    print(f"\n{'='*70}")
    print("Next Steps:")
    print("Based on the output above, use the correct plugins directory")
    print("to install the Snowflake connector.")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()




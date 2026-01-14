"""Find and verify Snowflake connector installation."""
import paramiko

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
KAFKA_CONNECT_CONTAINER = "kafka-connect-cdc"

print("=" * 70)
print("Finding and Verifying Snowflake Connector")
print("=" * 70)

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
    print(f"✅ Connected to {VPS_HOST}\n")
    
    # Find the file
    print("1. Searching for Snowflake connector JAR...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec {KAFKA_CONNECT_CONTAINER} find /usr -name '*snowflake*kafka*connector*.jar' 2>/dev/null"
    )
    files = stdout.read().decode('utf-8').strip()
    
    if files:
        print(f"   ✅ Found files:")
        for file_path in files.split('\n'):
            if file_path.strip():
                print(f"      {file_path}")
                
                # Get file size
                stdin, stdout, stderr = ssh.exec_command(
                    f"docker exec {KAFKA_CONNECT_CONTAINER} stat -c%s '{file_path}'"
                )
                size = stdout.read().decode('utf-8').strip()
                if size.isdigit():
                    size_mb = int(size) / 1024 / 1024
                    print(f"         Size: {size_mb:.2f} MB")
                
                # Show file details
                stdin, stdout, stderr = ssh.exec_command(
                    f"docker exec {KAFKA_CONNECT_CONTAINER} ls -lh '{file_path}'"
                )
                file_info = stdout.read().decode('utf-8').strip()
                if file_info:
                    print(f"         {file_info}")
    else:
        print(f"   ❌ No Snowflake connector files found")
        print(f"   Checking if directory exists...")
        stdin, stdout, stderr = ssh.exec_command(
            f"docker exec {KAFKA_CONNECT_CONTAINER} ls -la /usr/share/confluent-hub-components/snowflake-kafka-connector/ 2>&1"
        )
        dir_contents = stdout.read().decode('utf-8')
        if dir_contents:
            print(f"   Directory contents:")
            print(f"   {dir_contents}")
        else:
            print(f"   Directory doesn't exist or is empty")
    
    # Check container status
    print(f"\n2. Container status...")
    stdin, stdout, stderr = ssh.exec_command(
        f"docker ps | grep {KAFKA_CONNECT_CONTAINER}"
    )
    container_info = stdout.read().decode('utf-8').strip()
    if container_info:
        print(f"   ✅ {container_info}")
    else:
        print(f"   ⚠️  Container not running")
    
    ssh.close()
    
    print(f"\n{'='*70}")
    if files:
        print("✅ Snowflake connector found!")
    else:
        print("⚠️  Snowflake connector not found - may need to reinstall")
    print(f"{'='*70}")
    print()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()




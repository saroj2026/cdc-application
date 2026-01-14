"""Update Kafka Connect connector via SSH using curl commands."""
import subprocess
import json
import time
import sys

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"
KAFKA_CONNECT_URL = "http://localhost:8083"

# AWS Credentials
ACCESS_KEY = "AKIATLTXNANW2EV7QGV2"
SECRET_KEY = "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"

print("=" * 70)
print("Updating Kafka Connect Connector via SSH")
print("=" * 70)

def run_ssh_command(command):
    """Run command on VPS via SSH."""
    ssh_cmd = f"sshpass -p '{VPS_PASS}' ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '{command}'"
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

try:
    # Step 1: Get current configuration
    print(f"\n1. Getting current connector configuration...\n")
    docker_cmd = f"docker exec kafka-connect-cdc curl -s {KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config"
    success, output, error = run_ssh_command(docker_cmd)
    
    if not success:
        print(f"   ❌ Failed to get configuration: {error}")
        sys.exit(1)
    
    try:
        current_config = json.loads(output)
        print(f"   ✅ Retrieved configuration")
        print(f"   Current aws.access.key.id: {current_config.get('aws.access.key.id', 'NOT SET')[:20]}...")
    except json.JSONDecodeError:
        print(f"   ❌ Failed to parse configuration JSON")
        print(f"   Output: {output[:200]}")
        sys.exit(1)
    
    # Step 2: Update credentials
    print(f"\n2. Updating AWS credentials...\n")
    current_config['aws.access.key.id'] = ACCESS_KEY
    current_config['aws.secret.access.key'] = SECRET_KEY
    
    # Step 3: Update connector via REST API
    print(f"3. Updating connector configuration...\n")
    config_json = json.dumps(current_config)
    
    # Escape JSON for shell command
    config_json_escaped = config_json.replace("'", "'\\''")
    docker_cmd = f"docker exec kafka-connect-cdc curl -s -X PUT -H 'Content-Type: application/json' -d '{config_json_escaped}' {KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/config"
    
    success, output, error = run_ssh_command(docker_cmd)
    
    if success:
        print(f"   ✅ Configuration updated!")
    else:
        print(f"   ❌ Failed to update: {error}")
        print(f"   Output: {output[:200]}")
        sys.exit(1)
    
    # Step 4: Restart connector
    print(f"\n4. Restarting connector...\n")
    docker_cmd = f"docker exec kafka-connect-cdc curl -s -X POST {KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/restart"
    success, output, error = run_ssh_command(docker_cmd)
    
    if success:
        print(f"   ✅ Restart command sent!")
    else:
        print(f"   ⚠️  Restart may have failed: {error}")
    
    # Step 5: Wait and check status
    print(f"\n5. Waiting 30 seconds and checking status...\n")
    time.sleep(30)
    
    docker_cmd = f"docker exec kafka-connect-cdc curl -s {KAFKA_CONNECT_URL}/connectors/{CONNECTOR_NAME}/status"
    success, output, error = run_ssh_command(docker_cmd)
    
    if success:
        try:
            status = json.loads(output)
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   Connector State: {connector_state}")
            
            tasks = status.get('tasks', [])
            for i, task in enumerate(tasks):
                task_state = task.get('state', 'UNKNOWN')
                print(f"   Task {i} State: {task_state}")
                
                if task_state == 'FAILED':
                    trace = task.get('trace', '')
                    if 'AWS Access Key Id' in trace:
                        print(f"      ❌ AWS credentials error")
                    elif 'SignatureDoesNotMatch' in trace or 'signature' in trace.lower():
                        print(f"      ❌ Secret key mismatch")
                    else:
                        print(f"      ⚠️  Error: {trace[:200]}...")
                elif task_state == 'RUNNING':
                    print(f"      ✅ Task is running!")
            
            print(f"\n{'='*70}")
            if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
                print("✅ SUCCESS! Connector is running!")
                print("Data should now be flowing to S3!")
            else:
                print("⚠️  Connector still has issues - check errors above")
            print(f"{'='*70}")
        except json.JSONDecodeError:
            print(f"   ⚠️  Could not parse status: {output[:200]}")
    else:
        print(f"   ⚠️  Could not get status: {error}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()


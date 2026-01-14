"""Check connector status via SSH to VPS."""
import subprocess
import json

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"

print("=" * 70)
print(f"Checking Connector Status via SSH: {CONNECTOR_NAME}")
print("=" * 70)

def run_ssh_command(command):
    """Run command on VPS via SSH using sshpass."""
    # Use sshpass to provide password
    ssh_cmd = f'sshpass -p "{VPS_PASS}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} "{command}"'
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

try:
    # Check connector status
    print(f"\n1. Getting connector status...\n")
    docker_cmd = f"docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/status"
    success, output, error = run_ssh_command(docker_cmd)
    
    if not success:
        print(f"   ❌ Failed to get status: {error}")
        print(f"   Output: {output}")
        print(f"\n   Trying alternative method...")
        # Try without sshpass (might work if SSH keys are set up)
        ssh_cmd = f'ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} "{docker_cmd}"'
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30, input=f"{VPS_PASS}\n")
        if result.returncode == 0:
            output = result.stdout
            success = True
        else:
            print(f"   ❌ Alternative method also failed")
            sys.exit(1)
    
    if success and output:
        try:
            status = json.loads(output)
            connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
            print(f"   ✅ Connector State: {connector_state}")
            
            tasks = status.get('tasks', [])
            print(f"\n2. Tasks ({len(tasks)}):\n")
            
            for i, task in enumerate(tasks):
                task_state = task.get('state', 'UNKNOWN')
                task_id = task.get('id', i)
                print(f"   Task {task_id}: {task_state}")
                
                if task_state == 'FAILED':
                    trace = task.get('trace', '')
                    print(f"      ❌ FAILED")
                    print(f"      Error: {trace[:400]}...")
                elif task_state == 'RUNNING':
                    print(f"      ✅ RUNNING")
            
            # Get configuration
            print(f"\n3. Configuration:\n")
            docker_cmd = f"docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/config"
            success, config_output, error = run_ssh_command(docker_cmd)
            
            if success and config_output:
                try:
                    config = json.loads(config_output)
                    print(f"   aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:20]}...")
                    print(f"   aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}")
                    print(f"   flush.size: {config.get('flush.size', 'NOT SET')}")
                    print(f"   s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
                except:
                    print(f"   ⚠️  Could not parse config: {config_output[:200]}")
            
            print(f"\n{'='*70}")
            if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
                print("✅ SUCCESS! Connector is RUNNING!")
                print("Data should be flowing to S3 now.")
            elif connector_state == 'RUNNING' and any(task.get('state') == 'FAILED' for task in tasks):
                print("⚠️  Connector is RUNNING but task is FAILED")
                print("Check the error above.")
            else:
                print(f"⚠️  Connector state: {connector_state}")
            print(f"{'='*70}")
            
        except json.JSONDecodeError:
            print(f"   ⚠️  Could not parse status JSON")
            print(f"   Output: {output[:500]}")
    else:
        print(f"   ❌ No output received")
        print(f"   Error: {error}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print(f"\nNote: If sshpass is not available, you can:")
    print(f"  1. SSH manually: ssh root@72.61.233.209")
    print(f"  2. Run: docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/status")




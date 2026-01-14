"""Check connector status via SSH using paramiko or subprocess."""
import subprocess
import json
import sys

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASS = "segmbp@1100"
CONNECTOR_NAME = "sink-as400-s3_p-s3-dbo"

print("=" * 70)
print(f"Checking Connector via SSH: {CONNECTOR_NAME}")
print("=" * 70)

# Try using paramiko if available
try:
    import paramiko
    
    print(f"\n1. Connecting to VPS via SSH (using paramiko)...\n")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=10)
        print(f"   ✅ Connected to {VPS_HOST}")
        
        # Get connector status
        print(f"\n2. Getting connector status...\n")
        cmd = f"docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/status"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        status_output = stdout.read().decode('utf-8')
        error_output = stderr.read().decode('utf-8')
        
        if status_output:
            try:
                status = json.loads(status_output)
                connector_state = status.get('connector', {}).get('state', 'UNKNOWN')
                print(f"   ✅ Connector State: {connector_state}")
                
                tasks = status.get('tasks', [])
                print(f"\n3. Tasks ({len(tasks)}):\n")
                
                for i, task in enumerate(tasks):
                    task_state = task.get('state', 'UNKNOWN')
                    print(f"   Task {i}: {task_state}")
                    
                    if task_state == 'FAILED':
                        trace = task.get('trace', '')
                        print(f"      ❌ FAILED")
                        print(f"      Error: {trace[:400]}...")
                    elif task_state == 'RUNNING':
                        print(f"      ✅ RUNNING")
                
                # Get configuration
                print(f"\n4. Configuration:\n")
                cmd = f"docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/config"
                stdin, stdout, stderr = ssh.exec_command(cmd)
                config_output = stdout.read().decode('utf-8')
                
                if config_output:
                    try:
                        config = json.loads(config_output)
                        print(f"   aws.access.key.id: {config.get('aws.access.key.id', 'NOT SET')[:20]}...")
                        print(f"   aws.secret.access.key: {'SET' if config.get('aws.secret.access.key') else 'NOT SET'}")
                        print(f"   flush.size: {config.get('flush.size', 'NOT SET')}")
                        print(f"   s3.bucket.name: {config.get('s3.bucket.name', 'NOT SET')}")
                    except:
                        print(f"   ⚠️  Could not parse config")
                
                print(f"\n{'='*70}")
                if connector_state == 'RUNNING' and all(task.get('state') == 'RUNNING' for task in tasks):
                    print("✅ SUCCESS! Connector is RUNNING!")
                    print("Data should be flowing to S3 now.")
                else:
                    print(f"⚠️  Connector state: {connector_state}")
                    if any(task.get('state') == 'FAILED' for task in tasks):
                        print("Task is FAILED - check error above.")
                print(f"{'='*70}")
                
            except json.JSONDecodeError:
                print(f"   ⚠️  Could not parse status JSON")
                print(f"   Output: {status_output[:500]}")
        else:
            print(f"   ❌ No output received")
            if error_output:
                print(f"   Error: {error_output}")
        
        ssh.close()
        
    except paramiko.AuthenticationException:
        print(f"   ❌ Authentication failed")
        print(f"   Please verify SSH credentials")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        raise

except ImportError:
    # paramiko not available, try subprocess with ssh
    print(f"\n⚠️  paramiko not available, trying subprocess method...\n")
    
    # Create a temporary script to run on VPS
    script_content = f"""#!/bin/bash
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/status
"""
    
    # Try to use ssh with password via expect or plink
    print("Please run these commands manually on your VPS:")
    print(f"  ssh root@72.61.233.209")
    print(f"  docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/{CONNECTOR_NAME}/status | python3 -m json.tool")
    print(f"\nOr check in Kafka UI:")
    print(f"  http://72.61.233.209:8080/ui/clusters/local/connectors/{CONNECTOR_NAME}")




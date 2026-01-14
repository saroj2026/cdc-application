#!/usr/bin/env python3
import subprocess
import time
import sys

VPS_HOST = "72.61.233.209"
VPS_USER = "root"
VPS_PASSWORD = "segmbp@1100"
CONTAINER_NAME = "kafka-connect-cdc"

def run_cmd(cmd, description):
    print(f"\n{description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

print("=" * 80)
print("🚀 COMPLETING JAVA 17 INSTALLATION")
print("=" * 80)

# Step 1: Move Java 17
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker exec {CONTAINER_NAME} sh -c \'mv /tmp/jdk-17.0.2 /opt/ 2>/dev/null && echo OK || echo Already moved\'"',
    "1. Moving Java 17 to /opt"
)

# Step 2: Verify
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker exec {CONTAINER_NAME} /opt/jdk-17.0.2/bin/java -version 2>&1 | head -1"',
    "2. Verifying Java 17"
)

# Step 3: Create symlink
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker exec {CONTAINER_NAME} sh -c \'cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17 && echo OK\'"',
    "3. Creating Java 17 symlink"
)

# Step 4: Update startup script
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker exec {CONTAINER_NAME} sh -c \'if ! grep -q JAVA_HOME=/opt/jdk-17.0.2 /etc/confluent/docker/run; then sed -i \\"1a export JAVA_HOME=/opt/jdk-17.0.2\\" /etc/confluent/docker/run && sed -i \\"1a export PATH=\\$JAVA_HOME/bin:\\$PATH\\" /etc/confluent/docker/run && echo OK; else echo Already configured; fi\'"',
    "4. Updating startup script"
)

# Step 5: Restart
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker restart {CONTAINER_NAME}"',
    "5. Restarting Kafka Connect"
)

print("\n⏳ Waiting 70 seconds for Kafka Connect to start...")
time.sleep(70)

# Step 6: Verify Java
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker exec {CONTAINER_NAME} java -version 2>&1 | head -1"',
    "6. Verifying Java 17 is active"
)

# Step 7: Check connector
run_cmd(
    f'sshpass -p "{VPS_PASSWORD}" ssh -o StrictHostKeyChecking=no {VPS_USER}@{VPS_HOST} '
    f'"docker logs {CONTAINER_NAME} 2>&1 | grep -i \'Added plugin.*As400RpcConnector\' | tail -1"',
    "7. Checking IBM i connector"
)

print("\n" + "=" * 80)
print("✅ INSTALLATION COMPLETE")
print("=" * 80)


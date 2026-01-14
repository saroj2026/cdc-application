#!/bin/bash
# Complete Java 17 installation - Run this script

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "🚀 Completing Java 17 Installation..."

# Step 1: Move Java 17 to /opt
echo "1. Moving Java 17 to /opt..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'mv /tmp/jdk-17.0.2 /opt/ 2>/dev/null && echo OK || echo Already moved'"

# Step 2: Verify Java 17
echo "2. Verifying Java 17..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME /opt/jdk-17.0.2/bin/java -version 2>&1 | head -1"

# Step 3: Create symlink
echo "3. Creating Java 17 symlink..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17 && echo OK'"

# Step 4: Update startup script
echo "4. Updating startup script..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'if ! grep -q JAVA_HOME=/opt/jdk-17.0.2 /etc/confluent/docker/run; then sed -i \"1a export JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run && sed -i \"1a export PATH=\$JAVA_HOME/bin:\$PATH\" /etc/confluent/docker/run && echo OK; else echo Already configured; fi'"

# Step 5: Restart
echo "5. Restarting Kafka Connect..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker restart $CONTAINER_NAME"

echo "6. Waiting 70 seconds..."
sleep 70

# Step 6: Verify
echo "7. Verifying Java 17..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version 2>&1 | head -1"

echo "8. Checking IBM i connector..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

echo "✅ Installation complete! Check output above."


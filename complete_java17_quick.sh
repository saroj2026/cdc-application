#!/bin/bash
# Quick completion script - all steps in one
VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "🚀 Completing Java 17 installation..."

# Move Java 17 to /opt
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'mv /tmp/jdk-17.0.2 /opt/ 2>/dev/null || echo \"Already moved\"'"

# Verify and create symlink
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c '/opt/jdk-17.0.2/bin/java -version 2>&1 | head -1 && cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17'"

# Update startup script
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'if ! grep -q \"JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run; then sed -i \"1a export JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run && sed -i \"1a export PATH=\$JAVA_HOME/bin:\$PATH\" /etc/confluent/docker/run; fi'"

# Restart
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker restart $CONTAINER_NAME"

echo "⏳ Waiting 70 seconds..."
sleep 70

# Verify
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version 2>&1 | head -1"

sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

echo "✅ Done! Check output above for Java version and connector status."


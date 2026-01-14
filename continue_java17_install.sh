#!/bin/bash

# Continue Java 17 installation from where it left off
# Java 17 is already extracted in /tmp/jdk-17.0.2

set -e

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "=================================================================================="
echo "🔧 CONTINUING JAVA 17 INSTALLATION"
echo "=================================================================================="
echo ""

# Move from /tmp to /opt (writable location)
echo "1️⃣ Moving Java 17 from /tmp to /opt..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'mv /tmp/jdk-17.0.2 /opt/ 2>/dev/null && echo \"Moved to /opt/jdk-17.0.2\" || echo \"Already moved or not found\"'"

# Verify Java 17
echo ""
echo "2️⃣ Verifying Java 17..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME /opt/jdk-17.0.2/bin/java -version 2>&1 | head -1"

# Create symlink
echo ""
echo "3️⃣ Creating Java 17 symlink..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17 && /usr/bin/java17 -version 2>&1 | head -1'"

# Check startup script
echo ""
echo "4️⃣ Checking startup script..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'head -30 /etc/confluent/docker/run'"

# Update startup script
echo ""
echo "5️⃣ Updating startup script with JAVA_HOME..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'if ! grep -q \"JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run; then sed -i \"1a export JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run && sed -i \"1a export PATH=\$JAVA_HOME/bin:\$PATH\" /etc/confluent/docker/run && echo \"JAVA_HOME added to startup script\"; else echo \"JAVA_HOME already configured\"; fi'"

# Verify startup script
echo ""
echo "6️⃣ Verifying startup script configuration..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'grep -E \"JAVA_HOME|PATH.*jdk\" /etc/confluent/docker/run | head -3'"

# Restart
echo ""
echo "7️⃣ Restarting Kafka Connect..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker restart $CONTAINER_NAME && echo 'Container restarted'"

echo ""
echo "⏳ Waiting 70 seconds for Kafka Connect to start..."
sleep 70

# Verify
echo ""
echo "8️⃣ Verifying Java 17 is active..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version 2>&1 | head -1"

echo ""
echo "9️⃣ Checking if IBM i connector loads..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

echo ""
echo "🔟 Verifying via API..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); as400 = [p for p in plugins if 'As400RpcConnector' in p.get('class', '')]; print('✅✅✅ IBM i CONNECTOR LOADED!' if as400 else '❌ Not found'); [print(f'  {p.get(\"class\")} v{p.get(\"version\")}') for p in as400]\" 2>/dev/null || echo 'API not ready'"

echo ""
echo "=================================================================================="
echo "✅ INSTALLATION COMPLETE"
echo "=================================================================================="
echo ""


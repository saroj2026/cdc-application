#!/bin/bash

# Script to upgrade Kafka Connect to Java 17
# This enables the IBM i connector (2.6.0.Final) which requires Java 17

set -e

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "=================================================================================="
echo "🚀 UPGRADING KAFKA CONNECT TO JAVA 17"
echo "=================================================================================="
echo ""

# Step 1: Check current Java version
echo "1️⃣ Checking current Java version..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version"

echo ""
echo "2️⃣ Installing Java 17..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'apt-get update && apt-get install -y openjdk-17-jdk-headless'"

echo ""
echo "3️⃣ Setting Java 17 as default..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-17-openjdk-amd64/bin/java 1 && update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java'"

echo ""
echo "4️⃣ Configuring JAVA_HOME..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'echo \"export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64\" >> /etc/profile && echo \"export PATH=\$JAVA_HOME/bin:\$PATH\" >> /etc/profile'"

echo ""
echo "5️⃣ Verifying Java 17 installation..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version"

echo ""
echo "6️⃣ Restarting Kafka Connect..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker restart $CONTAINER_NAME"

echo ""
echo "⏳ Waiting 70 seconds for Kafka Connect to start..."
sleep 70

echo ""
echo "7️⃣ Verifying Java 17 is active..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version"

echo ""
echo "8️⃣ Checking if IBM i connector loads..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

echo ""
echo "9️⃣ Verifying all connectors via API..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); as400 = [p for p in plugins if 'As400RpcConnector' in p.get('class', '') or 'db2as400' in p.get('class', '').lower()]; print('✅✅✅ IBM i CONNECTOR LOADED!' if as400 else '❌ IBM i connector not found'); [print(f'  Class: {p.get(\"class\")}, Version: {p.get(\"version\")}') for p in as400]; existing = [p for p in plugins if 'db2' in p.get('class', '').lower() or 'postgres' in p.get('class', '').lower() or 'sqlserver' in p.get('class', '').lower()]; print(f'✅ Existing connectors: {len(existing)} loaded')\" 2>/dev/null || echo '⏳ API not ready yet'"

echo ""
echo "🔟 Checking for errors..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'error\|exception' | grep -i 'connector\|plugin' | tail -5 || echo '✅ No connector errors found'"

echo ""
echo "=================================================================================="
echo "✅ UPGRADE COMPLETE"
echo "=================================================================================="
echo ""
echo "Next steps:"
echo "1. Verify all existing connectors still work"
echo "2. Test the IBM i connector"
echo "3. Monitor logs for any issues"
echo ""


#!/bin/bash

# Manual Java 17 installation for Confluent Platform Docker image
# Downloads Java 17 binary and configures it

set -e

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "=================================================================================="
echo "🚀 INSTALLING JAVA 17 MANUALLY IN CONTAINER"
echo "=================================================================================="
echo ""

# Step 1: Download Java 17 on VPS
echo "1️⃣ Downloading Java 17 on VPS..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "cd /tmp && wget -q https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz && echo 'Downloaded Java 17' || echo 'Download failed'"

# Step 2: Copy to container
echo ""
echo "2️⃣ Copying Java 17 to container..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker cp /tmp/openjdk-17.0.2_linux-x64_bin.tar.gz $CONTAINER_NAME:/tmp/ && echo 'Copied to container'"

# Step 3: Extract in container (to /opt which is typically writable)
echo ""
echo "3️⃣ Extracting Java 17 in container..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cd /tmp && tar -xzf openjdk-17.0.2_linux-x64_bin.tar.gz && mv jdk-17.0.2 /opt/ && echo \"Java 17 extracted to /opt/jdk-17.0.2\"'"

# Step 4: Verify Java 17
echo ""
echo "4️⃣ Verifying Java 17 installation..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME /opt/jdk-17.0.2/bin/java -version"

# Step 5: Create symlink or update PATH
echo ""
echo "5️⃣ Creating Java 17 symlink..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'ln -sf /opt/jdk-17.0.2/bin/java /usr/bin/java17 2>/dev/null || cp /opt/jdk-17.0.2/bin/java /usr/bin/java17 && chmod +x /usr/bin/java17 && /usr/bin/java17 -version'"

# Step 6: Update startup script to use Java 17
echo ""
echo "6️⃣ Checking startup script..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cat /etc/confluent/docker/run | head -20'"

echo ""
echo "7️⃣ Setting JAVA_HOME in startup script..."
# We need to modify the startup script to use Java 17
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'if grep -q \"JAVA_HOME\" /etc/confluent/docker/run; then sed -i \"s|export JAVA_HOME=.*|export JAVA_HOME=/opt/jdk-17.0.2|g\" /etc/confluent/docker/run; else sed -i \"1i export JAVA_HOME=/opt/jdk-17.0.2\" /etc/confluent/docker/run; fi && sed -i \"s|export PATH=.*|export PATH=\$JAVA_HOME/bin:\$PATH|g\" /etc/confluent/docker/run 2>/dev/null && echo \"JAVA_HOME configured\" || echo \"Manual configuration needed\"'"

# Step 7: Restart container
echo ""
echo "8️⃣ Restarting Kafka Connect..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker restart $CONTAINER_NAME && echo 'Container restarted'"

echo ""
echo "⏳ Waiting 70 seconds for Kafka Connect to start..."
sleep 70

# Step 8: Verify
echo ""
echo "9️⃣ Verifying Java 17 is active..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version 2>&1 | head -1"

echo ""
echo "🔟 Checking if IBM i connector loads..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'Added plugin.*As400RpcConnector' | tail -1"

echo ""
echo "=================================================================================="
echo "✅ INSTALLATION COMPLETE"
echo "=================================================================================="
echo ""


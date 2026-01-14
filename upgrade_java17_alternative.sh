#!/bin/bash

# Alternative Java 17 upgrade script for Confluent Platform Docker image
# This uses a different approach since apt-get may not be available

set -e

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "=================================================================================="
echo "🚀 UPGRADING KAFKA CONNECT TO JAVA 17 (Alternative Method)"
echo "=================================================================================="
echo ""

# Check current Java
echo "1️⃣ Current Java version:"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME java -version 2>&1 | head -1"

echo ""
echo "2️⃣ Checking container type..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME cat /etc/os-release | grep -E '^NAME|^ID' | head -2"

echo ""
echo "3️⃣ Checking available Java installations..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'ls -la /usr/lib/jvm/ 2>/dev/null || echo \"Checking Java locations...\"'"

echo ""
echo "4️⃣ Checking if we can download Java 17..."
# Try to download Java 17 directly
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cd /tmp && curl -L -o openjdk-17.tar.gz \"https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz\" 2>&1 | tail -3 || echo \"Download method 1 failed\"'"

echo ""
echo "5️⃣ Alternative: Setting JAVA_HOME to use existing Java 17 if available..."
# Check if Java 17 already exists somewhere
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'find /usr -name \"java\" -type f 2>/dev/null | grep -E \"17|jdk-17\" | head -3 || echo \"Java 17 not found in container\"'"

echo ""
echo "=================================================================================="
echo "⚠️  CONTAINER DOESN'T HAVE APT-GET"
echo "=================================================================================="
echo ""
echo "Options:"
echo "1. Use a newer Confluent Platform Docker image with Java 17"
echo "2. Create a custom Dockerfile with Java 17"
echo "3. Mount Java 17 from host to container"
echo ""
echo "Recommended: Upgrade to Confluent Platform 7.5+ which includes Java 17"
echo ""


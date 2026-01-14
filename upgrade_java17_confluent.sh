#!/bin/bash

# Java 17 upgrade for Confluent Platform Docker image
# Since apt-get is not available, we'll use a different approach

set -e

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"

echo "=================================================================================="
echo "🚀 UPGRADING KAFKA CONNECT TO JAVA 17 (Confluent Platform Method)"
echo "=================================================================================="
echo ""

echo "⚠️  The Confluent Platform Docker image doesn't include apt-get."
echo "    We need to use a different approach."
echo ""

echo "Option 1: Upgrade to Confluent Platform 7.5+ (Recommended)"
echo "  - These versions include Java 17 by default"
echo "  - Requires Docker image upgrade"
echo ""

echo "Option 2: Download Java 17 and configure manually"
echo "  - Download Java 17 binary"
echo "  - Extract to container"
echo "  - Configure environment variables"
echo ""

echo "Checking current setup..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker inspect $CONTAINER_NAME | grep -i image | head -1"

echo ""
echo "Current Java location:"
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'which java && java -version 2>&1 | head -1'"

echo ""
echo "=================================================================================="
echo "RECOMMENDED SOLUTION: Upgrade Docker Image"
echo "=================================================================================="
echo ""
echo "The best approach is to use a Confluent Platform image with Java 17:"
echo ""
echo "1. Stop current container:"
echo "   docker stop kafka-connect-cdc"
echo ""
echo "2. Use Confluent Platform 7.5+ image (includes Java 17):"
echo "   docker run ... confluentinc/cp-kafka-connect:7.5.0"
echo ""
echo "OR configure environment variable to use Java 17 if available"
echo ""


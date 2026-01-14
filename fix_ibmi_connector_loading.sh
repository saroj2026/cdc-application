#!/bin/bash

# Script to diagnose and fix IBM i connector loading issues
# This script checks for missing dependencies and class loading errors

set -e

CONTAINER_NAME="kafka-connect-cdc"
VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"

echo "=================================================================================="
echo "🔍 DIAGNOSING IBM i CONNECTOR LOADING ISSUE"
echo "=================================================================================="

# Check if connector files exist
echo ""
echo "1️⃣ Checking connector files..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cd /usr/share/java/plugins/debezium-connector-ibmi && ls -la *.jar'"

# Check service file
echo ""
echo "2️⃣ Checking service file..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cd /usr/share/java/plugins/debezium-connector-ibmi && unzip -p debezium-connector-ibmi-2.6.0.Final.jar META-INF/services/org.apache.kafka.connect.source.SourceConnector 2>/dev/null'"

# Check for class loading errors in logs
echo ""
echo "3️⃣ Checking for class loading errors..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -i 'error\|exception\|warn' | grep -i 'ibmi\|as400\|db2as400' | tail -10"

# Check if jt400.jar exists
echo ""
echo "4️⃣ Checking for jt400.jar..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker exec $CONTAINER_NAME sh -c 'cd /usr/share/java/plugins/debezium-connector-ibmi && ls -la jt400*'"

# Check plugin loading in logs
echo ""
echo "5️⃣ Checking plugin loading logs..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "docker logs $CONTAINER_NAME 2>&1 | grep -A 20 'Loading plugin from.*ibmi' | tail -25"

# Check if connector is available via API
echo ""
echo "6️⃣ Checking connector availability via API..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" \
  "curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -c \"import sys, json; plugins = json.load(sys.stdin); as400 = [p for p in plugins if 'As400RpcConnector' in p.get('class', '') or 'db2as400' in p.get('class', '').lower()]; print('✅ CONNECTOR FOUND!' if as400 else '❌ Connector not found'); [print(f'  Class: {p.get(\"class\")}') for p in as400]\" 2>/dev/null || echo 'Kafka Connect not ready or API error'"

echo ""
echo "=================================================================================="
echo "✅ DIAGNOSIS COMPLETE"
echo "=================================================================================="


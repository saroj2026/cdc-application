#!/bin/bash
# Install Debezium IBM i connector 2.6.0.Final
# Run this from your Mac

VPS_HOST="72.61.233.209"
VPS_USER="root"
VPS_PASSWORD="segmbp@1100"
CONTAINER_NAME="kafka-connect-cdc"
CONNECTOR_NAME="debezium-connector-ibmi"
LOCAL_CONNECTOR_PATH="/Users/kumargaurav/Desktop/CDCTEAM/debezium-connector-ibmi-2.6.0.Final"
CONTAINER_PLUGIN_PATH="/usr/share/java/plugins"

echo "=================================================================================="
echo "🔄 INSTALLING DEBEZIUM IBM i CONNECTOR 2.6.0.Final"
echo "=================================================================================="
echo ""

echo "Step 1: Checking local connector..."
if [ ! -d "$LOCAL_CONNECTOR_PATH" ]; then
    echo "❌ Local connector not found at: $LOCAL_CONNECTOR_PATH"
    exit 1
fi

echo "✅ Local connector found: $LOCAL_CONNECTOR_PATH"
echo ""

echo "Step 2: Checking for JAR files..."
LOCAL_JAR_COUNT=$(find "$LOCAL_CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l | tr -d ' ')

if [ "$LOCAL_JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found!"
    exit 1
fi

echo "✅ Found $LOCAL_JAR_COUNT JAR files"
echo ""

echo "Step 3: Removing old connector from VPS..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "docker exec $CONTAINER_NAME rm -rf $CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME" 2>/dev/null
echo "✅ Old connector removed"
echo ""

echo "Step 4: Copying connector to VPS..."
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no -r "$LOCAL_CONNECTOR_PATH" "$VPS_USER@$VPS_HOST:/tmp/$CONNECTOR_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy connector to VPS"
    exit 1
fi

echo "✅ Connector copied to VPS"
echo ""

echo "Step 5: Installing connector in container..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "docker cp /tmp/$CONNECTOR_NAME $CONTAINER_NAME:$CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to install connector"
    exit 1
fi

echo "✅ Connector installed"
echo ""

echo "Step 6: Verifying JAR files..."
CONTAINER_JAR_COUNT=$(sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "docker exec $CONTAINER_NAME sh -c 'ls $CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME/*.jar 2>/dev/null | wc -l'" | tr -d ' ')

if [ "$CONTAINER_JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in container!"
    exit 1
fi

echo "✅ Found $CONTAINER_JAR_COUNT JAR files in container"
echo ""

echo "Step 7: Restarting Kafka Connect..."
sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "docker restart $CONTAINER_NAME"
echo "Waiting 50 seconds for restart..."
sleep 50
echo "✅ Kafka Connect restarted"
echo ""

echo "Step 8: Verifying connector is loaded..."
sleep 5
PLUGIN_CHECK=$(sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i 'As400RpcConnector\|db2as400'")

if [ -n "$PLUGIN_CHECK" ]; then
    echo "✅ AS400 connector plugin is LOADED!"
    echo ""
    echo "Connector details:"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i 'As400RpcConnector\|db2as400' || curl -s http://localhost:8083/connector-plugins | grep -i 'As400RpcConnector\|db2as400' -A 5"
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! Connector is installed and loaded"
    echo "=================================================================================="
else
    echo "⚠️  Connector installed but not yet loaded"
    echo ""
    echo "Check logs:"
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "docker logs $CONTAINER_NAME | tail -50 | grep -i 'error\|exception\|ibmi'"
fi

echo ""

#!/bin/bash
# Complete reinstall of IBM i connector from local machine
# Run this from your Mac

echo "=================================================================================="
echo "🔄 COMPLETE REINSTALL OF IBM i CONNECTOR"
echo "=================================================================================="
echo ""

VPS_HOST="72.61.233.209"
VPS_USER="root"
CONTAINER_NAME="kafka-connect-cdc"
CONNECTOR_NAME="debezium-connector-ibmi"
LOCAL_CONNECTOR_PATH="/Users/kumargaurav/Desktop/CDCTEAM/debezium-connector-ibmi"
CONTAINER_PLUGIN_PATH="/usr/share/java/plugins"

echo "Step 1: Checking local connector..."
if [ ! -d "$LOCAL_CONNECTOR_PATH" ]; then
    echo "❌ Local connector not found at: $LOCAL_CONNECTOR_PATH"
    echo ""
    echo "Please ensure the connector is at:"
    echo "  $LOCAL_CONNECTOR_PATH"
    exit 1
fi

echo "✅ Local connector found: $LOCAL_CONNECTOR_PATH"
echo ""

echo "Step 2: Checking for JAR files in local connector..."
LOCAL_JAR_COUNT=$(find "$LOCAL_CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l | tr -d ' ')

if [ "$LOCAL_JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in local connector!"
    echo ""
    echo "The connector folder exists but is empty or incomplete."
    echo "Please ensure you have the complete connector with all JAR files."
    exit 1
fi

echo "✅ Found $LOCAL_JAR_COUNT JAR files in local connector"
echo ""

echo "Step 3: Removing old connector from VPS..."
ssh "$VPS_USER@$VPS_HOST" "docker exec $CONTAINER_NAME rm -rf $CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME" 2>/dev/null
echo "✅ Old connector removed"
echo ""

echo "Step 4: Copying connector to VPS..."
echo "This may take a few minutes..."
scp -r "$LOCAL_CONNECTOR_PATH" "$VPS_USER@$VPS_HOST:/tmp/$CONNECTOR_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy connector to VPS"
    exit 1
fi

echo "✅ Connector copied to VPS"
echo ""

echo "Step 5: Installing connector in Kafka Connect container..."
ssh "$VPS_USER@$VPS_HOST" "docker cp /tmp/$CONNECTOR_NAME $CONTAINER_NAME:$CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME"

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy connector to container"
    exit 1
fi

echo "✅ Connector installed in container"
echo ""

echo "Step 6: Verifying JAR files in container..."
CONTAINER_JAR_COUNT=$(ssh "$VPS_USER@$VPS_HOST" "docker exec $CONTAINER_NAME find $CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME -name '*.jar' 2>/dev/null | wc -l" | tr -d ' ')

if [ "$CONTAINER_JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in container after installation!"
    echo "   Something went wrong during installation"
    exit 1
fi

echo "✅ Found $CONTAINER_JAR_COUNT JAR files in container"
echo ""

echo "Step 7: Checking connector structure..."
ssh "$VPS_USER@$VPS_HOST" "docker exec $CONTAINER_NAME ls -la $CONTAINER_PLUGIN_PATH/$CONNECTOR_NAME | head -10"
echo ""

echo "Step 8: Restarting Kafka Connect..."
ssh "$VPS_USER@$VPS_HOST" "docker restart $CONTAINER_NAME"
echo "Waiting 45 seconds for Kafka Connect to restart..."
sleep 45
echo "✅ Kafka Connect restarted"
echo ""

echo "Step 9: Verifying connector is loaded..."
echo "Checking connector plugins..."
sleep 5

PLUGIN_CHECK=$(ssh "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i 'As400RpcConnector\|db2as400'")

if [ -n "$PLUGIN_CHECK" ]; then
    echo "✅ AS400 connector plugin is LOADED!"
    echo ""
    echo "Connector details:"
    ssh "$VPS_USER@$VPS_HOST" "curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i 'As400RpcConnector\|db2as400' || curl -s http://localhost:8083/connector-plugins | grep -i 'As400RpcConnector\|db2as400' -A 5"
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! Connector is installed and loaded"
    echo "=================================================================================="
    echo ""
    echo "You can now start your AS400 pipeline!"
else
    echo "⚠️  Connector installed but not yet loaded"
    echo ""
    echo "This may take a few more seconds. Try checking again:"
    echo "  ssh $VPS_USER@$VPS_HOST"
    echo "  curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo ""
    echo "Or check logs for errors:"
    echo "  docker logs $CONTAINER_NAME | tail -50 | grep -i error"
fi

echo ""


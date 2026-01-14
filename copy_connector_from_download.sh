#!/bin/bash
# Copy Debezium AS400 connector from download folder to Kafka Connect container
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "📦 COPYING DEBEZIUM AS400 CONNECTOR FROM DOWNLOAD FOLDER"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"
DOWNLOAD_DIRS=(
    "$HOME/download"
    "$HOME/Downloads"
    "/root/download"
    "/root/Downloads"
    "./download"
    "./Downloads"
    "/opt/cdc3/connect-plugins"
)

# Find the connector
echo "Step 1: Looking for debezium-connector-ibmi in download folders..."
CONNECTOR_PATH=""

for dir in "${DOWNLOAD_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  Checking: $dir"
        FOUND=$(find "$dir" -type d -name "debezium-connector-ibmi*" 2>/dev/null | head -1)
        if [ -n "$FOUND" ]; then
            CONNECTOR_PATH="$FOUND"
            echo "  ✅ Found: $CONNECTOR_PATH"
            break
        fi
    fi
done

# Also search more broadly
if [ -z "$CONNECTOR_PATH" ]; then
    echo ""
    echo "  Searching more broadly..."
    CONNECTOR_PATH=$(find /root /home -type d -name "debezium-connector-ibmi*" 2>/dev/null | head -1)
    if [ -n "$CONNECTOR_PATH" ]; then
        echo "  ✅ Found: $CONNECTOR_PATH"
    fi
fi

if [ -z "$CONNECTOR_PATH" ]; then
    echo ""
    echo "❌ Connector not found in common download locations"
    echo ""
    echo "Please specify the full path to the connector, or run:"
    echo "  find / -type d -name 'debezium-connector-ibmi*' 2>/dev/null"
    exit 1
fi

echo ""
echo "Step 2: Verifying connector directory..."
if [ ! -d "$CONNECTOR_PATH" ]; then
    echo "❌ Connector path is not a directory: $CONNECTOR_PATH"
    exit 1
fi

# Count JAR files
JAR_COUNT=$(find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l)
if [ "$JAR_COUNT" -eq 0 ]; then
    echo "⚠️  No JAR files found in connector directory"
    echo "   This might not be a valid connector installation"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Found $JAR_COUNT JAR files in connector"
fi

echo ""
echo "Step 3: Checking Kafka Connect container..."
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container '$CONTAINER_NAME' is not running!"
    echo ""
    echo "Available containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo "✅ Container '$CONTAINER_NAME' is running"

echo ""
echo "Step 4: Checking if connector already exists in container..."
CONNECTOR_NAME=$(basename "$CONNECTOR_PATH")
CONTAINER_PATH="/usr/share/java/plugins/$CONNECTOR_NAME"

if docker exec "$CONTAINER_NAME" test -d "$CONTAINER_PATH" 2>/dev/null; then
    echo "⚠️  Connector already exists in container at: $CONTAINER_PATH"
    read -p "Replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "  Removing existing connector..."
        docker exec "$CONTAINER_NAME" rm -rf "$CONTAINER_PATH"
    else
        echo "  Keeping existing connector"
        echo ""
        echo "Step 5: Verifying existing connector is loaded..."
        sleep 2
        if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector"; then
            echo "✅ AS400 connector is already loaded!"
            exit 0
        else
            echo "⚠️  Connector exists but not loaded. Restarting container..."
            docker restart "$CONTAINER_NAME"
            sleep 30
            curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector" && echo "✅ SUCCESS!" || echo "⚠️  May need more time"
            exit 0
        fi
    fi
fi

echo ""
echo "Step 5: Copying connector to container..."
echo "  From: $CONNECTOR_PATH"
echo "  To: $CONTAINER_NAME:$CONTAINER_PATH"

docker cp "$CONNECTOR_PATH" "$CONTAINER_NAME:$CONTAINER_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Connector copied successfully"
    
    # Verify copy
    echo ""
    echo "Step 6: Verifying copy..."
    if docker exec "$CONTAINER_NAME" test -d "$CONTAINER_PATH" 2>/dev/null; then
        CONTAINER_JAR_COUNT=$(docker exec "$CONTAINER_NAME" find "$CONTAINER_PATH" -name "*.jar" 2>/dev/null | wc -l)
        echo "✅ Connector verified in container ($CONTAINER_JAR_COUNT JAR files)"
    else
        echo "❌ Verification failed - connector not found in container"
        exit 1
    fi
else
    echo "❌ Failed to copy connector"
    exit 1
fi

echo ""
echo "Step 7: Restarting Kafka Connect container..."
docker restart "$CONTAINER_NAME"

echo ""
echo "Waiting 30 seconds for Kafka Connect to restart..."
sleep 30

echo ""
echo "Step 8: Verifying connector is loaded..."
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector\|db2as400"; then
            echo "✅ AS400 connector plugin is loaded!"
            echo ""
            echo "Connector details:"
            curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" -A 5
            SUCCESS=true
            break
        else
            echo "  ⏳ Connector not loaded yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)..."
            RETRY_COUNT=$((RETRY_COUNT+1))
            sleep 5
        fi
    else
        echo "  ⏳ Kafka Connect not responding yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)..."
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo ""
    echo "⚠️  Could not verify connector loading automatically"
    echo "   Please check manually:"
    echo "   curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo ""
    echo "   Or check Kafka Connect logs:"
    echo "   docker logs $CONTAINER_NAME | tail -50"
else
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! AS400 connector is installed and loaded"
    echo "=================================================================================="
    echo ""
    echo "You can now start your AS400 pipeline:"
    echo "  python3 start_as400_pipeline.py"
    echo ""
fi


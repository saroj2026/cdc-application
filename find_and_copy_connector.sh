#!/bin/bash
# Find and copy Debezium AS400 connector to Kafka Connect container
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "🔍 FINDING AND COPYING DEBEZIUM AS400 CONNECTOR"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"

# Step 1: Search for the connector
echo "Step 1: Searching for debezium-connector-ibmi..."
echo ""

# Search in common locations
SEARCH_PATHS=(
    "/root"
    "/home"
    "/opt"
    "/tmp"
    "/var"
)

echo "Searching in common locations..."
CONNECTOR_PATH=""

for base_path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$base_path" ]; then
        echo "  Searching in: $base_path"
        FOUND=$(find "$base_path" -type d -name "*debezium-connector-ibmi*" 2>/dev/null | head -1)
        if [ -n "$FOUND" ]; then
            CONNECTOR_PATH="$FOUND"
            echo "  ✅ Found: $CONNECTOR_PATH"
            break
        fi
    fi
done

# If still not found, do a broader search
if [ -z "$CONNECTOR_PATH" ]; then
    echo ""
    echo "  Not found in common locations. Searching more broadly..."
    CONNECTOR_PATH=$(find / -type d -name "*debezium-connector-ibmi*" 2>/dev/null | grep -v "/proc\|/sys\|/dev" | head -1)
    if [ -n "$CONNECTOR_PATH" ]; then
        echo "  ✅ Found: $CONNECTOR_PATH"
    fi
fi

# If still not found, ask user
if [ -z "$CONNECTOR_PATH" ]; then
    echo ""
    echo "❌ Connector not found automatically"
    echo ""
    echo "Please provide the full path to the debezium-connector-ibmi folder:"
    echo "  (It should be a folder containing .jar files)"
    echo ""
    read -p "Enter path: " CONNECTOR_PATH
    
    if [ -z "$CONNECTOR_PATH" ] || [ ! -d "$CONNECTOR_PATH" ]; then
        echo "❌ Invalid path or directory does not exist"
        echo ""
        echo "To find it manually, run:"
        echo "  find / -type d -name '*debezium-connector-ibmi*' 2>/dev/null"
        exit 1
    fi
fi

echo ""
echo "Step 2: Verifying connector directory..."
echo "  Path: $CONNECTOR_PATH"

# Check if it's a valid connector directory
JAR_COUNT=$(find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l)
if [ "$JAR_COUNT" -eq 0 ]; then
    echo "⚠️  No JAR files found. This might not be a valid connector."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "  ✅ Found $JAR_COUNT JAR files"
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
echo "Step 4: Copying connector to container..."
CONNECTOR_NAME=$(basename "$CONNECTOR_PATH")
CONTAINER_PATH="/usr/share/java/plugins/$CONNECTOR_NAME"

echo "  From: $CONNECTOR_PATH"
echo "  To: $CONTAINER_NAME:$CONTAINER_PATH"

# Remove existing if present
if docker exec "$CONTAINER_NAME" test -d "$CONTAINER_PATH" 2>/dev/null; then
    echo "  Removing existing connector..."
    docker exec "$CONTAINER_NAME" rm -rf "$CONTAINER_PATH"
fi

# Copy
docker cp "$CONNECTOR_PATH" "$CONTAINER_NAME:$CONTAINER_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Connector copied successfully"
else
    echo "❌ Failed to copy connector"
    exit 1
fi

echo ""
echo "Step 5: Verifying copy..."
CONTAINER_JAR_COUNT=$(docker exec "$CONTAINER_NAME" find "$CONTAINER_PATH" -name "*.jar" 2>/dev/null | wc -l)
if [ "$CONTAINER_JAR_COUNT" -gt 0 ]; then
    echo "✅ Verified: $CONTAINER_JAR_COUNT JAR files in container"
else
    echo "⚠️  No JAR files found in container (but copy succeeded)"
fi

echo ""
echo "Step 6: Restarting Kafka Connect..."
docker restart "$CONTAINER_NAME"
echo "Waiting 30 seconds for restart..."
sleep 30

echo ""
echo "Step 7: Verifying connector is loaded..."
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
    echo "   Check manually: curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo "   Or check logs: docker logs $CONTAINER_NAME | tail -50"
else
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! AS400 connector is installed and loaded"
    echo "=================================================================================="
fi


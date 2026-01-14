#!/bin/bash

# Complete AS400 connector installation
# Run this on the server (72.61.233.209) where the connector was downloaded

set -e

echo "================================================================================
📦 COMPLETING AS400 CONNECTOR INSTALLATION
================================================================================
"

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found!"
    echo "   Available containers:"
    docker ps
    exit 1
fi

echo "   ✅ Found container: $CONTAINER"
echo ""

# Find downloaded connector directory
echo "2. Looking for downloaded connector..."
DOWNLOAD_DIR=""

# Check common download locations
for dir in \
    "$HOME/debezium-connector-ibmi" \
    "/tmp/debezium-connector-ibmi" \
    "/root/debezium-connector-ibmi" \
    "./debezium-connector-ibmi" \
    "$(find /tmp -type d -name 'debezium-connector-ibmi*' 2>/dev/null | head -1)" \
    "$(find $HOME -type d -name 'debezium-connector-ibmi*' 2>/dev/null | head -1)" \
    "$(find . -type d -name 'debezium-connector-ibmi*' 2>/dev/null | head -1)"; do
    
    if [ -d "$dir" ]; then
        DOWNLOAD_DIR="$dir"
        break
    fi
done

if [ -z "$DOWNLOAD_DIR" ]; then
    echo "   ❌ Connector directory not found!"
    echo ""
    echo "   Please provide the path to the connector directory, or"
    echo "   run this script from the directory containing 'debezium-connector-ibmi'"
    echo ""
    echo "   Searching for connector directories..."
    find /tmp /root $HOME -type d -name "*debezium*ibmi*" 2>/dev/null | head -5
    echo ""
    read -p "   Enter connector directory path: " DOWNLOAD_DIR
    
    if [ ! -d "$DOWNLOAD_DIR" ]; then
        echo "   ❌ Directory not found: $DOWNLOAD_DIR"
        exit 1
    fi
fi

echo "   ✅ Found connector directory: $DOWNLOAD_DIR"
echo ""

# Check if directory contains JARs
JAR_COUNT=$(find "$DOWNLOAD_DIR" -name "*.jar" 2>/dev/null | wc -l)
if [ "$JAR_COUNT" -eq 0 ]; then
    echo "   ⚠️  No JAR files found in directory"
    echo "   Listing contents:"
    ls -la "$DOWNLOAD_DIR" | head -10
    echo ""
    echo "   This might be the wrong directory or the connector wasn't extracted properly"
    exit 1
fi

echo "   Found $JAR_COUNT JAR file(s)"
echo ""

# Check if connector already exists in container
echo "3. Checking if connector already exists in container..."
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "   ⚠️  Connector already exists in container"
    read -p "   Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Removing existing connector..."
        docker exec $CONTAINER rm -rf "/kafka/connect/debezium-connector-ibmi"
    else
        echo "   Installation cancelled"
        exit 0
    fi
fi

# Copy connector to container
echo ""
echo "4. Copying connector to Kafka Connect container..."
docker cp "$DOWNLOAD_DIR" "$CONTAINER:/kafka/connect/debezium-connector-ibmi"

# Verify copy
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "   ✅ Connector copied successfully"
    
    # List some JARs
    echo "   Installed JARs:"
    docker exec $CONTAINER ls -1 "/kafka/connect/debezium-connector-ibmi"/*.jar 2>/dev/null | head -5 | while read jar; do
        echo "      - $(basename $jar)"
    done
    INSTALLED_COUNT=$(docker exec $CONTAINER ls -1 "/kafka/connect/debezium-connector-ibmi"/*.jar 2>/dev/null | wc -l)
    echo "      ... (Total: $INSTALLED_COUNT JARs)"
else
    echo "   ❌ Failed to copy connector"
    exit 1
fi

# Restart Kafka Connect
echo ""
echo "5. Restarting Kafka Connect container..."
docker restart $CONTAINER

# Wait for restart
echo "   Waiting 30 seconds for Kafka Connect to restart..."
sleep 30

# Verify installation
echo ""
echo "6. Verifying installation..."
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector\|db2as400"; then
            echo "   ✅ AS400 Connector is installed and available!"
            echo ""
            echo "   Available AS400 connector:"
            curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400"
            SUCCESS=true
            break
        else
            echo "   ⚠️  Kafka Connect is running but AS400 connector not found yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
            RETRY_COUNT=$((RETRY_COUNT+1))
            sleep 5
        fi
    else
        echo "   ⚠️  Kafka Connect not responding yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "   ⚠️  Could not verify installation automatically"
    echo "   Please check manually:"
    echo "   curl http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo ""
    echo "   Or check container logs:"
    echo "   docker logs $CONTAINER | tail -50"
fi

echo ""
echo "================================================================================
✅ INSTALLATION COMPLETE
================================================================================
"
echo "Next steps:"
echo "1. Verify connector is available:"
echo "   curl http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
echo ""
echo "2. Restart your backend application"
echo ""
echo "3. Try starting your AS400 pipeline again"
echo ""



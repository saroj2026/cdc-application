#!/bin/bash

# Script to install Debezium AS400 connector on remote Kafka Connect Docker container
# Run this on the server: 72.61.233.209
# SSH: ssh root@72.61.233.209

set -e

echo "================================================================================
📦 INSTALLING DEBEZIUM AS400 CONNECTOR ON KAFKA CONNECT
================================================================================
"

# Configuration
DEBEZIUM_IBM_VERSION="2.6.0.Beta1"
KAFKA_CONNECT_URL="http://localhost:8083"
CONNECTOR_NAME="debezium-connector-ibmi"

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep -i connect | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "   ❌ Kafka Connect container not found"
    echo "   Available containers:"
    docker ps --format "{{.Names}}"
    exit 1
fi

echo "   ✅ Found container: $CONTAINER_NAME"

# Check if connector already exists
echo ""
echo "2. Checking if connector already exists..."
if docker exec $CONTAINER_NAME test -d "/kafka/connect/$CONNECTOR_NAME" 2>/dev/null; then
    echo "   ⚠️  Connector directory already exists"
    read -p "   Do you want to reinstall? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Installation cancelled"
        exit 0
    fi
    echo "   Removing existing connector..."
    docker exec $CONTAINER_NAME rm -rf "/kafka/connect/$CONNECTOR_NAME"
fi

# Download connector
echo ""
echo "3. Downloading Debezium AS400 Connector..."
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-ibmi/${DEBEZIUM_IBM_VERSION}/debezium-connector-ibmi-${DEBEZIUM_IBM_VERSION}-plugin.tar.gz"

echo "   Downloading from: $DOWNLOAD_URL"
FILENAME="debezium-connector-ibmi-${DEBEZIUM_IBM_VERSION}-plugin.tar.gz"

if ! wget -q --show-progress "$DOWNLOAD_URL" -O "$FILENAME" 2>/dev/null; then
    echo "   Trying alternative download method (curl)..."
    if ! curl -L -f -o "$FILENAME" "$DOWNLOAD_URL" 2>/dev/null; then
        echo "   ❌ Failed to download connector"
        echo "   URL: $DOWNLOAD_URL"
        echo "   Please check:"
        echo "   1. Internet connectivity"
        echo "   2. Maven repository accessibility"
        exit 1
    fi
fi

echo "   ✅ Download complete"

# Extract
echo "   Extracting connector..."
tar -xzf "$FILENAME"

# Find extracted directory
EXTRACTED_DIR=$(ls -d debezium-connector-ibmi-*plugin 2>/dev/null | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    EXTRACTED_DIR=$(ls -d debezium-connector-*plugin 2>/dev/null | head -1)
fi

if [ -z "$EXTRACTED_DIR" ]; then
    echo "   ❌ Could not find extracted connector directory"
    echo "   Files in directory:"
    ls -la
    exit 1
fi

echo "   ✅ Extracted to: $EXTRACTED_DIR"

# Copy to container
echo ""
echo "4. Installing connector to Kafka Connect container..."
docker cp "$EXTRACTED_DIR" "$CONTAINER_NAME:/kafka/connect/$CONNECTOR_NAME"

# Verify files were copied
if docker exec $CONTAINER_NAME test -d "/kafka/connect/$CONNECTOR_NAME" 2>/dev/null; then
    echo "   ✅ Connector files copied successfully"
    
    # List JARs
    echo "   Installed JARs:"
    docker exec $CONTAINER_NAME ls -1 "/kafka/connect/$CONNECTOR_NAME"/*.jar 2>/dev/null | head -10 | while read jar; do
        echo "      - $(basename $jar)"
    done
    JAR_COUNT=$(docker exec $CONTAINER_NAME ls -1 "/kafka/connect/$CONNECTOR_NAME"/*.jar 2>/dev/null | wc -l)
    echo "      ... (Total: $JAR_COUNT JARs)"
else
    echo "   ❌ Failed to copy connector files"
    exit 1
fi

# Restart Kafka Connect
echo ""
echo "5. Restarting Kafka Connect container..."
docker restart $CONTAINER_NAME

# Wait for Kafka Connect to start
echo "   Waiting for Kafka Connect to start (30 seconds)..."
sleep 30

# Verify installation
echo ""
echo "6. Verifying installation..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s "$KAFKA_CONNECT_URL/connector-plugins" > /dev/null 2>&1; then
        # Check if AS400 connector is available
        if curl -s "$KAFKA_CONNECT_URL/connector-plugins" | grep -qi "As400RpcConnector\|db2as400"; then
            echo "   ✅ Debezium AS400 Connector is installed and available!"
            echo ""
            echo "   Available AS400 connector:"
            curl -s "$KAFKA_CONNECT_URL/connector-plugins" | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            curl -s "$KAFKA_CONNECT_URL/connector-plugins" | grep -i "As400RpcConnector\|db2as400"
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

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "   ⚠️  Could not verify installation (Kafka Connect may still be starting)"
    echo "   Please check manually:"
    echo "   curl $KAFKA_CONNECT_URL/connector-plugins | grep -i As400RpcConnector"
fi

# Cleanup
echo ""
echo "7. Cleaning up temporary files..."
rm -rf $TEMP_DIR

echo ""
echo "================================================================================
✅ INSTALLATION COMPLETE
================================================================================
"
echo "Next steps:"
echo "1. Verify connector is available:"
echo "   curl $KAFKA_CONNECT_URL/connector-plugins | grep -i As400RpcConnector"
echo ""
echo "2. Restart your backend application"
echo ""
echo "3. Try starting your AS400 pipeline again"
echo ""


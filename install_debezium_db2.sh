#!/bin/bash

# Script to install Debezium Db2 Connector for AS400/IBM i CDC
# Run this on the server where Kafka Connect is running

set -e

echo "================================================================================
📦 INSTALLING DEBEZIUM DB2 CONNECTOR FOR AS400/IBM i
================================================================================

NOTE: The Debezium Db2 connector (io.debezium.connector.db2.Db2Connector)
      is the connector used for IBM i/AS400 systems. There is no separate
      'IBM i connector' - the Db2 connector is configured with IBM i-specific
      parameters to work with AS400.

================================================================================
"

# Configuration
# AS400 connector was introduced in 2.6.0.Beta1 as debezium-connector-ibmi
DEBEZIUM_IBM_VERSION="2.6.0.Beta1"
KAFKA_CONNECT_URL="http://localhost:8083"
CONNECTOR_NAME="debezium-connector-ibmi"

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep -i connect | head -1)

if [ -z "$CONTAINER_NAME" ]; then
    echo "   ❌ Kafka Connect container not found"
    echo "   Please ensure Kafka Connect is running"
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
echo "3. Downloading Debezium Db2 Connector..."
TEMP_DIR=$(mktemp -d)
cd $TEMP_DIR

# Download AS400-specific connector
# AS400 connector is available as debezium-connector-ibmi (version 2.6.0.Beta1+)
DOWNLOAD_URL_IBMI="https://repo1.maven.org/maven2/io/debezium/debezium-connector-ibmi/${DEBEZIUM_IBM_VERSION}/debezium-connector-ibmi-${DEBEZIUM_IBM_VERSION}-plugin.tar.gz"

# Download IBM i connector (debezium-connector-ibmi)
echo "   Downloading IBM i connector (version ${DEBEZIUM_IBM_VERSION})..."
FILENAME="debezium-connector-ibmi-${DEBEZIUM_IBM_VERSION}-plugin.tar.gz"

if ! wget -q --show-progress "$DOWNLOAD_URL_IBMI" -O "$FILENAME" 2>/dev/null; then
    echo "   Trying alternative download method..."
    if ! curl -L -f -o "$FILENAME" "$DOWNLOAD_URL_IBMI" 2>/dev/null; then
        echo "   ❌ Failed to download connector"
        echo "   URL: $DOWNLOAD_URL_IBMI"
        echo "   Please check:"
        echo "   1. Internet connectivity"
        echo "   2. Maven repository accessibility"
        echo "   3. Connector version availability (2.6.0.Beta1+)"
        exit 1
    fi
fi

# Extract
echo "   Extracting connector..."
tar -xzf "$FILENAME"

# Copy to container
echo ""
echo "4. Installing connector to Kafka Connect..."
# Find extracted directory (should be debezium-connector-ibmi-*)
EXTRACTED_DIR=$(ls -d debezium-connector-ibmi-*plugin 2>/dev/null | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    # Try alternative naming
    EXTRACTED_DIR=$(ls -d debezium-connector-*plugin 2>/dev/null | head -1)
fi
if [ -z "$EXTRACTED_DIR" ]; then
    echo "   ❌ Could not find extracted connector directory"
    echo "   Extracted files:"
    ls -la
    exit 1
fi
echo "   Found connector directory: $EXTRACTED_DIR"
# Copy to container with a consistent name
docker cp "$EXTRACTED_DIR" "$CONTAINER_NAME:/kafka/connect/debezium-connector-ibmi"

# Verify files were copied
if docker exec $CONTAINER_NAME test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "   ✅ Connector files copied successfully"
    
    # List JARs
    echo "   Installed JARs:"
    docker exec $CONTAINER_NAME ls -1 "/kafka/connect/debezium-connector-ibmi"/*.jar 2>/dev/null | head -5 | while read jar; do
        echo "      - $(basename $jar)"
    done
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
        # Check if Db2 connector is available
        if curl -s "$KAFKA_CONNECT_URL/connector-plugins" | grep -qi "As400RpcConnector\|db2as400"; then
            echo "   ✅ Debezium AS400 Connector is installed and available!"
            echo ""
            echo "   Available AS400 connector:"
            curl -s "$KAFKA_CONNECT_URL/connector-plugins" | python3 -m json.tool 2>/dev/null | grep -A 5 -i "As400RpcConnector\|db2as400" || \
            curl -s "$KAFKA_CONNECT_URL/connector-plugins" | grep -i "As400RpcConnector\|db2as400"
            break
        else
            echo "   ⚠️  Kafka Connect is running but Db2 connector not found yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
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
    echo "   Please check manually: curl $KAFKA_CONNECT_URL/connector-plugins | grep -i db2"
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
echo "   curl $KAFKA_CONNECT_URL/connector-plugins | grep -i db2"
echo ""
echo "2. Try starting your AS400 pipeline again"
echo ""
echo "3. If issues persist, check Kafka Connect logs:"
echo "   docker logs $CONTAINER_NAME"
echo ""


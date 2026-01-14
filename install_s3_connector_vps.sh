#!/bin/bash
# Install S3 Connector to Kafka Connect on VPS Server
# Run this script on the VPS server (72.61.233.209)

echo "=========================================="
echo "S3 Connector Installation for VPS"
echo "=========================================="

# Configuration
KAFKA_CONNECT_CONTAINER="kafka-connect-cdc"
CONNECTOR_SOURCE_DIR="/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib"
KAFKA_CONNECT_PLUGIN_PATH="/kafka/connect"

# Check if running on VPS
echo ""
echo "1. Checking environment..."
if [ ! -d "$CONNECTOR_SOURCE_DIR" ]; then
    echo "   ⚠️  Connector directory not found at: $CONNECTOR_SOURCE_DIR"
    echo "   Looking for connector files..."
    
    # Try to find the connector directory
    if [ -d "/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8" ]; then
        echo "   ✅ Found connector directory"
        CONNECTOR_SOURCE_DIR=$(find /opt/cdc3/confluentinc-kafka-connect-s3-11.0.8 -type d -name "lib" | head -1)
        if [ -z "$CONNECTOR_SOURCE_DIR" ]; then
            echo "   ❌ Could not find lib directory in connector package"
            echo "   Please ensure the connector is extracted in /opt/cdc3/"
            exit 1
        fi
        echo "   Using: $CONNECTOR_SOURCE_DIR"
    else
        echo "   ❌ Connector directory not found"
        echo "   Please extract the connector to /opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/"
        exit 1
    fi
else
    echo "   ✅ Connector directory found: $CONNECTOR_SOURCE_DIR"
fi

# Check if container exists
echo ""
echo "2. Checking Kafka Connect container..."
if ! docker ps -a | grep -q "$KAFKA_CONNECT_CONTAINER"; then
    echo "   ❌ Container '$KAFKA_CONNECT_CONTAINER' not found"
    echo "   Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo "   ✅ Container found: $KAFKA_CONNECT_CONTAINER"

# Check container status
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$KAFKA_CONNECT_CONTAINER" 2>/dev/null)
echo "   Container status: $CONTAINER_STATUS"

# Count JAR files
JAR_COUNT=$(find "$CONNECTOR_SOURCE_DIR" -name "*.jar" 2>/dev/null | wc -l)
echo ""
echo "3. Found $JAR_COUNT JAR files to copy"

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "   ❌ No JAR files found in $CONNECTOR_SOURCE_DIR"
    exit 1
fi

# Copy JAR files
echo ""
echo "4. Copying JAR files to Kafka Connect container..."
echo "   Source: $CONNECTOR_SOURCE_DIR"
echo "   Target: $KAFKA_CONNECT_CONTAINER:$KAFKA_CONNECT_PLUGIN_PATH"

docker cp "$CONNECTOR_SOURCE_DIR"/. "$KAFKA_CONNECT_CONTAINER:$KAFKA_CONNECT_PLUGIN_PATH"

if [ $? -eq 0 ]; then
    echo "   ✅ JAR files copied successfully"
else
    echo "   ❌ Failed to copy JAR files"
    echo "   Make sure:"
    echo "     1. Docker is running"
    echo "     2. You have permission to copy files"
    echo "     3. Container is accessible"
    exit 1
fi

# Verify files were copied
echo ""
echo "5. Verifying files in container..."
COPIED_COUNT=$(docker exec "$KAFKA_CONNECT_CONTAINER" ls -1 "$KAFKA_CONNECT_PLUGIN_PATH"/*.jar 2>/dev/null | wc -l)
echo "   Found $COPIED_COUNT JAR files in container"

# Restart container
echo ""
echo "6. Restarting Kafka Connect container..."
docker restart "$KAFKA_CONNECT_CONTAINER"

if [ $? -eq 0 ]; then
    echo "   ✅ Container restarted"
else
    echo "   ❌ Failed to restart container"
    exit 1
fi

# Wait for restart
echo ""
echo "7. Waiting for Kafka Connect to start (60 seconds)..."
sleep 60

# Verify installation
echo ""
echo "8. Verifying S3 connector installation..."
KAFKA_CONNECT_URL="http://localhost:8083"
response=$(curl -s "$KAFKA_CONNECT_URL/connector-plugins" 2>/dev/null | grep -i "S3SinkConnector")

if [ -n "$response" ]; then
    echo "   ✅ S3 Sink Connector is installed!"
    echo ""
    echo "   Connector details:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "   ⚠️  S3 connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo ""
    echo "   Checking connector-plugins list..."
    curl -s "$KAFKA_CONNECT_URL/connector-plugins" | python3 -m json.tool 2>/dev/null | grep -i "s3\|class" || echo "   Could not parse response"
    echo ""
    echo "   Check logs: docker logs $KAFKA_CONNECT_CONTAINER | tail -50"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl $KAFKA_CONNECT_URL/connector-plugins | grep -i s3"
echo "2. Create/start a CDC pipeline with S3 target"
echo "3. Monitor connector status via API"
echo ""
echo "If connector is not found, check logs:"
echo "   docker logs $KAFKA_CONNECT_CONTAINER | tail -100"

# Install S3 Connector to Kafka Connect on VPS Server
# Run this script on the VPS server (72.61.233.209)

echo "=========================================="
echo "S3 Connector Installation for VPS"
echo "=========================================="

# Configuration
KAFKA_CONNECT_CONTAINER="kafka-connect-cdc"
CONNECTOR_SOURCE_DIR="/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib"
KAFKA_CONNECT_PLUGIN_PATH="/kafka/connect"

# Check if running on VPS
echo ""
echo "1. Checking environment..."
if [ ! -d "$CONNECTOR_SOURCE_DIR" ]; then
    echo "   ⚠️  Connector directory not found at: $CONNECTOR_SOURCE_DIR"
    echo "   Looking for connector files..."
    
    # Try to find the connector directory
    if [ -d "/opt/cdc3/confluentinc-kafka-connect-s3-11.0.8" ]; then
        echo "   ✅ Found connector directory"
        CONNECTOR_SOURCE_DIR=$(find /opt/cdc3/confluentinc-kafka-connect-s3-11.0.8 -type d -name "lib" | head -1)
        if [ -z "$CONNECTOR_SOURCE_DIR" ]; then
            echo "   ❌ Could not find lib directory in connector package"
            echo "   Please ensure the connector is extracted in /opt/cdc3/"
            exit 1
        fi
        echo "   Using: $CONNECTOR_SOURCE_DIR"
    else
        echo "   ❌ Connector directory not found"
        echo "   Please extract the connector to /opt/cdc3/confluentinc-kafka-connect-s3-11.0.8/"
        exit 1
    fi
else
    echo "   ✅ Connector directory found: $CONNECTOR_SOURCE_DIR"
fi

# Check if container exists
echo ""
echo "2. Checking Kafka Connect container..."
if ! docker ps -a | grep -q "$KAFKA_CONNECT_CONTAINER"; then
    echo "   ❌ Container '$KAFKA_CONNECT_CONTAINER' not found"
    echo "   Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

echo "   ✅ Container found: $KAFKA_CONNECT_CONTAINER"

# Check container status
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$KAFKA_CONNECT_CONTAINER" 2>/dev/null)
echo "   Container status: $CONTAINER_STATUS"

# Count JAR files
JAR_COUNT=$(find "$CONNECTOR_SOURCE_DIR" -name "*.jar" 2>/dev/null | wc -l)
echo ""
echo "3. Found $JAR_COUNT JAR files to copy"

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "   ❌ No JAR files found in $CONNECTOR_SOURCE_DIR"
    exit 1
fi

# Copy JAR files
echo ""
echo "4. Copying JAR files to Kafka Connect container..."
echo "   Source: $CONNECTOR_SOURCE_DIR"
echo "   Target: $KAFKA_CONNECT_CONTAINER:$KAFKA_CONNECT_PLUGIN_PATH"

docker cp "$CONNECTOR_SOURCE_DIR"/. "$KAFKA_CONNECT_CONTAINER:$KAFKA_CONNECT_PLUGIN_PATH"

if [ $? -eq 0 ]; then
    echo "   ✅ JAR files copied successfully"
else
    echo "   ❌ Failed to copy JAR files"
    echo "   Make sure:"
    echo "     1. Docker is running"
    echo "     2. You have permission to copy files"
    echo "     3. Container is accessible"
    exit 1
fi

# Verify files were copied
echo ""
echo "5. Verifying files in container..."
COPIED_COUNT=$(docker exec "$KAFKA_CONNECT_CONTAINER" ls -1 "$KAFKA_CONNECT_PLUGIN_PATH"/*.jar 2>/dev/null | wc -l)
echo "   Found $COPIED_COUNT JAR files in container"

# Restart container
echo ""
echo "6. Restarting Kafka Connect container..."
docker restart "$KAFKA_CONNECT_CONTAINER"

if [ $? -eq 0 ]; then
    echo "   ✅ Container restarted"
else
    echo "   ❌ Failed to restart container"
    exit 1
fi

# Wait for restart
echo ""
echo "7. Waiting for Kafka Connect to start (60 seconds)..."
sleep 60

# Verify installation
echo ""
echo "8. Verifying S3 connector installation..."
KAFKA_CONNECT_URL="http://localhost:8083"
response=$(curl -s "$KAFKA_CONNECT_URL/connector-plugins" 2>/dev/null | grep -i "S3SinkConnector")

if [ -n "$response" ]; then
    echo "   ✅ S3 Sink Connector is installed!"
    echo ""
    echo "   Connector details:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "   ⚠️  S3 connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo ""
    echo "   Checking connector-plugins list..."
    curl -s "$KAFKA_CONNECT_URL/connector-plugins" | python3 -m json.tool 2>/dev/null | grep -i "s3\|class" || echo "   Could not parse response"
    echo ""
    echo "   Check logs: docker logs $KAFKA_CONNECT_CONTAINER | tail -50"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl $KAFKA_CONNECT_URL/connector-plugins | grep -i s3"
echo "2. Create/start a CDC pipeline with S3 target"
echo "3. Monitor connector status via API"
echo ""
echo "If connector is not found, check logs:"
echo "   docker logs $KAFKA_CONNECT_CONTAINER | tail -100"


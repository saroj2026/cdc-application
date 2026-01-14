#!/bin/bash
# Script to install S3 connector to Kafka Connect on VPS server

VPS_SERVER="72.61.233.209"
CONNECTOR_DIR="confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib"
KAFKA_CONNECT_CONTAINER="kafka-connect-cdc"

echo "=========================================="
echo "Installing S3 Connector to Kafka Connect"
echo "=========================================="

# Check if connector directory exists
if [ ! -d "$CONNECTOR_DIR" ]; then
    echo "❌ Error: Connector directory not found: $CONNECTOR_DIR"
    exit 1
fi

echo ""
echo "1. Copying connector JAR files to Kafka Connect container..."
echo "   Container: $KAFKA_CONNECT_CONTAINER"
echo "   Source: $CONNECTOR_DIR"
echo ""

# Copy all JAR files to Kafka Connect
docker cp "$CONNECTOR_DIR"/. "$KAFKA_CONNECT_CONTAINER:/kafka/connect/"

if [ $? -eq 0 ]; then
    echo "   ✅ JAR files copied successfully"
else
    echo "   ❌ Failed to copy JAR files"
    echo "   Make sure:"
    echo "     1. Docker is running"
    echo "     2. Container '$KAFKA_CONNECT_CONTAINER' exists"
    echo "     3. You have permission to copy files"
    exit 1
fi

echo ""
echo "2. Restarting Kafka Connect container..."
docker restart "$KAFKA_CONNECT_CONTAINER"

if [ $? -eq 0 ]; then
    echo "   ✅ Container restarted"
else
    echo "   ❌ Failed to restart container"
    exit 1
fi

echo ""
echo "3. Waiting for Kafka Connect to start (30 seconds)..."
sleep 30

echo ""
echo "4. Verifying S3 connector installation..."
response=$(curl -s http://$VPS_SERVER:8083/connector-plugins | grep -i "S3SinkConnector")

if [ -n "$response" ]; then
    echo "   ✅ S3 Sink Connector is installed!"
    echo ""
    echo "   Available connector:"
    echo "$response"
else
    echo "   ⚠️  S3 connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo "   Check logs: docker logs $KAFKA_CONNECT_CONTAINER"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl http://$VPS_SERVER:8083/connector-plugins | grep -i s3"
echo "2. Create/start a CDC pipeline with S3 target"
echo "3. Monitor connector status via API"

# Script to install S3 connector to Kafka Connect on VPS server

VPS_SERVER="72.61.233.209"
CONNECTOR_DIR="confluentinc-kafka-connect-s3-11.0.8/confluentinc-kafka-connect-s3-11.0.8/lib"
KAFKA_CONNECT_CONTAINER="kafka-connect-cdc"

echo "=========================================="
echo "Installing S3 Connector to Kafka Connect"
echo "=========================================="

# Check if connector directory exists
if [ ! -d "$CONNECTOR_DIR" ]; then
    echo "❌ Error: Connector directory not found: $CONNECTOR_DIR"
    exit 1
fi

echo ""
echo "1. Copying connector JAR files to Kafka Connect container..."
echo "   Container: $KAFKA_CONNECT_CONTAINER"
echo "   Source: $CONNECTOR_DIR"
echo ""

# Copy all JAR files to Kafka Connect
docker cp "$CONNECTOR_DIR"/. "$KAFKA_CONNECT_CONTAINER:/kafka/connect/"

if [ $? -eq 0 ]; then
    echo "   ✅ JAR files copied successfully"
else
    echo "   ❌ Failed to copy JAR files"
    echo "   Make sure:"
    echo "     1. Docker is running"
    echo "     2. Container '$KAFKA_CONNECT_CONTAINER' exists"
    echo "     3. You have permission to copy files"
    exit 1
fi

echo ""
echo "2. Restarting Kafka Connect container..."
docker restart "$KAFKA_CONNECT_CONTAINER"

if [ $? -eq 0 ]; then
    echo "   ✅ Container restarted"
else
    echo "   ❌ Failed to restart container"
    exit 1
fi

echo ""
echo "3. Waiting for Kafka Connect to start (30 seconds)..."
sleep 30

echo ""
echo "4. Verifying S3 connector installation..."
response=$(curl -s http://$VPS_SERVER:8083/connector-plugins | grep -i "S3SinkConnector")

if [ -n "$response" ]; then
    echo "   ✅ S3 Sink Connector is installed!"
    echo ""
    echo "   Available connector:"
    echo "$response"
else
    echo "   ⚠️  S3 connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo "   Check logs: docker logs $KAFKA_CONNECT_CONTAINER"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl http://$VPS_SERVER:8083/connector-plugins | grep -i s3"
echo "2. Create/start a CDC pipeline with S3 target"
echo "3. Monitor connector status via API"


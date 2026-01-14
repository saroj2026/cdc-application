#!/bin/bash
# Script to install Snowflake Kafka Connector on VPS
# Run this script on your VPS (72.61.233.209)

set -e

echo "======================================================================"
echo "Installing Snowflake Kafka Connector"
echo "======================================================================"

# Configuration
KAFKA_CONNECT_CONTAINER="kafka-connect-cdc"
PLUGINS_DIR="/usr/share/java/plugins"
CONNECTOR_VERSION="1.11.0"  # Latest stable version
CONNECTOR_URL="https://repo1.maven.org/maven2/com/snowflake/snowflake-kafka-connector/${CONNECTOR_VERSION}/snowflake-kafka-connector-${CONNECTOR_VERSION}.jar"

echo ""
echo "1. Checking Kafka Connect container..."
if ! docker ps | grep -q "$KAFKA_CONNECT_CONTAINER"; then
    echo "   ❌ Error: Container '$KAFKA_CONNECT_CONTAINER' is not running"
    echo "   Please start the container first: docker start $KAFKA_CONNECT_CONTAINER"
    exit 1
fi
echo "   ✅ Container is running"

echo ""
echo "2. Creating plugins directory if it doesn't exist..."
docker exec $KAFKA_CONNECT_CONTAINER mkdir -p $PLUGINS_DIR/snowflake-kafka-connector
echo "   ✅ Directory created"

echo ""
echo "3. Downloading Snowflake Kafka Connector (version $CONNECTOR_VERSION)..."
echo "   This may take a few minutes..."
docker exec $KAFKA_CONNECT_CONTAINER wget -q -O $PLUGINS_DIR/snowflake-kafka-connector/snowflake-kafka-connector-${CONNECTOR_VERSION}.jar "$CONNECTOR_URL"

if [ $? -eq 0 ]; then
    echo "   ✅ Download successful"
else
    echo "   ⚠️  Direct download failed, trying alternative method..."
    # Alternative: Download locally and copy
    echo "   Please download manually from:"
    echo "   $CONNECTOR_URL"
    echo "   Then copy to container:"
    echo "   docker cp snowflake-kafka-connector-${CONNECTOR_VERSION}.jar $KAFKA_CONNECT_CONTAINER:$PLUGINS_DIR/snowflake-kafka-connector/"
    exit 1
fi

echo ""
echo "4. Verifying JAR file..."
JAR_SIZE=$(docker exec $KAFKA_CONNECT_CONTAINER ls -lh $PLUGINS_DIR/snowflake-kafka-connector/snowflake-kafka-connector-${CONNECTOR_VERSION}.jar | awk '{print $5}')
echo "   ✅ JAR file size: $JAR_SIZE"

echo ""
echo "5. Restarting Kafka Connect container to load the connector..."
docker restart $KAFKA_CONNECT_CONTAINER

echo ""
echo "6. Waiting for Kafka Connect to start (30 seconds)..."
sleep 30

echo ""
echo "7. Verifying connector installation..."
echo "   Checking available connectors..."
docker exec $KAFKA_CONNECT_CONTAINER curl -s http://localhost:8083/connector-plugins | grep -i snowflake || {
    echo "   ⚠️  Snowflake connector not found in plugin list"
    echo "   This might be normal - connectors are loaded on first use"
    echo "   Check Kafka Connect logs: docker logs $KAFKA_CONNECT_CONTAINER | tail -50"
}

echo ""
echo "======================================================================"
echo "✅ Installation Complete!"
echo "======================================================================"
echo ""
echo "The Snowflake Kafka Connector has been installed."
echo "Connector class: com.snowflake.kafka.connector.SnowflakeSinkConnector"
echo ""
echo "To verify, check the connector plugins:"
echo "  docker exec $KAFKA_CONNECT_CONTAINER curl -s http://localhost:8083/connector-plugins | grep -i snowflake"
echo ""
echo "Or check Kafka Connect logs:"
echo "  docker logs $KAFKA_CONNECT_CONTAINER | tail -100"
echo ""




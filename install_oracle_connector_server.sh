#!/bin/bash
# Run this script directly on the server (72.61.233.209)
# Install Debezium Oracle Connector in Kafka Connect container

set -e

CONTAINER_ID="28b9a11e27bb"
PLUGINS_DIR="/usr/share/confluent-hub-components"
DEBEZIUM_VERSION="2.5.0.Final"
CONNECTOR_NAME="debezium-connector-oracle"

echo "======================================================================"
echo "Installing Debezium Oracle Connector"
echo "======================================================================"
echo "Container: $CONTAINER_ID"
echo "Plugins Directory: $PLUGINS_DIR"
echo ""

# Step 1: Check if container is running
echo "1. Checking Kafka Connect container..."
if ! docker ps | grep -q "$CONTAINER_ID"; then
    echo "   ❌ Container $CONTAINER_ID is not running"
    exit 1
fi
echo "   ✅ Container is running"

# Step 2: Find plugins directory
echo ""
echo "2. Finding plugins directory..."
PLUGINS_PATH=$(docker exec $CONTAINER_ID find / -name "debezium-connector-postgresql*" -type d 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo "$PLUGINS_DIR")
echo "   Using: $PLUGINS_PATH"

# Step 3: Create connector directory
echo ""
echo "3. Creating connector directory..."
docker exec $CONTAINER_ID bash -c "mkdir -p $PLUGINS_PATH/$CONNECTOR_NAME"
echo "   ✅ Directory created"

# Step 4: Download and extract connector
echo ""
echo "4. Downloading Debezium Oracle Connector ($DEBEZIUM_VERSION)..."
docker exec $CONTAINER_ID bash -c "
    cd $PLUGINS_PATH/$CONNECTOR_NAME && \
    wget -q https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/$DEBEZIUM_VERSION/debezium-connector-oracle-${DEBEZIUM_VERSION}-plugin.tar.gz && \
    tar -xzf debezium-connector-oracle-${DEBEZIUM_VERSION}-plugin.tar.gz && \
    rm debezium-connector-oracle-${DEBEZIUM_VERSION}-plugin.tar.gz && \
    echo 'Download and extraction complete'
"
echo "   ✅ Connector downloaded and extracted"

# Step 5: Verify installation
echo ""
echo "5. Verifying installation..."
JAR_COUNT=$(docker exec $CONTAINER_ID bash -c "ls -1 $PLUGINS_PATH/$CONNECTOR_NAME/*.jar 2>/dev/null | wc -l" | tr -d ' ')
echo "   Found $JAR_COUNT JAR file(s)"
if [ "$JAR_COUNT" -gt 0 ]; then
    echo "   ✅ Installation verified"
    docker exec $CONTAINER_ID bash -c "ls -lh $PLUGINS_PATH/$CONNECTOR_NAME/*.jar | head -5"
else
    echo "   ⚠️  No JAR files found"
fi

# Step 6: Restart container
echo ""
echo "6. Restarting Kafka Connect container..."
docker restart $CONTAINER_ID
echo "   ✅ Container restarted"

# Step 7: Wait for container to be ready
echo ""
echo "7. Waiting for Kafka Connect to be ready..."
sleep 15
for i in {1..30}; do
    if docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        echo "   ✅ Kafka Connect is ready"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Step 8: Verify connector is available
echo ""
echo "8. Verifying Oracle connector is available..."
ORACLE_PLUGINS=$(docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins | grep -i oracle | wc -l | tr -d ' ')
if [ "$ORACLE_PLUGINS" -gt 0 ]; then
    echo "   ✅ Oracle connector is available!"
    docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins | grep -i oracle
else
    echo "   ⚠️  Oracle connector not found in plugins list"
    echo "   Checking logs..."
    docker logs $CONTAINER_ID --tail 50 | grep -i oracle || echo "   No Oracle-related logs found"
fi

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Verify connector: curl http://72.61.233.209:8083/connector-plugins | grep -i oracle"
echo "2. Test Oracle connection via API/UI"
echo "3. Create Oracle → Snowflake pipeline"


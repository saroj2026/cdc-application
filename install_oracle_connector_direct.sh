#!/bin/bash
# Direct installation script - run this ON THE SERVER (72.61.233.209)
# This script installs Debezium Oracle Connector in Kafka Connect container

set -e

CONTAINER_ID="28b9a11e27bb"
DEBEZIUM_VERSION="2.5.0.Final"
CONNECTOR_NAME="debezium-connector-oracle"

echo "======================================================================"
echo "Installing Debezium Oracle Connector"
echo "Container: $CONTAINER_ID"
echo "Version: $DEBEZIUM_VERSION"
echo "======================================================================"

# Step 1: Check container
echo ""
echo "1. Checking Kafka Connect container..."
if ! docker ps | grep -q "$CONTAINER_ID"; then
    echo "   ❌ Container $CONTAINER_ID is not running"
    echo "   Available containers:"
    docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
    exit 1
fi
echo "   ✅ Container is running"

# Step 2: Find plugins directory by checking existing Debezium connector
echo ""
echo "2. Finding plugins directory..."
PLUGINS_DIR=$(docker exec $CONTAINER_ID find / -name "debezium-connector-postgresql*" -type d 2>/dev/null | head -1 | xargs dirname 2>/dev/null)
if [ -z "$PLUGINS_DIR" ]; then
    # Try common locations
    for dir in "/usr/share/confluent-hub-components" "/usr/local/share/kafka/plugins" "/opt/kafka/plugins"; do
        if docker exec $CONTAINER_ID test -d "$dir" 2>/dev/null; then
            PLUGINS_DIR="$dir"
            break
        fi
    done
fi

if [ -z "$PLUGINS_DIR" ]; then
    echo "   ❌ Could not find plugins directory"
    echo "   Checking common locations..."
    docker exec $CONTAINER_ID ls -la /usr/share/confluent-hub-components 2>/dev/null || echo "   Not found"
    exit 1
fi

echo "   ✅ Found plugins directory: $PLUGINS_DIR"

# Step 3: Create connector directory
echo ""
echo "3. Creating connector directory..."
docker exec $CONTAINER_ID bash -c "mkdir -p $PLUGINS_DIR/$CONNECTOR_NAME"
echo "   ✅ Directory created: $PLUGINS_DIR/$CONNECTOR_NAME"

# Step 4: Download connector
echo ""
echo "4. Downloading Debezium Oracle Connector..."
DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/$DEBEZIUM_VERSION/debezium-connector-oracle-${DEBEZIUM_VERSION}-plugin.tar.gz"
echo "   URL: $DOWNLOAD_URL"

docker exec $CONTAINER_ID bash -c "
    cd $PLUGINS_DIR/$CONNECTOR_NAME && \
    if command -v wget > /dev/null; then
        wget -q --show-progress $DOWNLOAD_URL -O connector.tar.gz
    elif command -v curl > /dev/null; then
        curl -L -o connector.tar.gz $DOWNLOAD_URL
    else
        echo 'Error: Neither wget nor curl is available'
        exit 1
    fi
"

if [ $? -ne 0 ]; then
    echo "   ❌ Download failed"
    exit 1
fi
echo "   ✅ Download complete"

# Step 5: Extract
echo ""
echo "5. Extracting connector files..."
docker exec $CONTAINER_ID bash -c "
    cd $PLUGINS_DIR/$CONNECTOR_NAME && \
    tar -xzf connector.tar.gz && \
    rm connector.tar.gz && \
    echo 'Extraction complete'
"
echo "   ✅ Files extracted"

# Step 6: Verify installation
echo ""
echo "6. Verifying installation..."
JAR_FILES=$(docker exec $CONTAINER_ID bash -c "ls -1 $PLUGINS_DIR/$CONNECTOR_NAME/*.jar 2>/dev/null | wc -l" | tr -d ' ')
echo "   Found $JAR_FILES JAR file(s)"

if [ "$JAR_FILES" -gt 0 ]; then
    echo "   ✅ Installation verified"
    echo "   JAR files:"
    docker exec $CONTAINER_ID bash -c "ls -lh $PLUGINS_DIR/$CONNECTOR_NAME/*.jar | head -5"
else
    echo "   ⚠️  No JAR files found - checking directory contents..."
    docker exec $CONTAINER_ID bash -c "ls -la $PLUGINS_DIR/$CONNECTOR_NAME/"
fi

# Step 7: Restart container
echo ""
echo "7. Restarting Kafka Connect container..."
docker restart $CONTAINER_ID
echo "   ✅ Container restarted"

# Step 8: Wait for container to be ready
echo ""
echo "8. Waiting for Kafka Connect to be ready (this may take 30-60 seconds)..."
for i in {1..60}; do
    if docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        echo "   ✅ Kafka Connect is ready (after $i attempts)"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "   ⚠️  Kafka Connect did not become ready after 60 attempts"
        echo "   Check logs: docker logs $CONTAINER_ID"
    else
        echo -n "."
        sleep 1
    fi
done
echo ""

# Step 9: Verify Oracle connector is available
echo ""
echo "9. Verifying Oracle connector is available..."
sleep 5  # Extra wait for plugins to load
ORACLE_CHECK=$(docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i oracle | wc -l | tr -d ' ')

if [ "$ORACLE_CHECK" -gt 0 ]; then
    echo "   ✅ Oracle connector is available!"
    echo ""
    echo "   Oracle connector details:"
    docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins | grep -i oracle
else
    echo "   ⚠️  Oracle connector not found in plugins list"
    echo ""
    echo "   Checking logs for errors..."
    docker logs $CONTAINER_ID --tail 50 | grep -i "oracle\|error" | tail -10
    echo ""
    echo "   All available connectors:"
    docker exec $CONTAINER_ID curl -s http://localhost:8083/connector-plugins | grep -i debezium
fi

echo ""
echo "======================================================================"
echo "Installation Complete!"
echo "======================================================================"
echo ""
echo "If Oracle connector is not showing:"
echo "1. Check logs: docker logs $CONTAINER_ID | grep -i oracle"
echo "2. Verify JAR files: docker exec $CONTAINER_ID ls -la $PLUGINS_DIR/$CONNECTOR_NAME/"
echo "3. Check plugin path: docker exec $CONTAINER_ID env | grep PLUGIN"
echo "4. Restart again: docker restart $CONTAINER_ID"


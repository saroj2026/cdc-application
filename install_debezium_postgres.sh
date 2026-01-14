#!/bin/bash
# Install Debezium PostgreSQL Connector to Kafka Connect
# Run this on the VPS server (72.61.233.209)

set -e

echo "=========================================="
echo "Installing Debezium PostgreSQL Connector"
echo "=========================================="

CONTAINER_NAME="kafka-connect-cdc"
PLUGIN_PATH="/kafka/connect"
DEBEZIUM_VERSION="2.5.0.Final"
DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/${DEBEZIUM_VERSION}/debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz"

# Step 1: Download
echo ""
echo "1. Downloading Debezium PostgreSQL connector..."
cd /tmp
if [ -f "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz" ]; then
    echo "   [INFO] File already exists, skipping download"
else
    wget "$DOWNLOAD_URL" || {
        echo "   [ERROR] Failed to download connector"
        exit 1
    }
    echo "   [OK] Downloaded"
fi

# Step 2: Extract
echo ""
echo "2. Extracting connector..."
if [ -d "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin" ]; then
    echo "   [INFO] Directory already exists, removing old one..."
    rm -rf "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin"
fi
tar -xzf "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz"
echo "   [OK] Extracted"

# Step 3: Copy to container
echo ""
echo "3. Copying connector to Kafka Connect container..."
JAR_COUNT=$(find "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin" -name "*.jar" | wc -l)
echo "   Found $JAR_COUNT JAR files"

docker cp "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin"/. "${CONTAINER_NAME}:${PLUGIN_PATH}/" || {
    echo "   [ERROR] Failed to copy files to container"
    exit 1
}
echo "   [OK] Files copied"

# Step 4: Restart container
echo ""
echo "4. Restarting Kafka Connect container..."
docker restart "$CONTAINER_NAME" || {
    echo "   [ERROR] Failed to restart container"
    exit 1
}
echo "   [OK] Container restarted"

# Step 5: Wait and verify
echo ""
echo "5. Waiting for Kafka Connect to start (60 seconds)..."
sleep 60

echo ""
echo "6. Verifying installation..."
response=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "PostgresConnector" || echo "")

if [ -n "$response" ]; then
    echo "   ✅ Debezium PostgreSQL connector is installed!"
    echo ""
    echo "   Connector details:"
    curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 3 -i "PostgresConnector" || echo "$response"
else
    echo "   ⚠️  Connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo ""
    echo "   Check logs: docker logs $CONTAINER_NAME | tail -50"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl http://72.61.233.209:8083/connector-plugins | grep -i postgres"
echo "2. Retry starting the pipeline: python create_and_start_final_test.py"
echo ""

# Install Debezium PostgreSQL Connector to Kafka Connect
# Run this on the VPS server (72.61.233.209)

set -e

echo "=========================================="
echo "Installing Debezium PostgreSQL Connector"
echo "=========================================="

CONTAINER_NAME="kafka-connect-cdc"
PLUGIN_PATH="/kafka/connect"
DEBEZIUM_VERSION="2.5.0.Final"
DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-postgres/${DEBEZIUM_VERSION}/debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz"

# Step 1: Download
echo ""
echo "1. Downloading Debezium PostgreSQL connector..."
cd /tmp
if [ -f "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz" ]; then
    echo "   [INFO] File already exists, skipping download"
else
    wget "$DOWNLOAD_URL" || {
        echo "   [ERROR] Failed to download connector"
        exit 1
    }
    echo "   [OK] Downloaded"
fi

# Step 2: Extract
echo ""
echo "2. Extracting connector..."
if [ -d "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin" ]; then
    echo "   [INFO] Directory already exists, removing old one..."
    rm -rf "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin"
fi
tar -xzf "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin.tar.gz"
echo "   [OK] Extracted"

# Step 3: Copy to container
echo ""
echo "3. Copying connector to Kafka Connect container..."
JAR_COUNT=$(find "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin" -name "*.jar" | wc -l)
echo "   Found $JAR_COUNT JAR files"

docker cp "debezium-connector-postgres-${DEBEZIUM_VERSION}-plugin"/. "${CONTAINER_NAME}:${PLUGIN_PATH}/" || {
    echo "   [ERROR] Failed to copy files to container"
    exit 1
}
echo "   [OK] Files copied"

# Step 4: Restart container
echo ""
echo "4. Restarting Kafka Connect container..."
docker restart "$CONTAINER_NAME" || {
    echo "   [ERROR] Failed to restart container"
    exit 1
}
echo "   [OK] Container restarted"

# Step 5: Wait and verify
echo ""
echo "5. Waiting for Kafka Connect to start (60 seconds)..."
sleep 60

echo ""
echo "6. Verifying installation..."
response=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "PostgresConnector" || echo "")

if [ -n "$response" ]; then
    echo "   ✅ Debezium PostgreSQL connector is installed!"
    echo ""
    echo "   Connector details:"
    curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 3 -i "PostgresConnector" || echo "$response"
else
    echo "   ⚠️  Connector not found in connector-plugins"
    echo "   This might be normal if the connector needs more time to load"
    echo ""
    echo "   Check logs: docker logs $CONTAINER_NAME | tail -50"
fi

echo ""
echo "=========================================="
echo "Installation Complete"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Verify connector: curl http://72.61.233.209:8083/connector-plugins | grep -i postgres"
echo "2. Retry starting the pipeline: python create_and_start_final_test.py"
echo ""


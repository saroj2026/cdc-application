#!/bin/bash
# Script to install Debezium Oracle Connector on Kafka Connect server
# Run this on the server where Kafka Connect is running (72.61.233.209)

set -e

echo "======================================================================"
echo "Installing Debezium Oracle Connector"
echo "======================================================================"

# Kafka Connect plugins directory (adjust if different)
KAFKA_CONNECT_PLUGINS_DIR="/usr/share/confluent-hub-components"
# Alternative common locations:
# KAFKA_CONNECT_PLUGINS_DIR="/opt/kafka/plugins"
# KAFKA_CONNECT_PLUGINS_DIR="/var/lib/kafka-connect/plugins"

# Debezium Oracle Connector version (check latest at https://debezium.io/releases/)
DEBEZIUM_VERSION="2.5.0.Final"
ORACLE_CONNECTOR_NAME="debezium-connector-oracle"

echo ""
echo "1. Checking Kafka Connect plugins directory..."
if [ -d "$KAFKA_CONNECT_PLUGINS_DIR" ]; then
    echo "   ✅ Found plugins directory: $KAFKA_CONNECT_PLUGINS_DIR"
else
    echo "   ⚠️  Plugins directory not found at: $KAFKA_CONNECT_PLUGINS_DIR"
    echo "   Please update KAFKA_CONNECT_PLUGINS_DIR in this script"
    exit 1
fi

echo ""
echo "2. Creating Oracle connector directory..."
ORACLE_CONNECTOR_DIR="$KAFKA_CONNECT_PLUGINS_DIR/$ORACLE_CONNECTOR_NAME"
mkdir -p "$ORACLE_CONNECTOR_DIR"
echo "   ✅ Created: $ORACLE_CONNECTOR_DIR"

echo ""
echo "3. Downloading Debezium Oracle Connector..."
echo "   Version: $DEBEZIUM_VERSION"
echo "   URL: https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/$DEBEZIUM_VERSION/"

cd "$ORACLE_CONNECTOR_DIR"

# Download the connector JAR
JAR_FILE="debezium-connector-oracle-${DEBEZIUM_VERSION}-plugin.tar.gz"
DOWNLOAD_URL="https://repo1.maven.org/maven2/io/debezium/debezium-connector-oracle/$DEBEZIUM_VERSION/$JAR_FILE"

echo "   Downloading from: $DOWNLOAD_URL"
if command -v wget &> /dev/null; then
    wget "$DOWNLOAD_URL" -O "$JAR_FILE"
elif command -v curl &> /dev/null; then
    curl -L "$DOWNLOAD_URL" -o "$JAR_FILE"
else
    echo "   ❌ Error: Neither wget nor curl is available"
    exit 1
fi

if [ -f "$JAR_FILE" ]; then
    echo "   ✅ Downloaded: $JAR_FILE"
else
    echo "   ❌ Download failed"
    exit 1
fi

echo ""
echo "4. Extracting connector files..."
tar -xzf "$JAR_FILE"
rm "$JAR_FILE"  # Remove archive after extraction
echo "   ✅ Extracted connector files"

echo ""
echo "5. Verifying installation..."
if [ -f "$ORACLE_CONNECTOR_DIR/debezium-connector-oracle-${DEBEZIUM_VERSION}.jar" ]; then
    echo "   ✅ Connector JAR found"
    ls -lh "$ORACLE_CONNECTOR_DIR"/*.jar | head -5
else
    echo "   ⚠️  Connector JAR not found, checking directory contents..."
    ls -la "$ORACLE_CONNECTOR_DIR"
fi

echo ""
echo "6. Checking for Oracle JDBC driver..."
if [ -f "$ORACLE_CONNECTOR_DIR/ojdbc*.jar" ]; then
    echo "   ✅ Oracle JDBC driver found"
    ls -lh "$ORACLE_CONNECTOR_DIR/ojdbc*.jar"
else
    echo "   ⚠️  Oracle JDBC driver not found in connector package"
    echo "   You may need to download it separately:"
    echo "   https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html"
    echo "   Place ojdbc8.jar or ojdbc11.jar in: $ORACLE_CONNECTOR_DIR"
fi

echo ""
echo "======================================================================"
echo "✅ Installation Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. Restart Kafka Connect to load the new connector"
echo "2. Verify connector is available:"
echo "   curl http://localhost:8083/connector-plugins | grep -i oracle"
echo ""
echo "If Kafka Connect is in Docker:"
echo "  docker restart <kafka-connect-container-id>"
echo ""
echo "Connector directory: $ORACLE_CONNECTOR_DIR"


#!/bin/bash
# Copy Debezium AS400 connector from local CDCTEAM folder to VPS and install it
# Run this from your Mac

echo "=================================================================================="
echo "📦 COPYING DEBEZIUM CONNECTOR FROM LOCAL TO VPS"
echo "=================================================================================="
echo ""

VPS_HOST="72.61.233.209"
VPS_USER="root"
CONTAINER_NAME="kafka-connect-cdc"

# Find connector on local machine
echo "Step 1: Looking for debezium-connector-ibmi in CDCTEAM folder..."
echo ""

LOCAL_PATHS=(
    "$HOME/Desktop/CDCTEAM/debezium-connector-ibmi"
    "$HOME/Desktop/CDCTEAM/cdcteam/debezium-connector-ibmi"
    "$HOME/Desktop/CDCTEAM/seg-cdc-application/debezium-connector-ibmi"
    "./debezium-connector-ibmi"
    "../debezium-connector-ibmi"
    "../../debezium-connector-ibmi"
)

CONNECTOR_PATH=""

for path in "${LOCAL_PATHS[@]}"; do
    if [ -d "$path" ]; then
        CONNECTOR_PATH="$path"
        echo "✅ Found connector at: $CONNECTOR_PATH"
        break
    fi
done

# If not found, search more broadly
if [ -z "$CONNECTOR_PATH" ]; then
    echo "  Not found in common locations. Searching in Desktop/CDCTEAM..."
    CONNECTOR_PATH=$(find "$HOME/Desktop/CDCTEAM" -type d -name "debezium-connector-ibmi" 2>/dev/null | head -1)
    if [ -n "$CONNECTOR_PATH" ]; then
        echo "✅ Found connector at: $CONNECTOR_PATH"
    fi
fi

# If still not found, ask user
if [ -z "$CONNECTOR_PATH" ]; then
    echo ""
    echo "❌ Connector not found automatically"
    echo ""
    echo "Please provide the full path to the debezium-connector-ibmi folder:"
    echo "  Example: /Users/kumargaurav/Desktop/CDCTEAM/debezium-connector-ibmi"
    echo ""
    read -p "Enter path: " CONNECTOR_PATH
    
    if [ -z "$CONNECTOR_PATH" ] || [ ! -d "$CONNECTOR_PATH" ]; then
        echo "❌ Invalid path or directory does not exist"
        echo ""
        echo "To find it, run:"
        echo "  find ~/Desktop/CDCTEAM -type d -name 'debezium-connector-ibmi' 2>/dev/null"
        exit 1
    fi
fi

echo ""
echo "Step 2: Verifying connector directory..."
JAR_COUNT=$(find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l)
if [ "$JAR_COUNT" -eq 0 ]; then
    echo "⚠️  No JAR files found. This might not be a valid connector."
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Found $JAR_COUNT JAR files"
fi

echo ""
echo "Step 3: Copying connector to VPS server..."
echo "  From: $CONNECTOR_PATH"
echo "  To: $VPS_USER@$VPS_HOST:/tmp/debezium-connector-ibmi"
echo ""

# Create a tarball for faster transfer
echo "  Creating tarball..."
TARBALL="/tmp/debezium-connector-ibmi.tar.gz"
cd "$(dirname "$CONNECTOR_PATH")"
tar -czf "$TARBALL" "$(basename "$CONNECTOR_PATH")" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Failed to create tarball"
    exit 1
fi

echo "  Uploading to VPS..."
scp "$TARBALL" "$VPS_USER@$VPS_HOST:/tmp/"

if [ $? -ne 0 ]; then
    echo "❌ Failed to upload to VPS"
    rm -f "$TARBALL"
    exit 1
fi

echo "✅ Uploaded successfully"

# Clean up local tarball
rm -f "$TARBALL"

echo ""
echo "Step 4: Installing connector on VPS..."
echo "  (This will extract, copy to container, and restart Kafka Connect)"
echo ""

ssh "$VPS_USER@$VPS_HOST" << 'REMOTE_SCRIPT'
CONTAINER_NAME="kafka-connect-cdc"
TARBALL="/tmp/debezium-connector-ibmi.tar.gz"
EXTRACT_DIR="/tmp/debezium-connector-ibmi"
CONTAINER_PATH="/usr/share/java/plugins/debezium-connector-ibmi"

# Extract
echo "  Extracting tarball..."
rm -rf "$EXTRACT_DIR"
mkdir -p "$EXTRACT_DIR"
tar -xzf "$TARBALL" -C "$EXTRACT_DIR" --strip-components=1 2>/dev/null || tar -xzf "$TARBALL" -C "$EXTRACT_DIR"
rm -f "$TARBALL"

# Find the actual connector directory
CONNECTOR_DIR=$(find "$EXTRACT_DIR" -type d -name "debezium-connector-ibmi*" | head -1)
if [ -z "$CONNECTOR_DIR" ]; then
    CONNECTOR_DIR="$EXTRACT_DIR"
fi

echo "  Connector directory: $CONNECTOR_DIR"

# Check container
if ! docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container '$CONTAINER_NAME' is not running!"
    exit 1
fi

# Remove existing
if docker exec "$CONTAINER_NAME" test -d "$CONTAINER_PATH" 2>/dev/null; then
    echo "  Removing existing connector..."
    docker exec "$CONTAINER_NAME" rm -rf "$CONTAINER_PATH"
fi

# Copy to container
echo "  Copying to container..."
docker cp "$CONNECTOR_DIR" "$CONTAINER_NAME:$CONTAINER_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Copied to container"
else
    echo "❌ Failed to copy to container"
    exit 1
fi

# Restart
echo "  Restarting Kafka Connect..."
docker restart "$CONTAINER_NAME"
echo "  Waiting 30 seconds..."
sleep 30

# Verify
echo ""
echo "  Verifying connector is loaded..."
if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector\|db2as400"; then
    echo "✅ SUCCESS! AS400 connector is loaded!"
    curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
    curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" -A 5
else
    echo "⚠️  Connector may need more time to load"
    echo "   Check manually: curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
fi

# Cleanup
rm -rf "$EXTRACT_DIR"
REMOTE_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! Connector installed on VPS"
    echo "=================================================================================="
    echo ""
    echo "You can now start your AS400 pipeline:"
    echo "  python3 start_as400_pipeline.py"
    echo ""
else
    echo ""
    echo "❌ Installation failed. Check the error messages above."
    exit 1
fi


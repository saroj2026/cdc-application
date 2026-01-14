#!/bin/bash
# Fix IBM i connector not loading in Kafka Connect
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "🔧 FIXING IBM i CONNECTOR NOT LOADING"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"
CONNECTOR_PATH="/usr/share/java/plugins/debezium-connector-ibmi"

echo "Step 1: Checking connector directory structure..."
echo ""

# Check if directory exists
if ! docker exec "$CONTAINER_NAME" test -d "$CONNECTOR_PATH" 2>/dev/null; then
    echo "❌ Connector directory does not exist: $CONNECTOR_PATH"
    exit 1
fi

echo "✅ Connector directory exists: $CONNECTOR_PATH"
echo ""

# List directory contents
echo "Directory contents:"
docker exec "$CONTAINER_NAME" ls -la "$CONNECTOR_PATH"
echo ""

# Check for JAR files
echo "Step 2: Checking for JAR files..."
JAR_COUNT=$(docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null | wc -l)

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in connector directory!"
    echo ""
    echo "The connector directory exists but is empty or incomplete."
    echo ""
    echo "Checking subdirectories..."
    docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -type d
    echo ""
    echo "You may need to reinstall the connector with all JAR files."
    exit 1
fi

echo "✅ Found $JAR_COUNT JAR files"
echo ""

# Show sample JAR files
echo "Sample JAR files:"
docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null | head -10
echo ""

# Check for the specific AS400 connector JAR
echo "Step 3: Looking for AS400 connector JAR..."
AS400_JAR=$(docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -name "*as400*.jar" -o -name "*ibmi*.jar" -o -name "*db2as400*.jar" 2>/dev/null | head -1)

if [ -n "$AS400_JAR" ]; then
    echo "✅ Found AS400 connector JAR: $AS400_JAR"
else
    echo "⚠️  AS400-specific JAR not found (may be in main connector JAR)"
fi
echo ""

# Check Kafka Connect logs for errors
echo "Step 4: Checking Kafka Connect logs for errors..."
echo "Recent errors related to ibmi/as400:"
docker logs "$CONTAINER_NAME" 2>&1 | grep -i "ibmi\|as400\|db2as400" | tail -20
echo ""

# Check plugin path configuration
echo "Step 5: Checking plugin path configuration..."
PLUGIN_PATH=$(docker exec "$CONTAINER_NAME" env | grep -i "plugin.path\|PLUGIN_PATH" | head -1)
if [ -n "$PLUGIN_PATH" ]; then
    echo "Plugin path: $PLUGIN_PATH"
    
    # Check if /usr/share/java/plugins is in the path
    if echo "$PLUGIN_PATH" | grep -qi "/usr/share/java/plugins"; then
        echo "✅ /usr/share/java/plugins is in plugin path"
    else
        echo "⚠️  /usr/share/java/plugins may not be in plugin path"
        echo "   But it's usually included by default"
    fi
else
    echo "⚠️  Plugin path not explicitly set (using defaults)"
fi
echo ""

# Restart Kafka Connect
echo "Step 6: Restarting Kafka Connect to reload plugins..."
docker restart "$CONTAINER_NAME"
echo "Waiting 30 seconds for restart..."
sleep 30

echo ""
echo "Step 7: Checking if connector is now loaded..."
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        PLUGINS=$(curl -s http://localhost:8083/connector-plugins)
        
        # Check for AS400 connector
        if echo "$PLUGINS" | grep -qi "As400RpcConnector\|db2as400"; then
            echo "✅ AS400 connector plugin is now LOADED!"
            echo ""
            echo "Connector details:"
            echo "$PLUGINS" | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            echo "$PLUGINS" | grep -i "As400RpcConnector\|db2as400" -A 5
            SUCCESS=true
            break
        else
            echo "  ⏳ Connector not loaded yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)..."
            RETRY_COUNT=$((RETRY_COUNT+1))
            sleep 5
        fi
    else
        echo "  ⏳ Kafka Connect not responding yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)..."
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo ""
    echo "❌ Connector still not loaded after restart"
    echo ""
    echo "Troubleshooting steps:"
    echo ""
    echo "1. Check if connector JAR files are valid:"
    echo "   docker exec $CONTAINER_NAME find $CONNECTOR_PATH -name '*.jar' | head -5"
    echo ""
    echo "2. Check Kafka Connect logs for errors:"
    echo "   docker logs $CONTAINER_NAME | tail -100 | grep -i error"
    echo ""
    echo "3. Verify connector structure (should have JARs directly or in lib/):"
    echo "   docker exec $CONTAINER_NAME ls -la $CONNECTOR_PATH"
    echo "   docker exec $CONTAINER_NAME find $CONNECTOR_PATH -type f | head -10"
    echo ""
    echo "4. The connector may need to be in a specific structure."
    echo "   Check Debezium documentation for the correct plugin structure."
    echo ""
    echo "5. Try removing and reinstalling the connector:"
    echo "   docker exec $CONTAINER_NAME rm -rf $CONNECTOR_PATH"
    echo "   # Then reinstall using copy_connector_from_local_to_vps.sh"
    exit 1
else
    echo ""
    echo "=================================================================================="
    echo "✅ SUCCESS! AS400 connector is installed and loaded"
    echo "=================================================================================="
    echo ""
    echo "You can now start your AS400 pipeline:"
    echo "  python3 start_as400_pipeline.py"
    echo ""
fi


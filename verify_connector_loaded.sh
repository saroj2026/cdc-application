#!/bin/bash
# Verify AS400 connector is loaded in Kafka Connect
# Run this on the VPS server

echo "=================================================================================="
echo "🔍 VERIFYING AS400 CONNECTOR IS LOADED"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"

echo "Step 1: Checking if connector directory exists..."
if docker exec "$CONTAINER_NAME" test -d "/usr/share/java/plugins/debezium-connector-ibmi" 2>/dev/null; then
    echo "✅ Connector directory exists"
else
    echo "❌ Connector directory does NOT exist"
    exit 1
fi

echo ""
echo "Step 2: Checking JAR files..."
JAR_COUNT=$(docker exec "$CONTAINER_NAME" find /usr/share/java/plugins/debezium-connector-ibmi -name "*.jar" 2>/dev/null | wc -l)

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "❌ No JAR files found in connector directory"
    echo "   The connector may be incomplete"
    exit 1
else
    echo "✅ Found $JAR_COUNT JAR files"
    echo ""
    echo "Sample JAR files:"
    docker exec "$CONTAINER_NAME" find /usr/share/java/plugins/debezium-connector-ibmi -name "*.jar" 2>/dev/null | head -5
fi

echo ""
echo "Step 3: Checking if Kafka Connect is running..."
if ! curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
    echo "⚠️  Kafka Connect is not responding"
    echo "   Restarting container..."
    docker restart "$CONTAINER_NAME"
    echo "   Waiting 30 seconds..."
    sleep 30
fi

echo ""
echo "Step 4: Checking if connector plugin is loaded..."
PLUGINS=$(curl -s --max-time 10 "http://localhost:8083/connector-plugins" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$PLUGINS" ]; then
    if echo "$PLUGINS" | grep -qi "As400RpcConnector\|db2as400"; then
        echo "✅ AS400 connector plugin is LOADED!"
        echo ""
        echo "Connector details:"
        echo "$PLUGINS" | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
        echo "$PLUGINS" | grep -i "As400RpcConnector\|db2as400" -A 5
        echo ""
        echo "=================================================================================="
        echo "✅ SUCCESS! Connector is installed and loaded"
        echo "=================================================================================="
        echo ""
        echo "You can now start your AS400 pipeline:"
        echo "  python3 start_as400_pipeline.py"
    else
        echo "⚠️  Connector is installed but NOT loaded"
        echo ""
        echo "This usually means Kafka Connect needs to be restarted to load the plugin."
        echo ""
        echo "Restarting Kafka Connect..."
        docker restart "$CONTAINER_NAME"
        echo "Waiting 30 seconds..."
        sleep 30
        
        echo ""
        echo "Checking again..."
        PLUGINS=$(curl -s --max-time 10 "http://localhost:8083/connector-plugins" 2>/dev/null)
        if echo "$PLUGINS" | grep -qi "As400RpcConnector\|db2as400"; then
            echo "✅ AS400 connector plugin is now LOADED!"
            echo ""
            echo "Connector details:"
            echo "$PLUGINS" | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            echo "$PLUGINS" | grep -i "As400RpcConnector\|db2as400" -A 5
        else
            echo "❌ Connector still not loaded after restart"
            echo ""
            echo "Troubleshooting:"
            echo "1. Check Kafka Connect logs: docker logs $CONTAINER_NAME | tail -50"
            echo "2. Verify JAR files are valid: docker exec $CONTAINER_NAME ls -la /usr/share/java/plugins/debezium-connector-ibmi/*.jar | head -5"
            echo "3. Check plugin path: docker exec $CONTAINER_NAME env | grep PLUGIN_PATH"
            exit 1
        fi
    fi
else
    echo "❌ Cannot access connector plugins endpoint"
    echo "   Kafka Connect may not be running or accessible"
    exit 1
fi

echo ""


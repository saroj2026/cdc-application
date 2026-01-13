#!/bin/bash

# Check AS400 connector installation in Kafka Connect
# Run this on the server: 72.61.233.209

echo "================================================================================
🔍 CHECKING AS400 CONNECTOR INSTALLATION
================================================================================
"

# Find Kafka Connect container
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ Kafka Connect container not found!"
    exit 1
fi

echo "Container: $CONTAINER"
echo ""

# Check if connector directory exists
echo "1. Checking connector directory..."
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "   ✅ Directory exists: /kafka/connect/debezium-connector-ibmi"
    
    # Count JARs
    JAR_COUNT=$(docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | wc -l)
    echo "   JAR files: $JAR_COUNT"
    
    if [ "$JAR_COUNT" -gt 0 ]; then
        echo "   ✅ JAR files present"
        echo ""
        echo "   Sample JARs:"
        docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | head -5 | while read jar; do
            echo "      - $(basename $jar)"
        done
    else
        echo "   ❌ No JAR files found!"
    fi
else
    echo "   ❌ Directory NOT found: /kafka/connect/debezium-connector-ibmi"
    echo ""
    echo "   Available connector directories:"
    docker exec $CONTAINER ls -la /kafka/connect/ 2>/dev/null | grep "^d" | awk '{print "      - " $NF}' | grep -v "^\.$" | grep -v "^\.\.$"
fi
echo ""

# Check plugin path configuration
echo "2. Checking plugin path..."
PLUGIN_PATH=$(docker exec $CONTAINER env | grep -i "plugin.path\|PLUGIN_PATH" | head -1)
if [ -n "$PLUGIN_PATH" ]; then
    echo "   $PLUGIN_PATH"
else
    echo "   ⚠️  Plugin path not found in environment"
    echo "   Default should be: /kafka/connect"
fi
echo ""

# Check if plugin is loaded
echo "3. Checking if plugin is loaded..."
if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" | wc -l)
    if [ "$AS400_FOUND" -gt 0 ]; then
        echo "   ✅ AS400 connector plugin is loaded"
        echo ""
        echo "   Connector details:"
        curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
        curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" -A 5
    else
        echo "   ❌ AS400 connector plugin is NOT loaded"
        echo ""
        echo "   Available Debezium connectors:"
        curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -E '"class"' | grep -i "debezium" | head -10 || \
        curl -s http://localhost:8083/connector-plugins | grep -i "debezium" | head -10
    fi
else
    echo "   ❌ Cannot check plugins (Kafka Connect not responding)"
fi
echo ""

# Check for errors in logs
echo "4. Checking for errors in logs (last 200 lines)..."
ERRORS=$(docker logs $CONTAINER 2>&1 | tail -200 | grep -iE "error|exception|fatal|failed" | grep -v "WARNING" | head -20)
if [ -n "$ERRORS" ]; then
    echo "   ❌ Found errors:"
    echo "$ERRORS"
else
    echo "   ✅ No errors found (only warnings shown)"
fi
echo ""

# Summary
echo "================================================================================
📋 SUMMARY
================================================================================
"

# Check directory
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    JAR_COUNT=$(docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | wc -l)
    if [ "$JAR_COUNT" -gt 0 ]; then
        echo "✅ Connector directory exists with JARs"
        
        # Check if loaded
        AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" | wc -l)
        if [ "$AS400_FOUND" -gt 0 ]; then
            echo "✅ Connector plugin is loaded"
            echo ""
            echo "The connector is installed but may need a restart to be recognized."
        else
            echo "❌ Connector plugin is NOT loaded"
            echo ""
            echo "ACTION NEEDED: Restart Kafka Connect to load the plugin"
            echo "   docker restart $CONTAINER"
            echo "   sleep 30"
        fi
    else
        echo "❌ Connector directory exists but NO JAR files"
        echo ""
        echo "ACTION NEEDED: Reinstall the connector"
    fi
else
    echo "❌ Connector directory does NOT exist"
    echo ""
    echo "ACTION NEEDED: Install the connector"
    echo "   Run: /tmp/complete_as400_installation.sh"
fi

echo ""
echo "================================================================================
"



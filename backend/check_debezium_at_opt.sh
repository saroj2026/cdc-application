#!/bin/bash

# Check Debezium connector at /opt/cdc3/connect-plugins
# Run this on the server: 72.61.233.209

echo "================================================================================
🔍 CHECKING DEBEZIUM CONNECTOR AT /opt/cdc3/connect-plugins
================================================================================
"

# Check if directory exists on host
echo "1. Checking /opt/cdc3/connect-plugins on host..."
if [ -d "/opt/cdc3/connect-plugins" ]; then
    echo "   ✅ Directory exists on host"
    
    # List contents
    echo "   Contents:"
    ls -la /opt/cdc3/connect-plugins | head -20
    echo ""
    
    # Look for debezium connectors
    echo "   Debezium connectors found:"
    find /opt/cdc3/connect-plugins -type d -name "*debezium*" 2>/dev/null | while read dir; do
        echo "      - $dir"
        JAR_COUNT=$(find "$dir" -name "*.jar" 2>/dev/null | wc -l)
        echo "        JAR files: $JAR_COUNT"
    done
    
    # Look specifically for AS400/IBM i connector
    echo ""
    echo "   AS400/IBM i connector:"
    AS400_DIRS=$(find /opt/cdc3/connect-plugins -type d -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" 2>/dev/null)
    if [ -n "$AS400_DIRS" ]; then
        echo "$AS400_DIRS" | while read dir; do
            echo "      ✅ Found: $dir"
            JAR_COUNT=$(find "$dir" -name "*.jar" 2>/dev/null | wc -l)
            echo "        JAR files: $JAR_COUNT"
            if [ "$JAR_COUNT" -gt 0 ]; then
                echo "        Sample JARs:"
                find "$dir" -name "*.jar" 2>/dev/null | head -5 | while read jar; do
                    echo "          - $(basename $jar)"
                done
            fi
        done
    else
        echo "      ❌ AS400/IBM i connector directory not found"
    fi
else
    echo "   ❌ Directory does NOT exist on host"
fi
echo ""

# Find Kafka Connect container
echo "2. Finding Kafka Connect container..."
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found!"
    docker ps
    exit 1
fi

echo "   ✅ Found container: $CONTAINER"
echo ""

# Check if /opt/cdc3 is mounted in container
echo "3. Checking if /opt/cdc3 is accessible in container..."
if docker exec $CONTAINER test -d "/opt/cdc3/connect-plugins" 2>/dev/null; then
    echo "   ✅ Directory is accessible in container"
    
    # List contents in container
    echo "   Contents in container:"
    docker exec $CONTAINER ls -la /opt/cdc3/connect-plugins 2>/dev/null | head -20
    echo ""
    
    # Look for debezium connectors in container
    echo "   Debezium connectors in container:"
    docker exec $CONTAINER find /opt/cdc3/connect-plugins -type d -name "*debezium*" 2>/dev/null | while read dir; do
        echo "      - $dir"
        JAR_COUNT=$(docker exec $CONTAINER find "$dir" -name "*.jar" 2>/dev/null | wc -l)
        echo "        JAR files: $JAR_COUNT"
    done
    
    # Look specifically for AS400/IBM i connector in container
    echo ""
    echo "   AS400/IBM i connector in container:"
    AS400_DIRS=$(docker exec $CONTAINER find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" \) 2>/dev/null)
    if [ -n "$AS400_DIRS" ]; then
        echo "$AS400_DIRS" | while read dir; do
            echo "      ✅ Found: $dir"
            JAR_COUNT=$(docker exec $CONTAINER find "$dir" -name "*.jar" 2>/dev/null | wc -l)
            echo "        JAR files: $JAR_COUNT"
        done
    else
        echo "      ❌ AS400/IBM i connector directory not found in container"
    fi
else
    echo "   ❌ Directory is NOT accessible in container"
    echo "   This might mean it's not mounted as a volume"
    echo ""
    echo "   Checking container volumes..."
    docker inspect $CONTAINER | grep -A 10 "Mounts" | grep -i "opt\|cdc3" || echo "   No /opt/cdc3 mount found"
fi
echo ""

# Check Kafka Connect plugin path
echo "4. Checking Kafka Connect plugin path configuration..."
PLUGIN_PATH=$(docker exec $CONTAINER env | grep -i "plugin.path\|PLUGIN_PATH" | head -1)
if [ -n "$PLUGIN_PATH" ]; then
    echo "   $PLUGIN_PATH"
    
    # Check if /opt/cdc3/connect-plugins is in the path
    if echo "$PLUGIN_PATH" | grep -qi "opt/cdc3\|/opt/cdc3"; then
        echo "   ✅ /opt/cdc3/connect-plugins is in plugin path"
    else
        echo "   ⚠️  /opt/cdc3/connect-plugins is NOT in plugin path"
        echo "   Plugin path might need to include /opt/cdc3/connect-plugins"
    fi
else
    echo "   ⚠️  Plugin path not found in environment"
    echo "   Default is usually: /kafka/connect"
fi
echo ""

# Check if plugin is loaded
echo "5. Checking if plugin is loaded in Kafka Connect..."
if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400\|Db2Connector" | wc -l)
    if [ "$AS400_FOUND" -gt 0 ]; then
        echo "   ✅ AS400/DB2 connector plugin is loaded!"
        echo ""
        echo "   Connector details:"
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400\|Db2Connector" || \
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400\|Db2Connector" -A 5
    else
        echo "   ❌ AS400/DB2 connector plugin is NOT loaded"
        echo ""
        echo "   Available Debezium connectors:"
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -E '"class"' | grep -i "debezium" | head -10 || \
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "debezium" | head -10
    fi
else
    echo "   ❌ Cannot check plugins (Kafka Connect not responding)"
fi
echo ""

# Summary
echo "================================================================================
📋 SUMMARY
================================================================================
"

# Check host directory
if [ -d "/opt/cdc3/connect-plugins" ]; then
    AS400_HOST=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" \) 2>/dev/null | head -1)
    if [ -n "$AS400_HOST" ]; then
        echo "✅ AS400 connector found on host: $AS400_HOST"
    else
        echo "❌ AS400 connector NOT found on host in /opt/cdc3/connect-plugins"
    fi
else
    echo "❌ /opt/cdc3/connect-plugins does NOT exist on host"
fi

# Check container access
if docker exec $CONTAINER test -d "/opt/cdc3/connect-plugins" 2>/dev/null; then
    AS400_CONTAINER=$(docker exec $CONTAINER find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" \) 2>/dev/null | head -1)
    if [ -n "$AS400_CONTAINER" ]; then
        echo "✅ AS400 connector accessible in container: $AS400_CONTAINER"
    else
        echo "❌ AS400 connector NOT accessible in container"
    fi
else
    echo "❌ /opt/cdc3/connect-plugins is NOT accessible in container"
    echo "   ACTION: Check if it's mounted as a volume"
fi

# Check if loaded
AS400_LOADED=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400\|Db2Connector" | wc -l)
if [ "$AS400_LOADED" -gt 0 ]; then
    echo "✅ Connector plugin is loaded in Kafka Connect"
else
    echo "❌ Connector plugin is NOT loaded"
    echo ""
    echo "   If connector exists but not loaded:"
    echo "   1. Check plugin.path includes /opt/cdc3/connect-plugins"
    echo "   2. Restart Kafka Connect: docker restart $CONTAINER"
    echo "   3. Wait 30 seconds and check again"
fi

echo ""
echo "================================================================================
"



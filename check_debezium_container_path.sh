#!/bin/bash

# Check Debezium connector at /usr/share/java/plugins in container
# Run this on the server: 72.61.233.209

echo "================================================================================
🔍 CHECKING DEBEZIUM CONNECTOR AT /usr/share/java/plugins
================================================================================
"

# Find Kafka Connect container by name
echo "1. Finding Kafka Connect container..."
CONTAINER_NAME="kafka-connect-cdc"
CONTAINER=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container '$CONTAINER_NAME' not found!"
    echo "   Available containers:"
    docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
    exit 1
fi

echo "   ✅ Found container: $CONTAINER_NAME ($CONTAINER)"
echo ""

# Check if /usr/share/java/plugins exists in container
echo "2. Checking /usr/share/java/plugins in container..."
if docker exec $CONTAINER test -d "/usr/share/java/plugins" 2>/dev/null; then
    echo "   ✅ Directory exists in container"
    
    # List contents
    echo "   Contents:"
    docker exec $CONTAINER ls -la /usr/share/java/plugins 2>/dev/null | head -20
    echo ""
    
    # Look for debezium connectors
    echo "   Debezium connectors found:"
    docker exec $CONTAINER find /usr/share/java/plugins -type d -name "*debezium*" 2>/dev/null | while read dir; do
        echo "      - $dir"
        JAR_COUNT=$(docker exec $CONTAINER find "$dir" -name "*.jar" 2>/dev/null | wc -l)
        echo "        JAR files: $JAR_COUNT"
    done
    
    # Look specifically for AS400/IBM i connector
    echo ""
    echo "   AS400/IBM i connector:"
    AS400_DIRS=$(docker exec $CONTAINER find /usr/share/java/plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" -o -name "*db2*" \) 2>/dev/null)
    if [ -n "$AS400_DIRS" ]; then
        echo "$AS400_DIRS" | while read dir; do
            echo "      ✅ Found: $dir"
            JAR_COUNT=$(docker exec $CONTAINER find "$dir" -name "*.jar" 2>/dev/null | wc -l)
            echo "        JAR files: $JAR_COUNT"
            if [ "$JAR_COUNT" -gt 0 ]; then
                echo "        Sample JARs:"
                docker exec $CONTAINER find "$dir" -name "*.jar" 2>/dev/null | head -5 | while read jar; do
                    echo "          - $(basename $jar)"
                done
            fi
        done
    else
        echo "      ❌ AS400/IBM i connector directory not found"
        echo ""
        echo "      Checking for DB2 connector (may work for AS400):"
        DB2_DIRS=$(docker exec $CONTAINER find /usr/share/java/plugins -type d -name "*db2*" 2>/dev/null)
        if [ -n "$DB2_DIRS" ]; then
            echo "$DB2_DIRS" | while read dir; do
                echo "        - $dir"
            done
        else
            echo "        ❌ DB2 connector also not found"
        fi
    fi
else
    echo "   ❌ Directory does NOT exist in container"
    echo ""
    echo "   Checking alternative paths..."
    docker exec $CONTAINER ls -la /usr/share/java/ 2>/dev/null
    docker exec $CONTAINER ls -la /kafka/connect/ 2>/dev/null | head -10
fi
echo ""

# Check plugin path configuration
echo "3. Checking plugin path configuration..."
PLUGIN_PATH=$(docker exec $CONTAINER env | grep -i "plugin.path\|PLUGIN_PATH" | head -1)
if [ -n "$PLUGIN_PATH" ]; then
    echo "   $PLUGIN_PATH"
    
    # Check if /usr/share/java/plugins is in the path
    if echo "$PLUGIN_PATH" | grep -qi "usr/share/java/plugins\|/usr/share/java/plugins"; then
        echo "   ✅ /usr/share/java/plugins is in plugin path"
    else
        echo "   ⚠️  /usr/share/java/plugins is NOT explicitly in plugin path"
        echo "   (It might be included by default or in a parent directory)"
    fi
else
    echo "   ⚠️  Plugin path not found in environment"
    echo "   Default paths are usually:"
    echo "   - /usr/share/java/plugins"
    echo "   - /kafka/connect"
fi
echo ""

# Check if plugin is loaded
echo "4. Checking if plugin is loaded in Kafka Connect..."
if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    # Check for AS400 connector
    AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" | wc -l)
    # Check for DB2 connector (may work for AS400)
    DB2_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "Db2Connector" | grep -v "db2as400" | wc -l)
    
    if [ "$AS400_FOUND" -gt 0 ]; then
        echo "   ✅ AS400 connector plugin is loaded!"
        echo ""
        echo "   Connector details:"
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" -A 5
    elif [ "$DB2_FOUND" -gt 0 ]; then
        echo "   ⚠️  DB2 connector found (may work for AS400 with proper config)"
        echo ""
        echo "   Connector details:"
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 10 -i "Db2Connector" | grep -v "db2as400" || \
        curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "Db2Connector" | grep -v "db2as400" -A 5
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

# Check if connector needs to be copied from /opt/cdc3
echo "5. Checking if connector exists on host at /opt/cdc3/connect-plugins..."
if [ -d "/opt/cdc3/connect-plugins" ]; then
    echo "   ✅ Host directory exists"
    
    # Find AS400 connector on host
    AS400_HOST=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" -o -name "*db2*" \) 2>/dev/null | head -1)
    if [ -n "$AS400_HOST" ]; then
        echo "   ✅ Found connector on host: $AS400_HOST"
        echo ""
        echo "   To copy to container:"
        echo "   docker cp $AS400_HOST $CONTAINER:/usr/share/java/plugins/$(basename $AS400_HOST)"
        echo "   docker restart $CONTAINER"
    else
        echo "   ❌ Connector not found on host"
    fi
else
    echo "   ❌ Host directory does NOT exist"
fi
echo ""

# Summary
echo "================================================================================
📋 SUMMARY
================================================================================
"

# Check container directory
AS400_CONTAINER=$(docker exec $CONTAINER find /usr/share/java/plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" -o -name "*db2*" \) 2>/dev/null | head -1)
if [ -n "$AS400_CONTAINER" ]; then
    echo "✅ AS400/DB2 connector found in container: $AS400_CONTAINER"
    JAR_COUNT=$(docker exec $CONTAINER find "$AS400_CONTAINER" -name "*.jar" 2>/dev/null | wc -l)
    echo "   JAR files: $JAR_COUNT"
else
    echo "❌ AS400/DB2 connector NOT found in container at /usr/share/java/plugins"
fi

# Check if loaded
AS400_LOADED=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400\|Db2Connector" | wc -l)
if [ "$AS400_LOADED" -gt 0 ]; then
    echo "✅ Connector plugin is loaded in Kafka Connect"
else
    echo "❌ Connector plugin is NOT loaded"
    echo ""
    echo "   If connector exists but not loaded:"
    echo "   1. Restart Kafka Connect: docker restart $CONTAINER"
    echo "   2. Wait 30 seconds"
    echo "   3. Check again: curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
fi

echo ""
echo "================================================================================
"



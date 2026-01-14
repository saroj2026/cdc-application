#!/bin/bash

# Check if AS400 connector is available in Kafka Connect Docker container
# Run this on the server: 72.61.233.209

echo "================================================================================
🔍 CHECKING AS400 CONNECTOR IN KAFKA CONNECT DOCKER
================================================================================
"

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found!"
    echo "   Available containers:"
    docker ps
    exit 1
fi

echo "   ✅ Found container: $CONTAINER"
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep -i connect | head -1)
echo "   Container name: $CONTAINER_NAME"
echo ""

# Check if connector directory exists in container
echo "2. Checking connector directory in container..."
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "   ✅ Connector directory exists: /kafka/connect/debezium-connector-ibmi"
    
    # Count JARs
    JAR_COUNT=$(docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | wc -l)
    echo "   Found $JAR_COUNT JAR file(s)"
    
    if [ "$JAR_COUNT" -gt 0 ]; then
        echo ""
        echo "   Installed JARs:"
        docker exec $CONTAINER ls -1 /kafka/connect/debezium-connector-ibmi/*.jar 2>/dev/null | head -10 | while read jar; do
            echo "      - $(basename $jar)"
        done
        if [ "$JAR_COUNT" -gt 10 ]; then
            echo "      ... (showing first 10 of $JAR_COUNT)"
        fi
    else
        echo "   ⚠️  Directory exists but no JAR files found"
    fi
else
    echo "   ❌ Connector directory NOT found: /kafka/connect/debezium-connector-ibmi"
    echo ""
    echo "   Available connector directories:"
    docker exec $CONTAINER ls -la /kafka/connect/ 2>/dev/null | grep "^d" | awk '{print "      - " $NF}' | grep -v "^\.$" | grep -v "^\.\.$"
fi
echo ""

# Check if Kafka Connect is accessible
echo "3. Checking Kafka Connect API..."
if curl -s --connect-timeout 5 http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    echo "   ✅ Kafka Connect API is accessible"
    
    # Check for AS400 connector in plugins
    echo ""
    echo "4. Checking for AS400 connector in available plugins..."
    AS400_FOUND=false
    
    # Check for As400RpcConnector
    if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector"; then
        echo "   ✅ AS400 Connector (As400RpcConnector) FOUND!"
        AS400_FOUND=true
        echo ""
        echo "   Connector details:"
        curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector" || \
        curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector" -A 5
    fi
    
    # Check for db2as400
    if curl -s http://localhost:8083/connector-plugins | grep -qi "db2as400"; then
        echo "   ✅ AS400 Connector (db2as400) FOUND!"
        AS400_FOUND=true
    fi
    
    # Check for IBM i connector
    if curl -s http://localhost:8083/connector-plugins | grep -qi "ibmi"; then
        echo "   ✅ IBM i Connector FOUND!"
        AS400_FOUND=true
    fi
    
    if [ "$AS400_FOUND" = false ]; then
        echo "   ❌ AS400 Connector NOT found in available plugins"
        echo ""
        echo "   Available Debezium connectors:"
        curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -E '"class"' | grep -i "debezium" | head -10 || \
        curl -s http://localhost:8083/connector-plugins | grep -i "debezium" | head -10
    fi
else
    echo "   ❌ Kafka Connect API is NOT accessible"
    echo "   This could mean:"
    echo "   - Kafka Connect is not running"
    echo "   - Port 8083 is not exposed"
    echo "   - Firewall is blocking"
    echo ""
    echo "   Checking container status..."
    docker ps | grep -i connect
    echo ""
    echo "   Checking container logs..."
    docker logs $CONTAINER | tail -20
fi
echo ""

# Check from inside container
echo "5. Checking from inside container..."
if docker exec $CONTAINER curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    echo "   ✅ Kafka Connect is accessible from inside container"
    
    # Check for AS400 connector
    if docker exec $CONTAINER curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector"; then
        echo "   ✅ AS400 Connector is available from inside container"
    else
        echo "   ❌ AS400 Connector NOT available from inside container"
        echo ""
        echo "   This might mean:"
        echo "   - Connector JARs are in wrong location"
        echo "   - Kafka Connect needs restart"
        echo "   - Connector plugin path not configured correctly"
    fi
else
    echo "   ❌ Kafka Connect not accessible from inside container"
    echo "   Container may not be running properly"
fi
echo ""

# Summary
echo "================================================================================
📋 SUMMARY
================================================================================
"
echo "Container: $CONTAINER_NAME ($CONTAINER)"
echo ""

# Check directory
if docker exec $CONTAINER test -d "/kafka/connect/debezium-connector-ibmi" 2>/dev/null; then
    echo "✅ Connector directory: EXISTS"
else
    echo "❌ Connector directory: NOT FOUND"
fi

# Check API
if curl -s --connect-timeout 5 http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    echo "✅ Kafka Connect API: ACCESSIBLE"
    
    if curl -s http://localhost:8083/connector-plugins | grep -qi "As400RpcConnector"; then
        echo "✅ AS400 Connector Plugin: AVAILABLE"
        echo ""
        echo "🎉 AS400 connector is installed and ready to use!"
    else
        echo "❌ AS400 Connector Plugin: NOT AVAILABLE"
        echo ""
        echo "⚠️  Connector directory exists but plugin not loaded."
        echo "   Try restarting Kafka Connect:"
        echo "   docker restart $CONTAINER"
        echo "   Then wait 30 seconds and check again."
    fi
else
    echo "❌ Kafka Connect API: NOT ACCESSIBLE"
    echo ""
    echo "⚠️  Cannot verify plugin availability."
    echo "   Check if Kafka Connect is running and port 8083 is exposed."
fi

echo ""
echo "================================================================================
"



#!/bin/bash
# Diagnose and fix IBM i connector installation issue
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "🔍 DIAGNOSING IBM i CONNECTOR INSTALLATION"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"
CONNECTOR_PATH="/usr/share/java/plugins/debezium-connector-ibmi"

echo "Step 1: Checking connector directory..."
if docker exec "$CONTAINER_NAME" test -d "$CONNECTOR_PATH" 2>/dev/null; then
    echo "✅ Directory exists: $CONNECTOR_PATH"
else
    echo "❌ Directory does NOT exist"
    exit 1
fi

echo ""
echo "Step 2: Listing directory contents..."
docker exec "$CONTAINER_NAME" ls -la "$CONNECTOR_PATH"
echo ""

echo "Step 3: Checking for JAR files..."
JAR_FILES=$(docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -name "*.jar" 2>/dev/null)
JAR_COUNT=$(echo "$JAR_FILES" | grep -v "^$" | wc -l | tr -d ' ')

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "❌ NO JAR FILES FOUND!"
    echo ""
    echo "The connector directory exists but is EMPTY or incomplete."
    echo ""
    echo "Checking subdirectories..."
    docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -type d
    echo ""
    echo "Checking all files..."
    docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -type f | head -20
    echo ""
    echo "=================================================================================="
    echo "❌ PROBLEM IDENTIFIED: Connector directory is empty or incomplete"
    echo "=================================================================================="
    echo ""
    echo "SOLUTION: Reinstall the connector with all JAR files"
    echo ""
    echo "The connector needs to be properly extracted with all dependencies."
    echo "The directory structure should contain JAR files directly or in lib/ subdirectory."
    exit 1
else
    echo "✅ Found $JAR_COUNT JAR files"
    echo ""
    echo "Sample JAR files:"
    echo "$JAR_FILES" | head -10
fi

echo ""
echo "Step 4: Checking for the specific AS400 connector JAR..."
AS400_MAIN_JAR=$(docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -name "*debezium-connector-ibmi*.jar" -o -name "*db2as400*.jar" 2>/dev/null | head -1)

if [ -n "$AS400_MAIN_JAR" ]; then
    echo "✅ Found main connector JAR: $AS400_MAIN_JAR"
else
    echo "⚠️  Main connector JAR not found by name pattern"
    echo "   Checking all JARs for class..."
fi

echo ""
echo "Step 5: Checking directory structure..."
echo "Connector should have JARs directly in the directory or in lib/ subdirectory"
STRUCTURE=$(docker exec "$CONTAINER_NAME" find "$CONNECTOR_PATH" -maxdepth 2 -type f -name "*.jar" 2>/dev/null | head -5)
if [ -n "$STRUCTURE" ]; then
    echo "JAR files found at:"
    echo "$STRUCTURE"
else
    echo "⚠️  No JARs found in top 2 levels"
fi

echo ""
echo "Step 6: Checking Kafka Connect logs for connector loading errors..."
echo "Recent errors:"
docker logs "$CONTAINER_NAME" 2>&1 | grep -i "debezium-connector-ibmi\|db2as400\|As400RpcConnector" | tail -10
echo ""

echo "Step 7: Checking if connector JARs are valid..."
# Try to list contents of first JAR to see if it's valid
FIRST_JAR=$(echo "$JAR_FILES" | head -1)
if [ -n "$FIRST_JAR" ]; then
    echo "Checking first JAR: $FIRST_JAR"
    # Check if JAR contains the connector class
    docker exec "$CONTAINER_NAME" sh -c "unzip -l '$FIRST_JAR' 2>/dev/null | grep -i 'As400RpcConnector\|db2as400' | head -5" || echo "  Could not check JAR contents (unzip may not be available)"
fi

echo ""
echo "=================================================================================="
echo "📋 DIAGNOSIS SUMMARY"
echo "=================================================================================="
echo ""

if [ "$JAR_COUNT" -eq 0 ]; then
    echo "❌ PROBLEM: Connector directory is EMPTY"
    echo ""
    echo "SOLUTION:"
    echo "1. Remove the empty directory:"
    echo "   docker exec $CONTAINER_NAME rm -rf $CONNECTOR_PATH"
    echo ""
    echo "2. Reinstall the connector properly:"
    echo "   - Make sure you have the complete connector with all JAR files"
    echo "   - Extract it properly (it may be a tar.gz that needs extraction)"
    echo "   - Copy all JAR files to the connector directory"
    echo ""
    echo "3. The connector should have structure like:"
    echo "   debezium-connector-ibmi/"
    echo "   ├── debezium-connector-ibmi-*.jar"
    echo "   └── lib/"
    echo "       ├── *.jar (dependencies)"
    echo ""
else
    echo "✅ JAR files exist ($JAR_COUNT files)"
    echo ""
    echo "But connector is still not loading. Possible issues:"
    echo "1. JAR files may be corrupted or incomplete"
    echo "2. Connector class may not be in the JARs"
    echo "3. Dependencies may be missing"
    echo "4. Kafka Connect may need a full restart"
    echo ""
    echo "SOLUTION:"
    echo "1. Restart Kafka Connect:"
    echo "   docker restart $CONTAINER_NAME"
    echo "   sleep 45"
    echo ""
    echo "2. Check if connector loads:"
    echo "   curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
    echo ""
    echo "3. If still not loading, check logs:"
    echo "   docker logs $CONTAINER_NAME | tail -100 | grep -i error"
    echo ""
    echo "4. Verify connector structure matches other working connectors:"
    echo "   docker exec $CONTAINER_NAME ls -la /usr/share/java/plugins/debezium-connector-postgres"
    echo "   docker exec $CONTAINER_NAME ls -la $CONNECTOR_PATH"
fi

echo ""


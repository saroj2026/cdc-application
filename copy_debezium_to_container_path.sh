#!/bin/bash

# Copy Debezium connector from /opt/cdc3/connect-plugins to /usr/share/java/plugins in container
# Run this on the server: 72.61.233.209

echo "================================================================================
📦 COPYING DEBEZIUM CONNECTOR TO CONTAINER PATH
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

# Find connector on host
echo "2. Finding connector on host at /opt/cdc3/connect-plugins..."
if [ ! -d "/opt/cdc3/connect-plugins" ]; then
    echo "   ❌ /opt/cdc3/connect-plugins does NOT exist on host"
    exit 1
fi

echo "   ✅ Host directory exists"
echo ""

# Find AS400/DB2 connector
AS400_HOST=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" -o -name "*as400*" -o -name "*db2*" \) 2>/dev/null | head -1)

if [ -z "$AS400_HOST" ]; then
    echo "   ❌ AS400/DB2 connector not found in /opt/cdc3/connect-plugins"
    echo ""
    echo "   Available connectors:"
    ls -la /opt/cdc3/connect-plugins
    exit 1
fi

echo "   ✅ Found connector: $AS400_HOST"
CONNECTOR_NAME=$(basename "$AS400_HOST")
echo "   Connector name: $CONNECTOR_NAME"
echo ""

# Check JAR files
JAR_COUNT=$(find "$AS400_HOST" -name "*.jar" 2>/dev/null | wc -l)
echo "   JAR files on host: $JAR_COUNT"
if [ "$JAR_COUNT" -eq 0 ]; then
    echo "   ⚠️  No JAR files found!"
    exit 1
fi
echo ""

# Check if already exists in container
echo "3. Checking if connector already exists in container..."
CONTAINER_PATH="/usr/share/java/plugins/$CONNECTOR_NAME"
if docker exec $CONTAINER test -d "$CONTAINER_PATH" 2>/dev/null; then
    echo "   ⚠️  Connector already exists in container"
    read -p "   Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Installation cancelled"
        exit 0
    fi
    echo "   Removing existing connector..."
    docker exec $CONTAINER rm -rf "$CONTAINER_PATH"
fi

# Copy to container
echo ""
echo "4. Copying connector to container..."
echo "   From: $AS400_HOST"
echo "   To: $CONTAINER_PATH"
docker cp "$AS400_HOST" "$CONTAINER:$CONTAINER_PATH"

# Verify copy
if docker exec $CONTAINER test -d "$CONTAINER_PATH" 2>/dev/null; then
    echo "   ✅ Connector copied successfully"
    
    # Count JARs in container
    CONTAINER_JAR_COUNT=$(docker exec $CONTAINER find "$CONTAINER_PATH" -name "*.jar" 2>/dev/null | wc -l)
    echo "   JAR files in container: $CONTAINER_JAR_COUNT"
    
    if [ "$CONTAINER_JAR_COUNT" -gt 0 ]; then
        echo "   ✅ JAR files verified"
    else
        echo "   ⚠️  No JAR files found in container (copy may have failed)"
    fi
else
    echo "   ❌ Failed to copy connector"
    exit 1
fi

# Restart Kafka Connect
echo ""
echo "5. Restarting Kafka Connect container..."
docker restart $CONTAINER_NAME

# Wait for restart
echo "   Waiting 30 seconds for Kafka Connect to restart..."
sleep 30

# Verify installation
echo ""
echo "6. Verifying installation..."
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1; then
        # Check for AS400 connector
        AS400_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" | wc -l)
        # Check for DB2 connector
        DB2_FOUND=$(curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "Db2Connector" | grep -v "db2as400" | wc -l)
        
        if [ "$AS400_FOUND" -gt 0 ]; then
            echo "   ✅ AS400 connector plugin is loaded!"
            echo ""
            echo "   Connector details:"
            curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 10 -i "As400RpcConnector\|db2as400" || \
            curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "As400RpcConnector\|db2as400" -A 5
            SUCCESS=true
            break
        elif [ "$DB2_FOUND" -gt 0 ]; then
            echo "   ⚠️  DB2 connector found (may work for AS400)"
            echo ""
            echo "   Connector details:"
            curl -s http://localhost:8083/connector-plugins 2>/dev/null | python3 -m json.tool 2>/dev/null | grep -A 10 -i "Db2Connector" | grep -v "db2as400" || \
            curl -s http://localhost:8083/connector-plugins 2>/dev/null | grep -i "Db2Connector" | grep -v "db2as400" -A 5
            SUCCESS=true
            break
        else
            echo "   ⚠️  Connector not found yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
            RETRY_COUNT=$((RETRY_COUNT+1))
            sleep 5
        fi
    else
        echo "   ⚠️  Kafka Connect not responding yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "   ⚠️  Could not verify installation automatically"
    echo "   Please check manually:"
    echo "   curl -s http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
fi

echo ""
echo "================================================================================
✅ INSTALLATION COMPLETE
================================================================================
"
echo "Next steps:"
echo "1. Verify connector is available:"
echo "   curl http://localhost:8083/connector-plugins | grep -i As400RpcConnector"
echo ""
echo "2. Restart your backend application"
echo ""
echo "3. Try starting your AS400 pipeline again"
echo ""



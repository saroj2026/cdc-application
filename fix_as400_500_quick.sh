#!/bin/bash
# Quick fix for Kafka Connect 500 errors - run on VPS server

echo "🔧 Quick Fix for Kafka Connect 500 Errors"
echo ""

# Find Kafka Connect container by name
CONTAINER_NAME="kafka-connect-cdc"
CONTAINER=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ Kafka Connect container '$CONTAINER_NAME' not found!"
    echo "Available containers:"
    docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"
    exit 1
fi

echo "✅ Found container: $CONTAINER_NAME ($CONTAINER)"
echo ""

# Check if AS400 connector exists
echo "Checking for AS400 connector..."
CONNECTOR=$(docker exec $CONTAINER_NAME find /usr/share/java/plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)

if [ -z "$CONNECTOR" ]; then
    echo "❌ AS400 connector not found!"
    echo ""
    echo "Checking host path..."
    HOST_CONNECTOR=$(find /opt/cdc3/connect-plugins -type d \( -name "*ibmi*" -o -name "*db2as400*" \) 2>/dev/null | head -1)
    
    if [ -n "$HOST_CONNECTOR" ]; then
        echo "✅ Found connector on host: $HOST_CONNECTOR"
        echo "Copying to container..."
        CONNECTOR_NAME=$(basename "$HOST_CONNECTOR")
        docker cp "$HOST_CONNECTOR" "$CONTAINER_NAME:/usr/share/java/plugins/$CONNECTOR_NAME"
        echo "✅ Copied"
    else
        echo "❌ Connector not found on host either!"
        echo "Please download debezium-connector-ibmi first"
        exit 1
    fi
else
    echo "✅ AS400 connector found: $CONNECTOR"
fi

echo ""
echo "Restarting Kafka Connect..."
docker restart $CONTAINER_NAME

echo ""
echo "Waiting 30 seconds for restart..."
sleep 30

echo ""
echo "Checking if connector is loaded..."
curl -s http://localhost:8083/connector-plugins | grep -i "As400RpcConnector\|db2as400" && echo "✅ Connector loaded!" || echo "⚠️  Connector may need more time to load"

echo ""
echo "✅ Done! Try starting the pipeline again."


#!/bin/bash
# Check and start Kafka Connect on VPS server
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "🔍 CHECKING KAFKA CONNECT STATUS"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"
VPS_HOST="72.61.233.209"

# Check if container exists and is running
echo "Step 1: Checking Kafka Connect container..."
CONTAINER_STATUS=$(docker ps --filter "name=$CONTAINER_NAME" --format "{{.Status}}" 2>/dev/null)

if [ -z "$CONTAINER_STATUS" ]; then
    echo "❌ Container '$CONTAINER_NAME' is NOT running"
    echo ""
    echo "Checking if container exists..."
    if docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        echo "⚠️  Container exists but is stopped"
        echo ""
        echo "Starting container..."
        docker start "$CONTAINER_NAME"
        echo "Waiting 30 seconds for container to start..."
        sleep 30
    else
        echo "❌ Container '$CONTAINER_NAME' does not exist!"
        echo ""
        echo "Available containers:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}"
        echo ""
        echo "You may need to start the Kafka Connect service using docker-compose or your deployment method."
        exit 1
    fi
else
    echo "✅ Container is running: $CONTAINER_STATUS"
fi

echo ""
echo "Step 2: Checking Kafka Connect service..."
sleep 5

# Check if port 8083 is accessible
if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
    echo "✅ Kafka Connect is responding on port 8083"
else
    echo "⚠️  Kafka Connect is not responding on port 8083"
    echo ""
    echo "Checking container logs..."
    echo "Last 20 lines of logs:"
    docker logs "$CONTAINER_NAME" --tail 20 2>&1
    echo ""
    echo "The service may still be starting. Waiting 30 more seconds..."
    sleep 30
    
    if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
        echo "✅ Kafka Connect is now responding"
    else
        echo "❌ Kafka Connect is still not responding"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Check container logs: docker logs $CONTAINER_NAME"
        echo "2. Check if port 8083 is exposed: docker port $CONTAINER_NAME"
        echo "3. Restart the container: docker restart $CONTAINER_NAME"
        exit 1
    fi
fi

echo ""
echo "Step 3: Checking connector plugins..."
PLUGINS=$(curl -s --max-time 5 "http://localhost:8083/connector-plugins" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$PLUGINS" ]; then
    echo "✅ Connector plugins endpoint is accessible"
    
    if echo "$PLUGINS" | grep -qi "As400RpcConnector\|db2as400"; then
        echo "✅ AS400 connector plugin is available!"
    else
        echo "⚠️  AS400 connector plugin is NOT available"
        echo "   You need to install it. See: FIX_AS400_500_ERROR.md"
    fi
else
    echo "⚠️  Cannot access connector plugins endpoint"
fi

echo ""
echo "=================================================================================="
echo "✅ Kafka Connect Status Check Complete"
echo "=================================================================================="
echo ""
echo "If Kafka Connect is running, try starting your pipeline again:"
echo "  python3 start_as400_pipeline.py"
echo ""


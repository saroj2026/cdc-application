#!/bin/bash
# Fix Kafka Connect connection refused error
# Run this on the VPS server (72.61.233.209)

echo "=================================================================================="
echo "🔧 FIXING KAFKA CONNECT CONNECTION REFUSED ERROR"
echo "=================================================================================="
echo ""

CONTAINER_NAME="kafka-connect-cdc"

echo "Step 1: Checking container status..."
CONTAINER_ID=$(docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.ID}}" | head -1)

if [ -z "$CONTAINER_ID" ]; then
    echo "❌ Container '$CONTAINER_NAME' does not exist!"
    echo ""
    echo "Available containers:"
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    echo ""
    echo "You may need to start Kafka Connect using docker-compose or your deployment method."
    exit 1
fi

echo "✅ Found container: $CONTAINER_NAME ($CONTAINER_ID)"

# Check if running
if docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "✅ Container is running"
    
    echo ""
    echo "Step 2: Checking if Kafka Connect is responding..."
    sleep 3
    
    if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
        echo "✅ Kafka Connect is responding"
    else
        echo "⚠️  Kafka Connect is not responding"
        echo ""
        echo "Checking logs for errors..."
        docker logs "$CONTAINER_NAME" --tail 30 2>&1 | grep -i "error\|exception\|failed" | tail -10
        
        echo ""
        echo "Restarting container..."
        docker restart "$CONTAINER_NAME"
        echo "Waiting 30 seconds for restart..."
        sleep 30
        
        if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
            echo "✅ Kafka Connect is now responding"
        else
            echo "❌ Kafka Connect is still not responding"
            echo ""
            echo "Check logs: docker logs $CONTAINER_NAME"
            exit 1
        fi
    fi
else
    echo "⚠️  Container is stopped"
    echo ""
    echo "Starting container..."
    docker start "$CONTAINER_NAME"
    
    echo "Waiting 30 seconds for container to start..."
    sleep 30
    
    echo ""
    echo "Checking if Kafka Connect is responding..."
    if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
        echo "✅ Kafka Connect is responding"
    else
        echo "⚠️  Kafka Connect is not responding yet"
        echo "Waiting 30 more seconds..."
        sleep 30
        
        if curl -s --max-time 5 "http://localhost:8083/" > /dev/null 2>&1; then
            echo "✅ Kafka Connect is now responding"
        else
            echo "❌ Kafka Connect is still not responding"
            echo ""
            echo "Check logs: docker logs $CONTAINER_NAME"
            echo "Check port mapping: docker port $CONTAINER_NAME"
            exit 1
        fi
    fi
fi

echo ""
echo "Step 3: Verifying port 8083 is accessible..."
PORT_CHECK=$(docker port "$CONTAINER_NAME" 2>/dev/null | grep "8083")
if [ -n "$PORT_CHECK" ]; then
    echo "✅ Port mapping: $PORT_CHECK"
else
    echo "⚠️  Port 8083 mapping not found"
    echo "   Container may be using host network mode"
fi

echo ""
echo "Step 4: Testing connector plugins endpoint..."
if curl -s --max-time 5 "http://localhost:8083/connector-plugins" > /dev/null 2>&1; then
    echo "✅ Connector plugins endpoint is accessible"
    
    # Check for AS400 connector
    if curl -s "http://localhost:8083/connector-plugins" | grep -qi "As400RpcConnector\|db2as400"; then
        echo "✅ AS400 connector plugin is available!"
    else
        echo "⚠️  AS400 connector plugin is NOT available"
        echo "   Install it using: copy_connector_from_local_to_vps.sh"
    fi
else
    echo "⚠️  Connector plugins endpoint is not accessible"
fi

echo ""
echo "=================================================================================="
echo "✅ Fix Complete"
echo "=================================================================================="
echo ""
echo "Kafka Connect should now be accessible. Try starting your pipeline:"
echo "  python3 start_as400_pipeline.py"
echo ""


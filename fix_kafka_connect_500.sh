#!/bin/bash

# Quick fix script for Kafka Connect 500 errors
# Run this on the server: 72.61.233.209

echo "================================================================================
🔧 FIXING KAFKA CONNECT 500 ERRORS
================================================================================
"

# Find Kafka Connect container
echo "1. Finding Kafka Connect container..."
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found!"
    docker ps
    exit 1
fi

echo "   ✅ Found container: $CONTAINER"
echo ""

# Check current status
echo "2. Checking current status..."
curl -s http://localhost:8083/connectors > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Kafka Connect is responding"
else
    echo "   ❌ Kafka Connect is not responding properly"
fi
echo ""

# Check logs for errors
echo "3. Checking recent logs for errors..."
docker logs $CONTAINER 2>&1 | grep -i "error\|exception\|fatal" | tail -20
echo ""

# Restart Kafka Connect
echo "4. Restarting Kafka Connect container..."
docker restart $CONTAINER

echo "   Waiting 30 seconds for restart..."
sleep 30

# Verify
echo ""
echo "5. Verifying Kafka Connect is working..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8083/connectors > /dev/null 2>&1; then
        echo "   ✅ Kafka Connect is responding!"
        
        # Try to get connectors
        CONNECTORS=$(curl -s http://localhost:8083/connectors 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "   ✅ /connectors endpoint is working"
            echo "   Found connectors:"
            echo "$CONNECTORS" | python3 -m json.tool 2>/dev/null || echo "$CONNECTORS"
            break
        else
            echo "   ⚠️  Still getting errors (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
            RETRY_COUNT=$((RETRY_COUNT+1))
            sleep 5
        fi
    else
        echo "   ⚠️  Not responding yet (retry $((RETRY_COUNT+1))/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "   ⚠️  Kafka Connect may still have issues"
    echo "   Check logs: docker logs $CONTAINER | tail -50"
fi

echo ""
echo "================================================================================
✅ RESTART COMPLETE
================================================================================
"
echo "Next steps:"
echo "1. Try starting the pipeline again"
echo "2. If still failing, check logs: docker logs $CONTAINER | tail -100"
echo "3. Verify Kafka/Zookeeper are running: docker ps | grep -E 'kafka|zookeeper'"
echo ""



#!/bin/bash

# Script to check Kafka Connect status on remote server
# Run this on the server: 72.61.233.209

echo "================================================================================
🔍 CHECKING KAFKA CONNECT STATUS
================================================================================
"

KAFKA_CONNECT_URL="http://localhost:8083"
REMOTE_URL="http://72.61.233.209:8083"

echo "1. Checking if Kafka Connect container is running..."
CONTAINER=$(docker ps | grep -i connect | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "   ❌ Kafka Connect container not found!"
    echo ""
    echo "   All running containers:"
    docker ps
    echo ""
    echo "   Please check if Kafka Connect is running"
    exit 1
fi

echo "   ✅ Found container: $CONTAINER"
echo ""

echo "2. Checking container status..."
docker ps | grep -i connect
echo ""

echo "3. Checking if Kafka Connect is accessible from inside container..."
docker exec $CONTAINER curl -s http://localhost:8083/connector-plugins > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Kafka Connect is responding inside container"
else
    echo "   ❌ Kafka Connect is NOT responding inside container"
    echo "   Checking container logs..."
    docker logs $CONTAINER | tail -20
    exit 1
fi
echo ""

echo "4. Checking if port 8083 is exposed..."
NETWORK_MODE=$(docker inspect $CONTAINER --format='{{.HostConfig.NetworkMode}}')
PORTS=$(docker port $CONTAINER 2>/dev/null | grep 8083)

if [ -z "$PORTS" ]; then
    echo "   ⚠️  Port 8083 is not exposed/mapped to host"
    echo "   Network mode: $NETWORK_MODE"
    echo ""
    echo "   Container port mapping:"
    docker port $CONTAINER
    echo ""
    echo "   To fix, you may need to:"
    echo "   1. Check docker-compose.yml or docker run command"
    echo "   2. Ensure port 8083:8083 is mapped"
    echo "   3. Restart the container with proper port mapping"
else
    echo "   ✅ Port 8083 is mapped: $PORTS"
fi
echo ""

echo "5. Testing localhost connection..."
if curl -s --connect-timeout 5 http://localhost:8083/connector-plugins > /dev/null 2>&1; then
    echo "   ✅ Kafka Connect is accessible on localhost:8083"
    echo ""
    echo "   Available connectors:"
    curl -s http://localhost:8083/connector-plugins | python3 -m json.tool 2>/dev/null | grep -E '"class"|"type"' | head -10 || \
    curl -s http://localhost:8083/connector-plugins | head -20
else
    echo "   ❌ Cannot connect to localhost:8083"
    echo "   This means port is not accessible from host"
fi
echo ""

echo "6. Testing remote connection (from your machine)..."
echo "   Run this from your local machine:"
echo "   curl -v http://72.61.233.209:8083/connector-plugins"
echo ""

echo "7. Checking firewall/network..."
echo "   If localhost works but remote doesn't:"
echo "   - Check firewall rules: sudo ufw status"
echo "   - Check if port 8083 is open: sudo netstat -tuln | grep 8083"
echo "   - Check Docker network configuration"
echo ""

echo "8. Container logs (last 20 lines)..."
docker logs $CONTAINER | tail -20
echo ""

echo "================================================================================
📋 SUMMARY
================================================================================
"
echo "Container: $CONTAINER"
echo "Local URL: $KAFKA_CONNECT_URL"
echo "Remote URL: $REMOTE_URL"
echo ""
echo "If localhost works but remote doesn't:"
echo "1. Check firewall: sudo ufw allow 8083/tcp"
echo "2. Check Docker port mapping"
echo "3. Check if Kafka Connect binds to 0.0.0.0 (not just 127.0.0.1)"
echo ""



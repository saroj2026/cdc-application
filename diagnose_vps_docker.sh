#!/bin/bash
# Diagnostic script to run on VPS server to check Docker containers and network configuration

echo "=========================================="
echo "VPS DOCKER DIAGNOSIS FOR KAFKA CONNECT"
echo "=========================================="
echo ""

echo "=== 1. DOCKER CONTAINERS ==="
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== 2. KAFKA CONNECT CONTAINER INFO ==="
KAFKA_CONNECT_CONTAINER=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1)
if [ -z "$KAFKA_CONNECT_CONTAINER" ]; then
    KAFKA_CONNECT_CONTAINER=$(docker ps --filter "name=connect" --format "{{.Names}}" | head -1)
fi

if [ -n "$KAFKA_CONNECT_CONTAINER" ]; then
    echo "Found Kafka Connect container: $KAFKA_CONNECT_CONTAINER"
    echo ""
    
    echo "--- Environment Variables (Kafka/Bootstrap related) ---"
    docker exec $KAFKA_CONNECT_CONTAINER env | grep -iE "KAFKA|BOOTSTRAP|CONNECT" | sort
    echo ""
    
    echo "--- Network Configuration ---"
    docker inspect $KAFKA_CONNECT_CONTAINER --format 'Network: {{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}'
    echo ""
    
    echo "--- IP Address ---"
    docker inspect $KAFKA_CONNECT_CONTAINER --format 'IP: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
    echo ""
else
    echo "ERROR: Kafka Connect container not found!"
    exit 1
fi

echo ""
echo "=== 3. KAFKA CONTAINER INFO ==="
KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.Names}}" | grep -v connect | head -1)
if [ -z "$KAFKA_CONTAINER" ]; then
    KAFKA_CONTAINER=$(docker ps --filter "name=kafka-cdc" --format "{{.Names}}" | head -1)
fi

if [ -n "$KAFKA_CONTAINER" ]; then
    echo "Found Kafka container: $KAFKA_CONTAINER"
    echo ""
    
    echo "--- Container Name (hostname) ---"
    docker inspect $KAFKA_CONTAINER --format 'Name: {{.Name}}'
    echo ""
    
    echo "--- IP Address ---"
    docker inspect $KAFKA_CONTAINER --format 'IP: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
    echo ""
    
    echo "--- Network ---"
    docker inspect $KAFKA_CONTAINER --format 'Network: {{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}'
    echo ""
else
    echo "WARNING: Kafka container not found!"
fi

echo ""
echo "=== 4. NETWORK CONNECTIVITY TEST ==="
if [ -n "$KAFKA_CONNECT_CONTAINER" ] && [ -n "$KAFKA_CONTAINER" ]; then
    echo "Testing if Kafka Connect can resolve 'kafka' hostname:"
    docker exec $KAFKA_CONNECT_CONTAINER getent hosts kafka 2>&1 || docker exec $KAFKA_CONNECT_CONTAINER nslookup kafka 2>&1 | head -5
    echo ""
    
    echo "Testing connectivity to kafka:29092:"
    docker exec $KAFKA_CONNECT_CONTAINER timeout 3 bash -c 'cat < /dev/null > /dev/tcp/kafka/29092' 2>&1 && echo "SUCCESS: Can connect to kafka:29092" || echo "FAILED: Cannot connect to kafka:29092"
    echo ""
    
    # Try with actual Kafka container name
    KAFKA_HOSTNAME=$(docker inspect $KAFKA_CONTAINER --format '{{.Name}}' | sed 's/\///')
    echo "Testing connectivity to $KAFKA_HOSTNAME:29092:"
    docker exec $KAFKA_CONNECT_CONTAINER timeout 3 bash -c "cat < /dev/null > /dev/tcp/$KAFKA_HOSTNAME/29092" 2>&1 && echo "SUCCESS: Can connect to $KAFKA_HOSTNAME:29092" || echo "FAILED: Cannot connect to $KAFKA_HOSTNAME:29092"
    echo ""
fi

echo ""
echo "=== 5. DOCKER NETWORKS ==="
echo "All Docker networks:"
docker network ls
echo ""

if [ -n "$KAFKA_CONNECT_CONTAINER" ]; then
    NETWORK_NAME=$(docker inspect $KAFKA_CONNECT_CONTAINER --format '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}')
    if [ -n "$NETWORK_NAME" ]; then
        echo "Inspecting network: $NETWORK_NAME"
        docker network inspect $NETWORK_NAME --format '{{range .Containers}}{{.Name}} ({{.IPv4Address}}){{"\n"}}{{end}}' 2>/dev/null
    fi
fi

echo ""
echo "=== 6. KAFKA CONNECT WORKER CONFIG ==="
curl -s http://localhost:8083/ 2>/dev/null | head -5
echo ""

echo ""
echo "=== 7. ORACLE CONNECTOR STATUS ==="
curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status 2>/dev/null | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status
echo ""

echo ""
echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="


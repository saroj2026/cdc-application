#!/bin/bash
# Quick check - just docker ps and key info

echo "=== DOCKER CONTAINERS ==="
docker ps

echo ""
echo "=== KAFKA CONNECT ENV (BOOTSTRAP) ==="
KAFKA_CONNECT=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1)
if [ -z "$KAFKA_CONNECT" ]; then
    KAFKA_CONNECT=$(docker ps --filter "name=connect" --format "{{.Names}}" | head -1)
fi
if [ -n "$KAFKA_CONNECT" ]; then
    docker exec $KAFKA_CONNECT env | grep -iE "BOOTSTRAP|KAFKA" | grep -iE "CONNECT|BOOTSTRAP"
fi

echo ""
echo "=== KAFKA CONTAINER NAME ==="
KAFKA=$(docker ps --filter "name=kafka" --format "{{.Names}}" | grep -v connect | head -1)
if [ -n "$KAFKA" ]; then
    echo "Kafka container: $KAFKA"
    docker inspect $KAFKA --format 'Hostname/Name: {{.Name}}'
fi


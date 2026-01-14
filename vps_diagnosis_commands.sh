#!/bin/bash
# Diagnostic commands to run on VPS server to check Kafka Connect and Kafka connectivity

echo "=== DOCKER CONTAINERS ==="
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== KAFKA CONNECT CONTAINER NETWORK ==="
KAFKA_CONNECT_CONTAINER=$(docker ps --filter "name=kafka-connect" --format "{{.Names}}" | head -1)
if [ -n "$KAFKA_CONNECT_CONTAINER" ]; then
    echo "Kafka Connect container: $KAFKA_CONNECT_CONTAINER"
    echo -e "\nKafka Connect network:"
    docker inspect $KAFKA_CONNECT_CONTAINER --format '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}'
    
    echo -e "\nKafka Connect environment variables:"
    docker exec $KAFKA_CONNECT_CONTAINER env | grep -i kafka | grep -i bootstrap
    
    echo -e "\n=== HOSTNAME RESOLUTION FROM KAFKA CONNECT ==="
    echo "Testing if 'kafka' hostname resolves:"
    docker exec $KAFKA_CONNECT_CONTAINER nslookup kafka || docker exec $KAFKA_CONNECT_CONTAINER ping -c 1 kafka 2>&1 | head -3
    
    echo -e "\n=== KAFKA CONTAINER INFO ==="
    KAFKA_CONTAINER=$(docker ps --filter "name=kafka" --format "{{.Names}}" | grep -v connect | head -1)
    if [ -n "$KAFKA_CONTAINER" ]; then
        echo "Kafka container: $KAFKA_CONTAINER"
        echo "Kafka IP address:"
        docker inspect $KAFKA_CONTAINER --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
        
        echo -e "\n=== NETWORK CONNECTIVITY TEST ==="
        echo "Testing connectivity from Kafka Connect to Kafka:"
        docker exec $KAFKA_CONNECT_CONTAINER nc -zv kafka 29092 2>&1 || docker exec $KAFKA_CONNECT_CONTAINER telnet kafka 29092 2>&1 | head -3
    fi
else
    echo "Kafka Connect container not found!"
fi

echo -e "\n=== DOCKER NETWORKS ==="
docker network ls
echo -e "\nInspecting Docker networks:"
docker network inspect $(docker ps --filter "name=kafka-connect" --format '{{range $net, $conf := .NetworkSettings.Networks}}{{$net}}{{end}}' | head -1) 2>/dev/null | grep -A 5 "Containers"

echo -e "\n=== KAFKA CONNECT WORKER CONFIG (if accessible) ==="
curl -s http://localhost:8083/ 2>/dev/null | head -10

echo -e "\n=== CONNECTOR STATUS ==="
curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status 2>/dev/null | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8083/connectors/cdc-oracle_sf_p-ora-cdc_user/status


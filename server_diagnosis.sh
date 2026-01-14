#!/bin/bash
# Server-side diagnosis script for Kafka Connect consumer group issue

echo "======================================================================"
echo "Kafka Connect Diagnosis - Consumer Group DEAD Issue"
echo "======================================================================"

# 1. Check Docker containers
echo ""
echo "1. Checking Docker containers..."
docker ps | grep -i connect

# 2. Get Kafka Connect container ID
CONTAINER_ID=$(docker ps | grep -i connect | awk '{print $1}' | head -1)
if [ -z "$CONTAINER_ID" ]; then
    echo "   ERROR: No Kafka Connect container found!"
    exit 1
fi

echo ""
echo "   Kafka Connect Container ID: $CONTAINER_ID"

# 3. Check recent logs for sink connector
echo ""
echo "2. Checking recent logs for sink-ps_sn_p-snowflake-public..."
docker logs $CONTAINER_ID --tail 200 | grep -i "sink-ps_sn_p-snowflake-public\|consumer\|error\|exception\|failed" | tail -50

# 4. Check consumer group status
echo ""
echo "3. Checking consumer group status..."
# Try to find kafka-consumer-groups script
KAFKA_BIN=$(find /opt /usr -name "kafka-consumer-groups.sh" 2>/dev/null | head -1)
if [ -n "$KAFKA_BIN" ]; then
    $KAFKA_BIN --bootstrap-server localhost:9092 --group connect-sink-ps_sn_p-snowflake-public --describe 2>/dev/null || \
    $KAFKA_BIN --bootstrap-server 72.61.233.209:9092 --group connect-sink-ps_sn_p-snowflake-public --describe 2>/dev/null || \
    echo "   Could not connect to Kafka broker to check consumer group"
else
    echo "   kafka-consumer-groups.sh not found in standard locations"
fi

# 5. Check connector status via API
echo ""
echo "4. Checking connector status via API..."
curl -s http://localhost:8083/connectors/sink-ps_sn_p-snowflake-public/status | python3 -m json.tool 2>/dev/null || \
curl -s http://localhost:8083/connectors/sink-ps_sn_p-snowflake-public/status

# 6. Check connector config
echo ""
echo "5. Checking connector configuration..."
curl -s http://localhost:8083/connectors/sink-ps_sn_p-snowflake-public/config | python3 -m json.tool 2>/dev/null | grep -E "topics|transforms|consumer.group" || \
curl -s http://localhost:8083/connectors/sink-ps_sn_p-snowflake-public/config | grep -E "topics|transforms|consumer.group"

# 7. Check for task errors
echo ""
echo "6. Checking for task errors in logs..."
docker logs $CONTAINER_ID --tail 500 | grep -A 10 -B 5 "sink-ps_sn_p-snowflake-public.*ERROR\|sink-ps_sn_p-snowflake-public.*Exception\|sink-ps_sn_p-snowflake-public.*Failed" | tail -30

# 8. Check worker configuration
echo ""
echo "7. Checking worker configuration..."
docker exec $CONTAINER_ID cat /kafka/config/connect-distributed.properties 2>/dev/null | grep -E "bootstrap.servers|group.id|tasks.max" || \
echo "   Could not read worker config file"

# 9. Check if topic exists and has messages
echo ""
echo "8. Checking if topic has messages..."
KAFKA_BIN_DIR=$(dirname $KAFKA_BIN 2>/dev/null)
if [ -n "$KAFKA_BIN_DIR" ]; then
    $KAFKA_BIN_DIR/kafka-run-class.sh kafka.tools.GetOffsetShell \
        --broker-list localhost:9092 \
        --topic ps_sn_p.public.projects_simple \
        --time -1 2>/dev/null || \
    echo "   Could not check topic offsets"
else
    echo "   Kafka tools not found"
fi

# 10. Check connector task state transitions
echo ""
echo "9. Checking connector task state in logs..."
docker logs $CONTAINER_ID --tail 1000 | grep -i "sink-ps_sn_p-snowflake-public" | grep -E "state|transition|assigned|running" | tail -20

echo ""
echo "======================================================================"
echo "Diagnosis Complete"
echo "======================================================================"


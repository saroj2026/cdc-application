#!/bin/bash
# Detailed log checking

CONTAINER_ID="28b9a11e27bb"
CONNECTOR="sink-ps_sn_p-snowflake-public"

echo "=== Recent connector activity ==="
docker logs $CONTAINER_ID --tail 100 | grep -i "$CONNECTOR" | tail -20

echo ""
echo "=== Errors ==="
docker logs $CONTAINER_ID --tail 200 | grep -i "error\|exception" | grep -i "$CONNECTOR" | tail -15

echo ""
echo "=== Task status ==="
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/status | grep -o '"state":"[^"]*"' | head -5

echo ""
echo "=== Consumer activity ==="
docker logs $CONTAINER_ID --tail 200 | grep -i "consumer\|partition\|offset" | grep -i "$CONNECTOR" | tail -10


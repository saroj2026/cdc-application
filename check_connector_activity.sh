#!/bin/bash
# Check detailed connector activity

CONTAINER_ID="28b9a11e27bb"
CONNECTOR="sink-ps_sn_p-snowflake-public"

echo "=== Checking connector task activity ==="
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | grep -E "consumed|committed|offset|insert|write|snowflake" | tail -20

echo ""
echo "=== Checking for any errors ==="
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | grep -i "error\|exception\|failed" | tail -15

echo ""
echo "=== Checking connector status ==="
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/status | python3 -m json.tool 2>/dev/null | grep -A 5 "state\|trace"

echo ""
echo "=== Recent connector logs ==="
docker logs $CONTAINER_ID --tail 100 | grep -i "$CONNECTOR" | tail -10


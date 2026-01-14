#!/bin/bash
# Run this script directly on the server to check connector status

CONTAINER_ID="28b9a11e27bb"
CONNECTOR="sink-ps_sn_p-snowflake-public"

echo "======================================================================"
echo "Snowflake Connector Diagnosis"
echo "======================================================================"

echo ""
echo "1. Connector Status:"
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/status | python3 -m json.tool 2>/dev/null || \
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/status

echo ""
echo "2. Recent Connector Logs (last 50 lines):"
docker logs $CONTAINER_ID --tail 200 | grep -i "$CONNECTOR" | tail -50

echo ""
echo "3. Errors in Logs:"
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | grep -i "error\|exception\|failed" | tail -20

echo ""
echo "4. Consumer Activity:"
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | grep -i "consumer\|partition\|offset\|consumed\|committed" | tail -15

echo ""
echo "5. Snowflake Connection Activity:"
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | grep -i "snowflake\|SFSession\|insert\|table\|write" | tail -15

echo ""
echo "6. Connector Configuration:"
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/config | python3 -m json.tool 2>/dev/null | grep -E "value.converter|transforms|topics|consumer.group" || \
docker exec $CONTAINER_ID curl -s http://localhost:8083/connectors/$CONNECTOR/config | grep -E "value.converter|transforms|topics"

echo ""
echo "======================================================================"


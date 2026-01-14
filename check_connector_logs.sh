#!/bin/bash
# Check detailed connector logs

CONTAINER_ID="28b9a11e27bb"
CONNECTOR="sink-ps_sn_p-snowflake-public"

echo "Checking connector logs for processing activity..."
docker logs $CONTAINER_ID --tail 500 | grep -i "$CONNECTOR" | tail -30

echo ""
echo "Checking for any errors or exceptions..."
docker logs $CONTAINER_ID --tail 500 | grep -i "error\|exception\|failed" | grep -i "$CONNECTOR" | tail -20

echo ""
echo "Checking for message processing..."
docker logs $CONTAINER_ID --tail 500 | grep -i "consumed\|committed\|offset\|record" | grep -i "$CONNECTOR" | tail -20

echo ""
echo "Checking Snowflake connection activity..."
docker logs $CONTAINER_ID --tail 500 | grep -i "snowflake\|SFSession\|insert\|table" | tail -20


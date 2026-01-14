#!/bin/bash
# Update connector to use Debezium unwrap transform

CONTAINER_ID="28b9a11e27bb"
CONNECTOR="sink-ps_sn_p-snowflake-public"
API="http://localhost:8083"

echo "Getting current config..."
CONFIG=$(docker exec $CONTAINER_ID curl -s $API/connectors/$CONNECTOR/config)

echo "Updating config with Debezium unwrap transform..."
# Use jq if available, or python
if command -v jq &> /dev/null; then
    UPDATED_CONFIG=$(echo "$CONFIG" | jq '. + {
        "transforms": "unwrap",
        "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
        "transforms.unwrap.drop.tombstones": "false",
        "transforms.unwrap.delete.handling.mode": "none"
    }')
else
    # Use python
    UPDATED_CONFIG=$(echo "$CONFIG" | python3 -c "
import sys, json
config = json.load(sys.stdin)
config['transforms'] = 'unwrap'
config['transforms.unwrap.type'] = 'io.debezium.transforms.ExtractNewRecordState'
config['transforms.unwrap.drop.tombstones'] = 'false'
config['transforms.unwrap.delete.handling.mode'] = 'none'
# Remove old transform configs
for key in list(config.keys()):
    if key.startswith('transforms.extract'):
        del config[key]
print(json.dumps(config))
")
fi

echo "Updating connector..."
docker exec $CONTAINER_ID curl -s -X PUT \
    -H "Content-Type: application/json" \
    -d "$UPDATED_CONFIG" \
    $API/connectors/$CONNECTOR/config

echo ""
echo "Restarting connector..."
docker exec $CONTAINER_ID curl -s -X POST $API/connectors/$CONNECTOR/restart

echo ""
echo "Done! Using Debezium unwrap transform."


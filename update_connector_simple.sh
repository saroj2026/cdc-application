#!/bin/bash
# Simple script to update connector - run this on the VPS

CONNECTOR="sink-as400-s3_p-s3-dbo"
ACCESS_KEY="AKIATLTXNANW2EV7QGV2"
SECRET_KEY="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"

echo "Updating connector: $CONNECTOR"

# Get config, update, and apply
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR/config | \
python3 -c "
import sys, json
config = json.load(sys.stdin)
config['aws.access.key.id'] = '$ACCESS_KEY'
config['aws.secret.access.key'] = '$SECRET_KEY'
print(json.dumps(config))
" | \
docker exec -i kafka-connect-cdc curl -s -X PUT \
  -H 'Content-Type: application/json' \
  -d @- \
  http://localhost:8083/connectors/$CONNECTOR/config

echo ""
echo "Restarting connector..."
docker exec kafka-connect-cdc curl -s -X POST http://localhost:8083/connectors/$CONNECTOR/restart

echo ""
echo "Waiting 30 seconds..."
sleep 30

echo ""
echo "Checking status:"
docker exec kafka-connect-cdc curl -s http://localhost:8083/connectors/$CONNECTOR/status | python3 -m json.tool



